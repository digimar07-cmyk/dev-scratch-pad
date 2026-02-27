"""Ollama AI service with health checks and retry logic."""
import time
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger("Laserflix.Ollama")


class OllamaService:
    """Manages communication with Ollama API."""
    
    def __init__(self, base_url: str, retries: int = 3, health_timeout: int = 4):
        self.base_url = base_url
        self.retries = retries
        self.health_timeout = health_timeout
        self.session = requests.Session()
        self._health_cache = {"ts": 0.0, "ok": None}
        self.stop_flag = False
    
    def is_available(self) -> bool:
        """Check Ollama availability with 5s cache."""
        try:
            now = time.time()
            cached = self._health_cache
            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
                return bool(cached["ok"])
            
            resp = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=self.health_timeout,
            )
            ok = resp.status_code == 200
            self._health_cache = {"ts": now, "ok": ok}
            return ok
        except Exception:
            self._health_cache = {"ts": time.time(), "ok": False}
            return False
    
    def generate_text(
        self,
        prompt: str,
        model: str,
        timeout: tuple,
        temperature: float = 0.7,
        num_predict: int = 350,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate text using chat API with instruction format."""
        if self.stop_flag:
            return ""
        
        if not self.is_available():
            logger.warning("Ollama unavailable, returning empty")
            return ""
        
        # Default system prompt for Laserflix context
        if system_prompt is None:
            system_prompt = (
                "Você é um assistente especialista em produtos de corte laser, "
                "decoração artesanal e objetos afetivos personalizados. "
                "Responda SEMPRE em português brasileiro. "
                "Siga as instruções de formato com precisão."
            )
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
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
        for attempt in range(1, self.retries + 1):
            if self.stop_flag:
                return ""
            
            try:
                resp = self.session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=timeout,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                
                data = resp.json()
                text = (data.get("message") or {}).get("content") or data.get("response") or ""
                logger.info(f"✅ [{model}] generated {len(text)} chars")
                return text.strip()
            except Exception as e:
                last_err = e
                logger.warning(f"Attempt {attempt}/{self.retries} failed [{model}]: {e}")
                if attempt < self.retries:
                    time.sleep(2.0)
        
        if last_err:
            logger.error(f"All retries failed [{model}]: {last_err}", exc_info=True)
        return ""
    
    def generate_with_vision(
        self,
        prompt: str,
        image_b64: str,
        model: str,
        timeout: tuple,
        temperature: float = 0.2,
        num_predict: int = 60,
    ) -> str:
        """Generate description from image using vision model."""
        if self.stop_flag:
            return ""
        
        if not self.is_available():
            return ""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            },
        }
        
        try:
            resp = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
            )
            if resp.status_code == 200:
                vision_text = (resp.json().get("response") or "").strip()
                logger.info(f"👁️ [{model}] vision: {vision_text[:80]}")
                return vision_text
        except Exception as e:
            logger.warning(f"Vision generation failed: {e}")
        return ""
    
    def list_models(self) -> list:
        """List available models from Ollama."""
        try:
            resp = self.session.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                return [m["name"] for m in resp.json().get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        return []
    
    def close(self):
        """Close HTTP session."""
        self.session.close()
