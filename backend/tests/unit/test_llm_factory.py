from app.ai.llm.base import ILLMClient
from app.ai.llm.factory import get_llm_client
from app.config.settings import settings


def test_default_provider_is_ollama():
    client = get_llm_client()
    assert isinstance(client, ILLMClient)
    # Default provider exposes the configured Ollama model name.
    assert client.model_name == settings.OLLAMA_MODEL
