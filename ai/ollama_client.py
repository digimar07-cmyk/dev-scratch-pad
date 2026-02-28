"""Ollama client - comunicação com modelos"""
import time
import requests
from core.config import OLLAMA_MODELS, TIMEOUTS
from core.logging_setup import LOGGER


class OllamaClient:
    def __init__(self, active_models):
        self.logger = LOGGER
        self.active_models = active_models
        self.http_session = requests.Session()
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_retries = 3
        self.ollama_health_timeout = 4
        self._ollama_health_cache = {"ts": 0.0, "ok": None}
        self.stop_analysis = False

    def _ollama_is_available(self) -> bool:
        try:
            now = time.time()
            cached = self._ollama_health_cache
            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
                return bool(cached["ok"])
            resp = self.http_session.get(
                f"{self.ollama_base_url}/api/tags",
                timeout=self.ollama_health_timeout,
            )
            ok = resp.status_code == 200
            self._ollama_health_cache = {"ts": now, "ok": ok}
            return ok
        except Exception:
            self._ollama_health_cache = {"ts": time.time(), "ok": False}
            return False

    def _model_name(self, role: str) -> str:
        return self.active_models.get(role, OLLAMA_MODELS.get(role, ""))

    def _timeout(self, role: str):
        return TIMEOUTS.get(role, (5, 30))

    def _ollama_generate_text(
        self,
        prompt: str,
        *,
        role: str = "text_quality",
        temperature: float = 0.7,
        num_predict: int = 350,
    ) -> str:
        if self.stop_analysis:
            return ""
        if not self._ollama_is_available():
            self.logger.warning("Ollama indisponível. Usando fallback.")
            return ""

        model = self._model_name(role)
        timeout = self._timeout(role)

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
        for attempt in range(1, self.ollama_retries + 1):
            if self.stop_analysis:
                return ""
            try:
                resp = self.http_session.post(
                    f"{self.ollama_base_url}/api/chat",
                    json=payload,
                    timeout=timeout,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                text = (data.get("message") or {}).get("content") or data.get("response") or ""
                self.logger.info("✅ [%s] gerou resposta (%d chars)", model, len(text))
                return text.strip()
            except Exception as e:
                last_err = e
                self.logger.warning("Ollama falhou (tentativa %d/%d) [%s]: %s", attempt, self.ollama_retries, model, e)
                if attempt < self.ollama_retries:
                    time.sleep(2.0)
        if last_err:
            self.logger.error("Ollama falhou definitivamente [%s]: %s", model, last_err, exc_info=True)
        return ""
