"""Cliente HTTP e comunicação com Ollama."""
import time
import requests
from core.config import OLLAMA_MODELS, TIMEOUTS


def init_http_session(app):
    app.http_session = requests.Session()
    app.ollama_base_url = "http://localhost:11434"
    app.ollama_retries = 3
    app.ollama_health_timeout = 4
    app._ollama_health_cache = {"ts": 0.0, "ok": None}
    app.active_models = dict(OLLAMA_MODELS)


def _ollama_is_available(app) -> bool:
    """Checa disponibilidade do Ollama com cache de 5s."""
    try:
        now = time.time()
        cached = app._ollama_health_cache
        if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
            return bool(cached["ok"])
        resp = app.http_session.get(
            f"{app.ollama_base_url}/api/tags",
            timeout=app.ollama_health_timeout,
        )
        ok = resp.status_code == 200
        app._ollama_health_cache = {"ts": now, "ok": ok}
        return ok
    except Exception:
        app._ollama_health_cache = {"ts": time.time(), "ok": False}
        return False


def _model_name(app, role: str) -> str:
    return app.active_models.get(role, OLLAMA_MODELS.get(role, ""))


def _timeout(app, role: str):
    return TIMEOUTS.get(role, (5, 30))


def _ollama_generate_text(
    app,
    prompt: str,
    *,
    role: str = "text_quality",
    temperature: float = 0.7,
    num_predict: int = 350,
) -> str:
    """Gera texto com o modelo definido por `role`."""
    if getattr(app, "stop_analysis", False):
        return ""
    if not _ollama_is_available(app):
        app.logger.warning("Ollama indisponível. Usando fallback.")
        return ""

    model = _model_name(app, role)
    timeout = _timeout(app, role)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é um assistente especialista em produtos de corte laser, "
                    "decoração artesanal e objetos afetivos personalizados. "
                    "Responda SEMPRE em português brasileiro. "
                    "Siga as instruções de formato com precisão."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 40,
            "num_predict": num_predict,
            "repeat_penalty": 1.1,
        },
    }

    last_err = None
    for attempt in range(1, app.ollama_retries + 1):
        if getattr(app, "stop_analysis", False):
            return ""
        try:
            resp = app.http_session.post(
                f"{app.ollama_base_url}/api/chat",
                json=payload,
                timeout=timeout,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama HTTP {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            text = (data.get("message") or {}).get("content") or data.get("response") or ""
            app.logger.info("✅ [%s] gerou resposta (%d chars)", model, len(text))
            return text.strip()
        except Exception as e:
            last_err = e
            app.logger.warning("Ollama falhou (tentativa %d/%d) [%s]: %s", attempt, app.ollama_retries, model, e)
            if attempt < app.ollama_retries:
                time.sleep(2.0)
    if last_err:
        app.logger.error("Ollama falhou definitivamente [%s]: %s", model, last_err, exc_info=True)
    return ""
