import os
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import base64

from app.providers import ImageProviderFactory, DiagramProviderFactory, VideoProviderFactory
from app.config import settings
from app.logger import configure_logging, get_logger
from app.middleware import RequestIDMiddleware, RequestLoggerMiddleware
from app.middleware_slo import SLOTrackingMiddleware
from app.middleware_timeout import TimeoutMiddleware
from app.tracing import init_tracing
from app.graceful_shutdown import lifespan
from app.cost_tracking import cost_tracker, estimate_request_cost
from app.caching import get_cache_manager
from app.routing import select_provider, execute_with_fallback
from prometheus_fastapi_instrumentator import Instrumentator


load_dotenv()

# Configure structured logging
env = os.getenv("ENV", "development")
log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"
log_dir = os.getenv("LOG_DIR", "logs")
configure_logging(env=env, log_to_file=log_to_file, log_dir=log_dir)

logger = get_logger()
logger.info("Creative service initialized", env=env)

# Initialize OpenTelemetry tracing
try:
    init_tracing(
        service_name="creative-service",
        service_version="0.1.0",
        environment=env,
    )
    logger.info("Tracing initialized")
except Exception as e:
    logger.warn("Failed to initialize tracing", error=str(e))

app = FastAPI(
    title="Woragis Creative Service", 
    version="0.1.0", 
    description="AI-powered image, diagram, and video generation for technical content",
    lifespan=lifespan
)

# Add middleware for request ID, logging, SLO tracking, and timeouts
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(SLOTrackingMiddleware)
app.add_middleware(TimeoutMiddleware)

# Add Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)

if settings.CORS_ENABLED:
    origins = settings.CORS_ALLOWED_ORIGINS.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ============ Request/Response Models ============

class ImageGenerationRequest(BaseModel):
    provider: Literal["openai", "stable-diffusion", "cipher"] = Field("openai", description="Image generation provider")
    prompt: str = Field(..., description="Image generation prompt")
    size: Optional[str] = Field(None, description="Image size (e.g., '1024x1024')")
    style: Optional[Literal["technical", "diagram", "thumbnail", "illustration"]] = Field("technical", description="Image style")
    context: Optional[str] = Field(None, description="Additional context for the image")
    n: Optional[int] = Field(1, description="Number of images to generate")


class ImageData(BaseModel):
    url: Optional[str] = None
    b64_json: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    data: list[ImageData]
    provider: str
    prompt: str


class DiagramGenerationRequest(BaseModel):
    description: str = Field(..., description="Description of the diagram to generate")
    diagram_type: Literal["mermaid", "graphviz"] = Field("mermaid", description="Type of diagram code to generate")
    diagram_kind: Optional[str] = Field("flowchart", description="Kind of diagram (flowchart, sequence, er, etc.)")
    output_format: Literal["png", "svg", "pdf"] = Field("png", description="Output format")
    ai_provider: Literal["openai", "anthropic"] = Field("openai", description="AI provider for code generation")


class DiagramGenerationResponse(BaseModel):
    b64_json: str
    code: str
    format: str
    diagram_type: str


class VideoGenerationRequest(BaseModel):
    image_url: Optional[str] = Field(None, description="URL of the input image")
    image_b64: Optional[str] = Field(None, description="Base64 encoded input image")
    motion_bucket_id: Optional[int] = Field(127, description="Motion intensity (1-255)")
    num_frames: Optional[int] = Field(25, description="Number of frames (14-25)")
    provider: Literal["replicate", "runway"] = Field("replicate", description="Video generation provider")


class VideoGenerationResponse(BaseModel):
    video_url: Optional[str] = None
    video_b64: Optional[str] = None
    format: str


# ============ Endpoints ============

@app.get("/healthz")
def healthz():
    """
    Health check endpoint.
    Returns service availability and dependency status.
    """
    from app.health import check_health
    result = check_health()
    
    # Determine HTTP status code
    status_code = 200
    if result["status"] == "unhealthy":
        status_code = 503
    
    return JSONResponse(content=result, status_code=status_code)


@app.post("/v1/images/generate", response_model=ImageGenerationResponse)
async def generate_images(req: ImageGenerationRequest):
    """Generate images using various AI providers."""
    logger.info("Image generation request", provider=req.provider, style=req.style)
    
    # Check cache
    cache_manager = get_cache_manager()
    cache_key = f"image:{req.provider}:{req.prompt}:{req.style}:{req.size or 'default'}"
    cached_response = cache_manager.get(cache_key)
    
    if cached_response is not None:
        logger.info("Cache hit for image generation", provider=req.provider)
        return cached_response
    
    try:
        # Select provider using routing policies
        selected_provider, fallback_chain = select_provider(
            requested_provider=req.provider,
            cost_mode="balanced"
        )
        
        # Track cost
        estimated_cost = estimate_request_cost(selected_provider, "/v1/images/generate")
        cost_tracker.record_api_call(selected_provider, "default")
        
        async def generate_with_provider(provider_name: str):
            provider = ImageProviderFactory.create(provider_name)
            
            # Use enhanced prompt for OpenAI if style is provided
            if provider_name == "openai" and req.style:
                return await provider.generate_with_enhanced_prompt(
                    base_prompt=req.prompt,
                    style=req.style,
                    context=req.context,
                    size=req.size,
                    n=req.n,
                )
            elif provider_name == "stable-diffusion":
                # Use technical diagram generation for stable diffusion if context suggests it
                if req.context and ("architecture" in req.context.lower() or "microservice" in req.context.lower() or "diagram" in req.prompt.lower()):
                    return await provider.generate_technical_diagram(
                        description=req.prompt,
                        diagram_type="architecture" if "architecture" in req.context.lower() else "flowchart",
                    )
                else:
                    return await provider.generate(prompt=req.prompt, **({"width": 1024, "height": 1024} if req.size else {}))
            else:
                return await provider.generate(
                    prompt=req.prompt,
                    size=req.size,
                    n=req.n,
                )
        
        # Execute with fallback chain
        results = await execute_with_fallback(
            provider=selected_provider,
            fallback_chain=fallback_chain,
            execution_function=generate_with_provider,
            endpoint="/v1/images/generate"
        )
        
        # Normalize to ImageData format
        normalized = []
        for item in results:
            normalized.append(ImageData(url=item.get("url"), b64_json=item.get("b64_json")))
        
        # Track cost
        cost_tracker.record_request("/v1/images/generate", selected_provider, estimated_cost)
        
        response = ImageGenerationResponse(
            data=normalized,
            provider=selected_provider,
            prompt=req.prompt,
        )
        
        # Store in cache
        cache_manager.set(cache_key, response, "/v1/images/generate")
        
        return response
    except Exception as e:
        logger.exception("Image generation error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/images/generate/thumbnail")
