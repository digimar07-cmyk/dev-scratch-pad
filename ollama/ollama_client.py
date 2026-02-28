"""Cliente HTTP Ollama completo."""
import requests
import time
from functools import lru_cache
from core.config import OLLAMA_BASE_URL, OLLAMA_TIMEOUT, OLLAMA_MODELS, TIMEOUTS


def init_http_session(app):
    """Inicializa sessão HTTP reutilizável."""
    app.http_session = requests.Session()
    app.ollama_base_url = OLLAMA_BASE_URL


@lru_cache(maxsize=1)
def _ollama_health_check_cached(timestamp):
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _ollama_is_available(app):
    """Verifica se Ollama está disponível (com cache de 5s)."""
    timestamp = int(time.time() / 5)
    return _ollama_health_check_cached(timestamp)


def is_ollama_available(app):
    """Alias público."""
    return _ollama_is_available(app)


def _model_name(app, role):
    """Retorna nome do modelo para o role."""
    return app.current_models.get(role, OLLAMA_MODELS.get(role, "qwen2.5:7b-instruct-q4_K_M"))


def _timeout(app, role):
    """Retorna timeout para o role."""
    return TIMEOUTS.get(role, (5, 120))[1]


def _ollama_generate_text(app, prompt, role="text_quality", temperature=0.7, num_predict=200):
    """Gera texto usando Ollama."""
    if not _ollama_is_available(app):
        return None
    
    model = _model_name(app, role)
    timeout_val = _timeout(app, role)
    
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
            timeout=timeout_val
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    
    except Exception as e:
        if hasattr(app, 'logger'):
            app.logger.error(f"Erro Ollama generate: {e}")
    
    return None
