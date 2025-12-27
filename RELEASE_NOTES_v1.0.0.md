# Creative Service v1.0.0

## Overview

The Creative Service is a production-ready FastAPI-based service that provides AI-powered image, diagram, and video generation capabilities specifically designed for technical blog content. This initial stable release features multi-provider support, intelligent prompt enhancement, technical diagram generation, and comprehensive observability.

## Key Features

### Core Functionality
- **Multi-Provider Image Generation**: Unified interface for DALL-E 3 (OpenAI), Stable Diffusion XL (Replicate), and Cipher (NoFilterGPT)
- **Intelligent Prompt Enhancement**: Automatic prompt optimization for technical content (architecture diagrams, thumbnails, illustrations)
- **AI-Powered Diagram Generation**: Generate technical diagrams from natural language descriptions using Mermaid and Graphviz
- **Video/GIF Generation**: Animate static images into videos using Stable Video Diffusion
- **Thumbnail Optimization**: Specialized endpoint for social media thumbnail generation

### Image Generation Features
- **Style-Based Generation**: Support for technical, diagram, thumbnail, and illustration styles
- **Context-Aware Prompts**: Automatic prompt enhancement based on context and style
- **Technical Diagram Mode**: Specialized generation for architecture and microservices diagrams
- **Multiple Formats**: PNG, JPEG, WebP support
- **Size Flexibility**: Configurable image dimensions

### Diagram Generation Features
- **Mermaid Diagrams**: Flowcharts, sequence diagrams, ER diagrams, state diagrams
- **Graphviz Diagrams**: Network graphs, dependency graphs, organizational charts
- **AI Code Generation**: Use OpenAI or Anthropic to generate diagram code from descriptions
- **Multiple Output Formats**: PNG, SVG, PDF rendering
- **Online & Local Rendering**: Mermaid.ink API or local mermaid-cli support

### Video Generation Features
- **Image-to-Video**: Animate static images into MP4 videos
- **Motion Control**: Configurable motion intensity (motion_bucket_id: 1-255)
- **Frame Control**: Adjustable number of frames (14-25)
- **Stable Video Diffusion**: Powered by Replicate's Stable Video Diffusion model

### Production Features
- **FastAPI Framework**: Modern async Python web framework with automatic API documentation
- **Health Check Endpoint**: HTTP endpoint at `/healthz` for Kubernetes liveness/readiness probes
- **Prometheus Metrics**: Comprehensive metrics exposed at `/metrics` endpoint via prometheus-fastapi-instrumentator
- **Structured Logging**: JSON logging in production, text logging in development with structlog
- **OpenTelemetry Tracing**: Distributed tracing support with OTLP exporter (Jaeger compatible)
- **Request ID Middleware**: Automatic trace ID generation and propagation via `X-Trace-ID` headers
- **HTTP Request Logging**: Automatic structured logging of all HTTP requests with duration, status, and context

### Configuration & Flexibility
- **Environment-based Configuration**: All settings via environment variables
- **CORS Support**: Configurable CORS for cross-origin requests
- **Provider Factory Pattern**: Easy to add new providers
- **Flexible Sizing**: Per-request size overrides
- **Quality Options**: HD and standard quality for DALL-E

### Code Quality
- **Comprehensive Testing**: Unit tests and integration tests included
- **Test Coverage**: Coverage reporting with pytest-cov
- **Type Hints**: Full type annotation support
- **Clean Architecture**: Separation of concerns with providers, factories, and middleware
- **Async/Await**: Full async support for high concurrency

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       │
┌──────▼──────────────────┐
│   FastAPI Application   │
│                         │
│  ┌──────────────────┐   │
│  │  Middleware      │   │
│  │  - Request ID    │   │
│  │  - Logging       │   │
│  │  - Tracing       │   │
│  └────────┬─────────┘   │
│           │            │
│  ┌────────▼─────────┐   │
│  │ Provider Factory │   │
│  └────────┬─────────┘   │
└───────────┼─────────────┘
            │
    ┌───────┴────────┐
    │                │
┌───▼────┐      ┌───▼─────┐
│ Images │      │Diagrams │
│ Factory│      │Factory  │
└───┬────┘      └───┬─────┘
    │               │