async def generate_thumbnail(req: ImageGenerationRequest):
    """Generate a thumbnail optimized for social media posts."""
    # Override style to thumbnail
    req.style = "thumbnail"
    return await generate_images(req)


@app.post("/v1/diagrams/generate", response_model=DiagramGenerationResponse)
async def generate_diagram(req: DiagramGenerationRequest):
    """Generate technical diagrams using AI-generated code (Mermaid/Graphviz)."""
    logger.info("Diagram generation request", diagram_type=req.diagram_type, diagram_kind=req.diagram_kind)
    
    try:
        generator = DiagramProviderFactory.create(req.ai_provider)
        result = await generator.generate(
            description=req.description,
            diagram_type=req.diagram_type,
            diagram_kind=req.diagram_kind,
            output_format=req.output_format,
        )
        
        return DiagramGenerationResponse(
            b64_json=result["b64_json"],
            code=result["code"],
            format=result["format"],
            diagram_type=req.diagram_type,
        )
    except Exception as e:
        logger.exception("Diagram generation error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/diagrams/mermaid", response_model=DiagramGenerationResponse)
async def generate_mermaid_diagram(
    description: str,
    diagram_kind: str = "flowchart",
    output_format: Literal["png", "svg"] = "png",
    ai_provider: Literal["openai", "anthropic"] = "openai",
):
    """Generate a Mermaid diagram from description."""
    req = DiagramGenerationRequest(
        description=description,
        diagram_type="mermaid",
        diagram_kind=diagram_kind,
        output_format=output_format,
        ai_provider=ai_provider,
    )
    return await generate_diagram(req)


@app.post("/v1/videos/generate", response_model=VideoGenerationResponse)
async def generate_video(req: VideoGenerationRequest):
    """Generate a video/GIF from an image using AI."""
    logger.info("Video generation request", provider=req.provider)
    
    if not req.image_url and not req.image_b64:
        raise HTTPException(status_code=400, detail="Either image_url or image_b64 must be provided")
    
    try:
        generator = VideoProviderFactory.create(req.provider)
        result = await generator.generate_from_image(
            image_url=req.image_url,
            image_b64=req.image_b64,
            motion_bucket_id=req.motion_bucket_id,
            num_frames=req.num_frames,
        )
        
        return VideoGenerationResponse(
            video_url=result.get("video_url"),
            video_b64=result.get("video_b64"),
            format=result.get("format", "mp4"),
        )
    except Exception as e:
        logger.exception("Video generation error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/videos/animate")
async def animate_image(req: VideoGenerationRequest):
    """Create an animated GIF/video from a static image."""
    return await generate_video(req)


# ============ Utility Endpoints ============

@app.get("/v1/providers/images")
def list_image_providers():
    """List available image generation providers."""
    return {
        "providers": ["openai", "stable-diffusion", "cipher"],
        "descriptions": {
            "openai": "DALL-E 3 - Best for high-quality thumbnails and illustrations",
            "stable-diffusion": "Stable Diffusion XL - Good for artistic and diagram-style images",
            "cipher": "Cipher/NoFilterGPT - Alternative provider",
        }
    }


@app.post("/v1/routing/reload")
def reload_routing_policies():
    """Reload routing policies (hot reload)."""
    from app.routing.policy import get_routing_policy_loader
    policy_loader = get_routing_policy_loader()
    policy_loader.reload()
    logger.info("Routing policies reloaded")
    return {"status": "success", "message": "Routing policies reloaded"}


@app.get("/v1/providers/diagrams")
def list_diagram_providers():
    """List available diagram generation providers."""
    return {
        "providers": ["mermaid", "graphviz"],
        "ai_providers": ["openai", "anthropic"],
        "descriptions": {
            "mermaid": "Mermaid diagrams - Flowcharts, sequence diagrams, ER diagrams, etc.",
            "graphviz": "Graphviz DOT - Network graphs, dependency graphs, etc.",
        }
    }


@app.get("/v1/providers/videos")
def list_video_providers():
    """List available video generation providers."""
    return {
        "providers": ["replicate", "runway"],
        "descriptions": {
            "replicate": "Stable Video Diffusion - Generate videos from images",
            "runway": "Runway Gen-2 - Advanced video generation (coming soon)",
        }
    }

