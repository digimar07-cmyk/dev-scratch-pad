"""Cliente HTTP Ollama."""
import requests
from functools import lru_cache
from core.config import OLLAMA_BASE_URL, OLLAMA_TIMEOUT


def init_http_session(app):
    """Inicializa sessão HTTP reutilizável."""
    app.http_session = requests.Session()


@lru_cache(maxsize=1)
def _ollama_health_check_cached(timestamp):
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def is_ollama_available(app):
    import time
    timestamp = int(time.time() / 5)
    return _ollama_health_check_cached(timestamp)


def _ollama_generate_text(app, prompt, role="text_quality", temperature=0.7, num_predict=200):
    if not is_ollama_available(app):
        return None
    
    model = app.current_models.get(role, "qwen2.5:7b-instruct-q4_K_M")
    
    try:
        response = app.http_session.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,
                }
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    
    except Exception as e:
        app.logger.error(f"Erro Ollama generate: {e}")
    
    return None