┌───▼────┐      ┌───▼─────┐
│ Videos │      │  ...    │
│ Factory│      │         │
└────────┘      └─────────┘
```

## Dependencies

### Core Framework
- **fastapi**: Modern async web framework
- **uvicorn**: ASGI server with standard extras
- **pydantic**: Data validation and settings management

### Image Generation
- **openai**: OpenAI Python SDK for DALL-E 3
- **replicate**: Replicate API client for Stable Diffusion
- **httpx**: Async HTTP client for Cipher provider
- **Pillow**: Image processing and manipulation

### Diagram Generation
- **openai**: For generating diagram code
- **anthropic**: Alternative AI provider for code generation
- **graphviz**: Graphviz Python bindings and rendering
- **mermaid.ink API**: Online Mermaid rendering (fallback to local mermaid-cli)

### Video Generation
- **replicate**: Stable Video Diffusion API
- **httpx**: HTTP client for video processing

### Observability
- **structlog**: Structured logging
- **prometheus-client**: Prometheus metrics
- **prometheus-fastapi-instrumentator**: FastAPI metrics auto-instrumentation
- **opentelemetry-api/sdk**: OpenTelemetry tracing
- **opentelemetry-exporter-otlp-proto-http**: OTLP HTTP exporter
- **opentelemetry-instrumentation-fastapi**: FastAPI auto-instrumentation

### Development & Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking support
- **python-dotenv**: Environment variable management

## API Endpoints

### Image Generation

#### POST `/v1/images/generate`
Generate images using various AI providers.

**Request:**
```json
{
  "provider": "openai",
  "prompt": "Microservices architecture with connecting gears",
  "style": "technical",
  "context": "Software architecture for a distributed system",
  "size": "1024x1024",
  "n": 1
}
```

**Response:**
```json
{
  "data": [
    {
      "b64_json": "base64_encoded_image",
      "url": null
    }
  ],
  "provider": "openai",
  "prompt": "..."
}
```

#### POST `/v1/images/generate/thumbnail`
Generate a thumbnail optimized for social media posts.

**Request:** Same as `/v1/images/generate` (style automatically set to "thumbnail")

### Diagram Generation

#### POST `/v1/diagrams/generate`
Generate technical diagrams from natural language descriptions.

**Request:**
```json
{
  "description": "A microservices architecture with an API gateway, three microservices (user, order, payment), and a Redis cache layer",
  "diagram_type": "mermaid",
  "diagram_kind": "flowchart",
  "output_format": "png",
  "ai_provider": "openai"
}
```

**Response:**
```json
{
  "b64_json": "base64_encoded_diagram_image",
  "code": "graph TD\n    A[API Gateway] --> B[User Service]\n    ...",
  "format": "png",
  "diagram_type": "mermaid"
}
```

#### POST `/v1/diagrams/mermaid`
Quick endpoint for Mermaid diagrams (simplified parameters).

**Request:**
```json
{
  "description": "Request flow through microservices",
  "diagram_kind": "sequence",
  "output_format": "png",
  "ai_provider": "openai"
}
```

### Video Generation

#### POST `/v1/videos/generate`
Animate a static image into a video.

**Request:**
```json
{
  "image_b64": "base64_encoded_image",
  "motion_bucket_id": 127,
  "num_frames": 25,
  "provider": "replicate"
}
```

**Response:**
```json
{
  "video_url": "https://...",
  "video_b64": "base64_encoded_video",
  "format": "mp4"
}
```

#### POST `/v1/videos/animate`
Alias for `/v1/videos/generate` (semantic naming).

### Utility Endpoints

#### GET `/v1/providers/images`
List available image generation providers and descriptions.

#### GET `/v1/providers/diagrams`
List available diagram generation providers and AI providers.

#### GET `/v1/providers/videos`
List available video generation providers and descriptions.

#### GET `/healthz`
Health check endpoint for Kubernetes probes.

**Response:**
```json
{
  "status": "healthy",
  "checks": [
    {
      "name": "service",
      "status": "ok"
    }
  ]
}
```

#### GET `/metrics`
Prometheus metrics endpoint (auto-instrumented).

## Configuration Variables

### Core Configuration
- `ENV`: Environment mode - "development" or "production" (affects logging)
- `CORS_ENABLED`: Enable CORS (default: true)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins (default: "*")
- `DEFAULT_IMAGE_FORMAT`: Default image format (default: "png")
- `DEFAULT_DIAGRAM_FORMAT`: Default diagram format (default: "png")

### OpenAI Configuration (DALL-E & Diagram Code)
- `OPENAI_API_KEY`: OpenAI API key (required for "openai" provider)
- `DALL_E_MODEL`: DALL-E model (default: "dall-e-3")
- `DALL_E_QUALITY`: Quality setting (default: "standard", options: "standard", "hd")
- `DALL_E_SIZE`: Default DALL-E size (default: "1024x1024", options: "1024x1024", "1792x1024", "1024x1792")
- `OPENAI_MODEL`: Model for diagram code generation (default: "gpt-4o-mini")

### Stable Diffusion Configuration (via Replicate)
- `REPLICATE_API_KEY`: Replicate API key (required for "stable-diffusion" provider)
- `STABLE_DIFFUSION_MODEL`: Stable Diffusion model ID (default: "stability-ai/sdxl:...")

### Video Generation Configuration
- `REPLICATE_VIDEO_MODEL`: Stable Video Diffusion model ID (default: "stability-ai/stable-video-diffusion:...")
- `RUNWAY_API_KEY`: Runway API key (optional, for future Runway Gen-2 support)

### Cipher Configuration
- `CIPHER_API_KEY`: Cipher API key (required for "cipher" provider)
- `CIPHER_IMAGE_URL`: Cipher image generation URL (default: "https://api.nofiltergpt.com/v1/images/generations")
- `CIPHER_IMAGE_SIZE`: Default image size (default: "1024x1024")
- `CIPHER_IMAGE_N`: Default number of images (default: 1)

### Anthropic Configuration (Diagram Code)
- `ANTHROPIC_API_KEY`: Anthropic API key (required for "anthropic" ai_provider)
- `ANTHROPIC_MODEL`: Anthropic model for code generation (default: "claude-3-5-sonnet-latest")

### Observability Configuration
- `OTLP_ENDPOINT`: OpenTelemetry OTLP endpoint (default: "http://jaeger:4318")
- `LOG_TO_FILE`: Enable file logging in development (default: false)
- `LOG_DIR`: Directory for log files (default: "logs")

## Supported Providers

### Image Generation Providers
- **openai**: DALL-E 3 - Best for high-quality thumbnails and illustrations
- **stable-diffusion**: Stable Diffusion XL via Replicate - Good for artistic and diagram-style images
- **cipher**: Cipher/NoFilterGPT - Alternative provider

### Diagram Generation
- **mermaid**: Flowcharts, sequence diagrams, ER diagrams, state diagrams
- **graphviz**: Network graphs, dependency graphs, organizational charts
- **AI Providers**: OpenAI GPT-4o-mini or Anthropic Claude (for code generation)

### Video Generation Providers
- **replicate**: Stable Video Diffusion - Generate videos from images
- **runway**: Runway Gen-2 (coming soon)

## Use Cases

### 1. Blog Post Thumbnails
Generate eye-catching thumbnails optimized for social media platforms.

```bash
POST /v1/images/generate/thumbnail
{
  "provider": "openai",
  "prompt": "Kubernetes orchestration architecture",
  "style": "thumbnail"
}
```

### 2. Architecture Diagrams
Create clear, professional architecture diagrams from descriptions.

```bash
POST /v1/diagrams/generate
{
  "description": "Three-tier architecture: web server, application server, database",
  "diagram_type": "mermaid",
  "diagram_kind": "flowchart"
}
```

### 3. Technical Illustrations
Generate technical illustrations for blog posts.

```bash
POST /v1/images/generate
{
  "provider": "openai",
  "prompt": "Microservices communication patterns",
  "style": "technical",
  "context": "Blog post about distributed systems"
}
```

### 4. Workflow Diagrams
Visualize complex workflows and processes.

```bash
POST /v1/diagrams/mermaid
{
  "description": "User authentication flow with OAuth, JWT tokens, and session management",
  "diagram_kind": "sequence"
}
```

### 5. Animated Content
Transform static diagrams into engaging animations.

```bash
# First generate an image/diagram
POST /v1/images/generate/...
# Then animate it
POST /v1/videos/animate
{
  "image_b64": "...",
  "motion_bucket_id": 100
}
```

## Recommendations

### For Technical Blog Posts

1. **Thumbnails**: Use `openai` provider with `style: "thumbnail"`
   - Best quality and consistency
   - Optimized for social media platforms

2. **Architecture Diagrams**: 
   - Use `diagrams/generate` with `mermaid` for precise, editable diagrams
   - Use `stable-diffusion` with technical context for artistic flexibility

3. **Process Flows**: Use diagram generation with `mermaid` and `diagram_kind: "sequence"` or `"flowchart"`
   - Clean, professional, and easy to modify
   - Perfect for technical documentation

4. **Animations**: Generate a static image first, then use video generation to animate it
   - Great for demonstrating workflows or system interactions
   - Keep `motion_bucket_id` moderate (100-150) for professional content

## Observability

### Structured Logging
- **Production**: JSON format for log aggregation systems
- **Development**: Human-readable text format
- **Fields**: Automatic service name, trace ID, request context
- **Levels**: DEBUG (dev), INFO (prod) with automatic error logging

### Distributed Tracing
- **OpenTelemetry**: Full OTLP support with Jaeger compatibility
- **Auto-instrumentation**: FastAPI and HTTP requests automatically traced
- **Sampling**: 100% in development, 10% in production
- **Context Propagation**: Trace IDs via `X-Trace-ID` headers

### Metrics
- **HTTP Metrics**: Request count, duration, status codes
- **Endpoint Metrics**: Per-endpoint performance tracking
- **Custom Metrics**: Extensible metric system via Prometheus client

## Development

### Testing
```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests
make test-integration

