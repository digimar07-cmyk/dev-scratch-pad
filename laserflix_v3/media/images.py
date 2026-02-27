"""
LASERFLIX v3.0 — Processamento de Imagens
Camada isolada para manipulação de imagens (thumbnails, covers, hero).

Extraído da v7.4.0 para isolar lógica de mídia do resto da aplicação.

Responsabilidades:
- Localização de imagens de capa
- Geração de thumbnails (com cache LRU)
- Análise de qualidade de imagem (filtro para visão)
- Hero images para modais
- Listagem de todas as imagens de um projeto
"""

import os
from collections import OrderedDict
from typing import Optional, List, Dict, Any
from PIL import Image, ImageTk, ImageStat

from config import LOGGER


class ImageProcessor:
    """
    Processador de imagens com cache LRU de thumbnails.
    
    Features:
    - Cache de thumbnails (LRU com limite configurável)
    - Validação de mtime para invalidar cache
    - Análise de qualidade de imagem (brilho, saturação, pixels brancos)
    - Redimensionamento inteligente
    
    Exemplos:
        >>> processor = ImageProcessor(cache_limit=300)
        >>> thumb = processor.get_thumbnail("/path/to/image.png")
        >>> quality = processor.analyze_quality("/path/to/image.png")
        >>> quality['use_vision']
        True
    """
    
    def __init__(self, cache_limit: int = 300):
        """
        Args:
            cache_limit: Número máximo de thumbnails em cache
        """
        self.thumbnail_cache = OrderedDict()
        self.cache_limit = cache_limit
        
        # Extensões válidas
        self.valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    
    def find_first_image(self, project_path: str) -> Optional[str]:
        """
        Encontra a primeira imagem na pasta do projeto.
        
        Args:
            project_path: Caminho completo do projeto
        
        Returns:
            Caminho da primeira imagem ou None
        
        Exemplos:
            >>> processor.find_first_image("/projects/easter_frame")
            '/projects/easter_frame/cover.png'
        """
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(self.valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            LOGGER.exception("Falha ao listar %s", project_path)
        
        return None
    
    def get_thumbnail(self, image_path: str, size: tuple = (220, 200)) -> Optional[Any]:
        """
        Gera thumbnail com cache LRU.
        
        Verifica mtime do arquivo para invalidar cache automaticamente.
        
        Args:
            image_path: Caminho completo da imagem
            size: Tamanho máximo (width, height)
        
        Returns:
            ImageTk.PhotoImage ou None em caso de falha
        
        Exemplos:
            >>> thumb = processor.get_thumbnail("/path/img.png", size=(200, 180))
        """
        if not image_path or not os.path.exists(image_path):
            return None
        
        try:
            mtime = os.path.getmtime(image_path)
        except Exception:
            return None
        
        try:
            # Cache hit?
            cached = self.thumbnail_cache.get(image_path)
            if cached:
                cached_mtime, cached_photo = cached
                if cached_mtime == mtime:
                    # Move para o fim (LRU)
                    self.thumbnail_cache.move_to_end(image_path)
                    return cached_photo
            
            # Cache miss - gera thumbnail
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Armazena no cache
            self.thumbnail_cache[image_path] = (mtime, photo)
            self.thumbnail_cache.move_to_end(image_path)
            
            # Limpa cache se excedeu limite
            while len(self.thumbnail_cache) > self.cache_limit:
                self.thumbnail_cache.popitem(last=False)
            
            return photo
        
        except Exception:
            LOGGER.exception("Erro ao gerar thumbnail de %s", image_path)
            return None
    
    def get_hero_image(self, project_path: str, max_width: int = 800) -> Optional[Any]:
        """
        Gera imagem hero (alta resolução) para modal.
        
        Args:
            project_path: Caminho completo do projeto
            max_width: Largura máxima
        
        Returns:
            ImageTk.PhotoImage ou None
        
        Exemplos:
            >>> hero = processor.get_hero_image("/projects/frame", max_width=1200)
        """
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(self.valid_extensions):
                    img_path = os.path.join(project_path, item)
                    img = Image.open(img_path)
                    
                    # Redimensiona se necessário
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    
                    return ImageTk.PhotoImage(img)
        
        except Exception:
            LOGGER.exception("Falha ao carregar hero image de %s", project_path)
        
        return None
    
    def list_all_images(self, project_path: str) -> List[str]:
        """
        Lista todos os arquivos de imagem no projeto.
        
        Args:
            project_path: Caminho completo do projeto
        
        Returns:
            Lista de caminhos completos das imagens (ordenada)
        
        Exemplos:
            >>> processor.list_all_images("/projects/frame")
            ['/projects/frame/cover.png', '/projects/frame/detail1.jpg']
        """
        images = []
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(self.valid_extensions):
                    images.append(os.path.join(project_path, item))
        except Exception:
            LOGGER.exception("Falha ao listar imagens de %s", project_path)
        
        return sorted(images)
    
    def analyze_quality(self, image_path: str) -> Dict[str, Any]:
        """
        Avalia qualidade de imagem para decidir se usar análise de visão.
        
        Critérios de rejeição (imagem ambígua para visão):
        - Brilho médio > 210 (foto muito clara / fundo branco dominante)
        - Saturação média < 25 (quase monocromática)
        - % de pixels brancos > 50% (mockup com fundo branco)
        
        Args:
            image_path: Caminho completo da imagem
        
        Returns:
            Dict com métricas e flag 'use_vision'
        
        Exemplos:
            >>> quality = processor.analyze_quality("/path/to/image.png")
            >>> quality
            {'brightness': 180.5, 'saturation': 65.2, 'white_pct': 15.3, 'use_vision': True}
        """
        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                w, h = img_rgb.size
                
                # Analisa só a área central (remove bordas com marca d'água)
                box = (int(w*0.05), int(h*0.10), int(w*0.75), int(h*0.90))
                center = img_rgb.crop(box)
                
                # Brilho médio (canal L)
                gray = center.convert("L")
                stat_g = ImageStat.Stat(gray)
                brightness = stat_g.mean[0]
                
                # Saturação média (canal S do HSV)
                hsv = center.convert("HSV")
                stat_s = ImageStat.Stat(hsv)
                saturation = stat_s.mean[1]
                
                # % pixels brancos (aproximação)
                white_pct = (brightness / 255.0) * max(0, 1.0 - (stat_g.stddev[0] / 80.0))
                white_pct_normalized = white_pct * 100
                
                # Decide se usa visão
                use_vision = not (
                    brightness > 210 or
                    saturation < 25  or
                    white_pct_normalized > 50
                )
                
                LOGGER.info(
                    "📊 [quality] brilho=%.1f sat=%.1f fundo_branco~%.1f%% → vision=%s",
                    brightness, saturation, white_pct_normalized, use_vision
                )
                
                return {
                    "brightness": brightness,
                    "saturation": saturation,
                    "white_pct":  white_pct_normalized,
                    "use_vision": use_vision,
                }
        
        except Exception as e:
            LOGGER.warning("Falha em analyze_quality: %s", e)
            return {
                "brightness": 0,
                "saturation": 100,
                "white_pct": 0,
                "use_vision": True,
            }
    
    def clear_cache(self) -> None:
        """
        Limpa todo o cache de thumbnails.
        
        Exemplos:
            >>> processor.clear_cache()
        """
        self.thumbnail_cache.clear()
        LOGGER.info("Cache de thumbnails limpo")
