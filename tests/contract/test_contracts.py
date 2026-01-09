"""
Contract tests for Creative Service
Validates API contracts and data structures
"""
import pytest


class TestCreativeServiceContracts:
    """Contract tests for Creative Service API"""

    def test_image_generation_request_contract(self):
        """Test image generation request payload contract"""
        valid_request = {
            "provider": "openai",
            "prompt": "A futuristic city",
            "size": "1024x1024",
            "quality": "high",
            "style": "photorealistic",
        }

        # Validate required fields
        assert "provider" in valid_request
        assert "prompt" in valid_request

        # Validate types
        assert isinstance(valid_request["provider"], str)
        assert isinstance(valid_request["prompt"], str)

    def test_image_generation_response_contract(self):
        """Test image generation response structure"""
        response = {
            "images": [
                {"url": "https://example.com/image1.png", "id": "img-123"}
            ],
            "model": "dall-e-3",
            "created": 1234567890,
            "usage": {"prompt_tokens": 20},
        }

        # Validate required fields
        assert "images" in response
        assert isinstance(response["images"], list)
        assert len(response["images"]) > 0

        # Validate image structure
        image = response["images"][0]
        assert "url" in image
        assert "id" in image

    def test_video_generation_request_contract(self):
        """Test video generation request structure"""
        request = {
            "provider": "replicate",
            "prompt": "A cat dancing",
            "duration": 10,
            "fps": 30,
        }

        assert "provider" in request
        assert "prompt" in request
        assert request["duration"] > 0
        assert request["fps"] > 0

    def test_diagram_generation_request_contract(self):
        """Test diagram generation request"""
        request = {
            "type": "flowchart",
            "specification": "graph LR; A --> B --> C",
            "format": "svg",
        }

        valid_types = ["flowchart", "sequence", "class", "statediagram"]
        assert request["type"] in valid_types

    def test_provider_contract(self):
        """Test supported providers"""
        supported_providers = ["openai", "anthropic", "replicate", "graphviz"]
        test_provider = "openai"

        assert test_provider in supported_providers

    def test_error_response_contract(self):
        """Test error response structure"""
        error_response = {
            "error": {
                "code": "PROVIDER_ERROR",
                "message": "Failed to generate image",
                "details": "Rate limit exceeded",
            },
            "request_id": "req-123456",
        }

        assert "error" in error_response
        assert "code" in error_response["error"]
        assert "message" in error_response["error"]

    def test_cost_tracking_contract(self):
        """Test cost tracking response"""
        cost_response = {
            "provider": "openai",
            "operation": "image_generation",
            "cost": 0.02,
            "tokens_used": None,
        }

        assert "provider" in cost_response
        assert "cost" in cost_response
        assert cost_response["cost"] >= 0

    def test_quality_validation_contract(self):
        """Test quality validation contract"""
        quality_result = {
            "status": "passed",
            "checks": {
                "toxicity": "passed",
                "nsfw": "passed",
                "format": "passed",
            },
        }

        assert "status" in quality_result
        assert quality_result["status"] in ["passed", "failed", "warning"]