# Run with coverage
make test-cov

# Clean test artifacts
make clean
```

### Running Locally
```bash
# Install dependencies
make install

# Install Graphviz (required for Graphviz diagrams)
# macOS: brew install graphviz
# Ubuntu/Debian: apt-get install graphviz
# Windows: Download from https://graphviz.org/download/

# Optional: Install Mermaid CLI (for local Mermaid rendering)
npm install -g @mermaid-js/mermaid-cli

# Run with uvicorn (development)
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
# Build image (includes Graphviz)
docker build -t creative-service .

# Run container
docker run -p 8000:8000 --env-file .env creative-service
```

## Deployment

### Kubernetes
- **Port**: 8000 (default)
- **Health Check**: `GET /healthz`
- **Liveness Probe**: Every 10s, timeout 5s
- **Readiness Probe**: Every 10s, timeout 5s
- **Resource Requirements**: Adjust based on concurrent request load (image/video generation is CPU/GPU intensive)

### Scaling
- **Horizontal Scaling**: Stateless design allows multiple instances
- **Load Balancing**: Use Kubernetes service or ingress load balancer
- **Async Processing**: All providers use async HTTP clients for efficient concurrent requests

### Environment Variables
Use Kubernetes Secrets or ConfigMaps for sensitive configuration:
- API keys → Secrets
- Service configuration → ConfigMaps

### System Dependencies
- **Graphviz**: Required for Graphviz diagram rendering (included in Dockerfile)
- **Mermaid CLI**: Optional, for local Mermaid rendering (defaults to mermaid.ink API)

## Documentation

- **README.md**: Comprehensive service documentation and usage examples
- **HEALTH_CHECK.md**: Detailed health check documentation
- **LOGGING.md**: Structured logging guidelines and usage
- **ENVIRONMENT.md**: Environment variable reference
- **tests/README.md**: Testing documentation

## Breaking Changes

None - This is the initial release.

## Future Enhancements

Potential improvements for future versions:
- Additional image providers (Midjourney, Leonardo.ai, etc.)
- Runway Gen-2 video generation support
- Batch generation endpoints
- Image editing and manipulation endpoints
- Caching layer for frequently requested content
- Rate limiting and usage quotas
- Cost tracking and analytics
- Custom prompt templates
- Webhook support for async generation
- Image optimization and compression
- CDN integration for generated assets

## Contributors

Initial release by the Woragis team.

## License

Part of the Woragis backend infrastructure.

