"""
LASERFLIX v3.0 — Cliente Ollama (IA)
Camada isolada para comunicação com Ollama API.

Extraído da v7.4.0 para isolar lógica de IA do resto da aplicação.

Responsabilidades:
- Health check do serviço Ollama
- Geração de texto (Qwen 2.5)
- Análise de imagem (Moondream)
- Retry logic + timeout + cache
- Seleção automática de modelo (qualidade vs velocidade)
"""

import requests
import time
import base64
import io
from typing import Optional, Tuple
from PIL import Image

from config import OLLAMA_MODELS, FAST_MODEL_THRESHOLD, TIMEOUTS, LOGGER


class OllamaClient:
    """
    Cliente HTTP para comunicação com Ollama API local.
    
    Features:
    - Health check com cache de 5s
    - Retry automático (3 tentativas)
    - Timeouts configuráveis por modelo
    - Seleção automática de modelo baseada em batch size
    - Suporte a chat/messages format (Qwen instruction-following)
    
    Exemplos:
        >>> client = OllamaClient()
        >>> client.check_health()
        True
        >>> client.generate_text("Descreva um porta-retrato de Páscoa")
        'Um porta-retrato temático...'
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Args:
            base_url: URL base do Ollama (default: localhost:11434)
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.retries = 3
        self.health_timeout = 4
        
        # Cache de health check (timestamp, resultado)
        self._health_cache = {"ts": 0.0, "ok": None}
        
        # Modelos ativos (podem ser customizados)
        self.active_models = dict(OLLAMA_MODELS)
    
    def check_health(self) -> bool:
        """
        Verifica se Ollama está disponível (com cache de 5s).
        
        Returns:
            True se Ollama responder, False caso contrário
        
        Exemplos:
            >>> client.check_health()
            True
        """
        try:
            now = time.time()
            cached = self._health_cache
            
            # Cache hit?
            if cached.get("ok") is not None and (now - cached.get("ts", 0.0)) < 5.0:
                return bool(cached["ok"])
            
            # Cache miss - faz request
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
    
    def _get_model_name(self, role: str) -> str:
        """
        Retorna o nome do modelo configurado para o papel dado.
        
        Args:
            role: Papel do modelo ("text_quality", "text_fast", "vision", "embed")
        
        Returns:
            Nome do modelo
        """
        return self.active_models.get(role, OLLAMA_MODELS.get(role, ""))
    
    def _get_timeout(self, role: str) -> Tuple[int, int]:
        """
        Retorna o timeout (connect, read) para o modelo.
        
        Args:
            role: Papel do modelo
        
        Returns:
            Tupla (connect_timeout, read_timeout)
        """
        return TIMEOUTS.get(role, (5, 30))
    
    def choose_text_role(self, batch_size: int = 1) -> str:
        """
        Escolhe qual modelo usar baseado no tamanho do lote.
        
        Args:
            batch_size: Número de itens a processar
        
        Returns:
            "text_fast" para lotes grandes, "text_quality" para análise individual
        
        Exemplos:
            >>> client.choose_text_role(batch_size=100)
            'text_fast'
            >>> client.choose_text_role(batch_size=1)
            'text_quality'
        """
        if batch_size > FAST_MODEL_THRESHOLD:
            return "text_fast"
        return "text_quality"
    
    def generate_text(
        self,
        prompt: str,
        *,
        role: str = "text_quality",
        temperature: float = 0.7,
        num_predict: int = 350,
        stop_flag: Optional[callable] = None,
    ) -> str:
        """
        Gera texto usando o modelo Qwen.
        
        Usa /api/chat com messages format para garantir instruction-following correto.
        Retry automático em caso de falha.
        
        Args:
            prompt: Prompt de instrução
            role: Papel do modelo ("text_quality" ou "text_fast")
            temperature: Temperatura de geração (0.0-1.0)
            num_predict: Máximo de tokens a gerar
            stop_flag: Função que retorna True se deve parar (opcional)
        
        Returns:
            Texto gerado ou string vazia em caso de falha
        
        Exemplos:
            >>> client.generate_text("Descreva um porta-retrato", temperature=0.5)
            'Um porta-retrato elegante...'
        """
        # Verifica flag de parada
        if stop_flag and stop_flag():
            return ""
        
        if not self.check_health():
            LOGGER.warning("Ollama indisponível. Usando fallback.")
            return ""
        
        model = self._get_model_name(role)
        timeout = self._get_timeout(role)
        
        # Payload com chat/messages format (ideal para Qwen2.5-Instruct)
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
        for attempt in range(1, self.retries + 1):
            if stop_flag and stop_flag():
                return ""
            
            try:
                resp = self.session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=timeout,
                )
                
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {resp.status_code}: {resp.text[:200]}")
                
                data = resp.json()
                text = (data.get("message") or {}).get("content") or data.get("response") or ""
                
                LOGGER.info("✅ [%s] gerou resposta (%d chars)", model, len(text))
                return text.strip()
                
            except Exception as e:
                last_err = e
                LOGGER.warning(
                    "Ollama falhou (tentativa %d/%d) [%s]: %s",
                    attempt, self.retries, model, e
                )
                
                if attempt < self.retries:
                    time.sleep(2.0)
        
        if last_err:
            LOGGER.error(
                "Ollama falhou definitivamente [%s]: %s",
                model, last_err, exc_info=True
            )
        
        return ""
    
    def describe_image(self, image_path: str) -> str:
        """
        Usa Moondream para descrever o OBJETO CENTRAL da imagem.
        
        Prompt cirúrgico: ignora fundo, brinquedos e marcas d'água.
        Redimensiona imagem para 512x512 antes de enviar.
        
        Args:
            image_path: Caminho completo da imagem
        
        Returns:
            Descrição visual ou string vazia em caso de falha
        
        Exemplos:
            >>> client.describe_image("/path/to/cover.png")
            'A wooden Easter bunny frame with floral details'
        """
        import os
        
        if not image_path or not os.path.exists(image_path):
            return ""
        
        if not self.check_health():
            return ""
        
        model = self._get_model_name("vision")
        timeout = self._get_timeout("vision")
        
        try:
            # Redimensiona e converte para base64
            with Image.open(image_path) as img:
                img.thumbnail((512, 512), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            
            payload = {
                "model": model,
                "prompt": (
                    "Look only at the main laser-cut wooden object in the center of this image. "
                    "Ignore the background, walls, stuffed animals, toys, watermarks and any text overlays. "
                    "Describe ONLY the central object: its shape, theme and style. "
                    "One short sentence. Be specific and factual."
                ),
                "images": [img_b64],
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 60},
            }
            
            resp = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
            )
            
            if resp.status_code == 200:
                vision_text = (resp.json().get("response") or "").strip()
                LOGGER.info("👁️ [moondream] %s", vision_text[:80])
                return vision_text
        
        except Exception as e:
            LOGGER.warning("Falha ao descrever imagem com moondream: %s", e)
        
        return ""
    
    def update_models(self, models_dict: dict) -> None:
        """
        Atualiza os modelos ativos.
        
        Args:
            models_dict: Dicionário {role: model_name}
        
        Exemplos:
            >>> client.update_models({"text_quality": "qwen2.5:14b"})
        """
        self.active_models.update(models_dict)
        LOGGER.info("Modelos atualizados: %s", models_dict)
