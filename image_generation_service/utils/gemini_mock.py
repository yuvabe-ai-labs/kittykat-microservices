class _FakeFinishReason:
    def __init__(self, name: str):
        self.name = name


class _FakeCandidate:
    def __init__(self, finish_reason_name: str):
        self.finish_reason = _FakeFinishReason(finish_reason_name)
        self.content = None  # no image parts → asset_base64s stays []


class _FakeGenerateContentResponse:
    def __init__(self, finish_reason_name: str):
        self.candidates = [_FakeCandidate(finish_reason_name)]
        self.usage_metadata = {"promptTokenCount": 0, "totalTokenCount": 0}
        self.sdk_http_response = None

    def to_json_dict(self):
        return {
            "candidates": [{"content": {}, "finishReason": self.candidates[0].finish_reason.name}],
            "usageMetadata": self.usage_metadata,
        }


class _FakeImagenResponse:
    generated_images = []
    sdk_http_response = None

    def to_json_dict(self):
        return {"generatedImages": []}


class _FakeModels:
    def __init__(self, finish_reason_name: str):
        self._finish_reason_name = finish_reason_name

    async def generate_content(self, **kwargs):
        return _FakeGenerateContentResponse(self._finish_reason_name)

    async def generate_images(self, **kwargs):
        # Imagen path — empty list triggers existing NSFW handling
        return _FakeImagenResponse()


class _FakeAio:
    def __init__(self, finish_reason_name: str):
        self.models = _FakeModels(finish_reason_name)


class FakeGeminiClient:
    """
    Drop-in replacement for genai.Client. Returns a fake response with no images
    and the configured finishReason — zero real API calls made.

    Activated by setting GEMINI_MOCK_FINISH_REASON in the environment, e.g.:
        GEMINI_MOCK_FINISH_REASON=MALFORMED_FUNCTION_CALL
    """

    def __init__(self, finish_reason_name: str):
        self.aio = _FakeAio(finish_reason_name)
