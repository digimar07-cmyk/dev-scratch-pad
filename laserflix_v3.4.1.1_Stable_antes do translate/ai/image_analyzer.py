"""
Análise de qualidade de imagem e integração com visão
"""
import os
from PIL import Image, ImageStat
from config.settings import IMAGE_QUALITY_THRESHOLDS
from utils.logging_setup import LOGGER


class ImageAnalyzer:
    """
    Analisa qualidade de imagens e decide se são adequadas para análise com moondream.
    
    Critérios de rejeição (imagens ambíguas):
      - Brilho médio > 210 (foto muito clara/fundo branco dominante)
      - Saturação média < 25 (quase monocromática)
      - % pixels brancos > 50% (mockup com fundo branco)
    """
    
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.logger = LOGGER
        self.thresholds = IMAGE_QUALITY_THRESHOLDS
    
    def quality_score(self, image_path):
        """
        Avalia qualidade da imagem para análise visual.
        
        Returns:
            dict com métricas:
                - brightness: brilho médio (0-255)
                - saturation: saturação média (0-255)
                - white_pct: % aproximada de pixels brancos
                - use_vision: True se imagem é adequada
        """
        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                w, h = img_rgb.size
                
                # Analisa só área central (remove bordas com marca d'água)
                box = (
                    int(w * 0.05),
                    int(h * 0.10),
                    int(w * 0.75),
                    int(h * 0.90)
                )
                center = img_rgb.crop(box)
                
                # Brilho médio (canal L - luminosidade)
                gray = center.convert("L")
                stat_g = ImageStat.Stat(gray)
                brightness = stat_g.mean[0]
                
                # Saturação média (canal S do HSV)
                hsv = center.convert("HSV")
                stat_s = ImageStat.Stat(hsv)
                saturation = stat_s.mean[1]
                
                # Aproximação de % pixels brancos
                # (pixels claros = brilho alto E baixo desvio padrão)
                white_pct = (brightness / 255.0) * max(0, 1.0 - (stat_g.stddev[0] / 80.0))
                white_pct_normalized = white_pct * 100
                
                # Decide se deve usar visão
                use_vision = not (
                    brightness > self.thresholds["max_brightness"] or
                    saturation < self.thresholds["min_saturation"] or
                    white_pct_normalized > self.thresholds["max_white_pct"]
                )
                
                self.logger.info(
                    "📊 [quality] brilho=%.1f sat=%.1f fundo_branco~%.1f%% → vision=%s",
                    brightness, saturation, white_pct_normalized, use_vision
                )
                
                return {
                    "brightness": brightness,
                    "saturation": saturation,
                    "white_pct": white_pct_normalized,
                    "use_vision": use_vision,
                }
        
        except Exception as e:
            self.logger.warning("Falha em quality_score: %s", e)
            # Fallback: assume imagem válida
            return {
                "brightness": 0,
                "saturation": 100,
                "white_pct": 0,
                "use_vision": True
            }
    
    def should_use_vision(self, image_path):
        """
        Retorna True se imagem passa no filtro de qualidade.
        """
        if not image_path or not os.path.exists(image_path):
            return False
        
        quality = self.quality_score(image_path)
        return quality["use_vision"]
    
    def analyze_cover(self, image_path):
        """
        Analisa imagem de capa com moondream (se passar no filtro de qualidade).
        
        Returns:
            String com descrição visual ou "" se:
              - Imagem não existe
              - Não passa no filtro de qualidade
              - Ollama indisponível
        """
        if not image_path or not os.path.exists(image_path):
            return ""
        
        # Verifica qualidade primeiro
        quality = self.quality_score(image_path)
        
        if not quality["use_vision"]:
            self.logger.info(
                "⚠️ Visão desativada para %s (brilho=%.1f sat=%.1f fundo~%.1f%%)",
                os.path.basename(image_path),
                quality["brightness"],
                quality["saturation"],
                quality["white_pct"]
            )
            return ""
        
        # Usa moondream
        return self.ollama_client.describe_image(image_path)
