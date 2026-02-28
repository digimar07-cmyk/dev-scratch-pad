"""
Cache LRU de thumbnails
"""
import os
from collections import OrderedDict
from PIL import Image, ImageTk
from config.settings import THUMBNAIL_CACHE_LIMIT, THUMBNAIL_SIZE
from config.constants import FILE_EXTENSIONS
from utils.logging_setup import LOGGER


class ThumbnailCache:
    """
    Cache LRU (Least Recently Used) para thumbnails.
    Limite padrão: 300 imagens.
    """
    
    def __init__(self, limit=THUMBNAIL_CACHE_LIMIT):
        self.cache = OrderedDict()
        self.limit = limit
        self.logger = LOGGER
    
    def get(self, image_path):
        """
        Busca thumbnail no cache. Retorna PhotoImage ou None.
        Atualiza posição LRU se encontrado.
        """
        if not image_path or not os.path.exists(image_path):
            return None
        
        try:
            mtime = os.path.getmtime(image_path)
        except Exception:
            return None
        
        cached = self.cache.get(image_path)
        if cached:
            cached_mtime, cached_photo = cached
            # Valida se arquivo não foi modificado
            if cached_mtime == mtime:
                # Move para o fim (marca como recentemente usado)
                self.cache.move_to_end(image_path)
                return cached_photo
            else:
                # Arquivo modificado, remove do cache
                del self.cache[image_path]
        
        return None
    
    def set(self, image_path, photo):
        """
        Adiciona thumbnail ao cache.
        Remove item mais antigo se exceder limite.
        """
        if not image_path:
            return
        
        try:
            mtime = os.path.getmtime(image_path)
            self.cache[image_path] = (mtime, photo)
            self.cache.move_to_end(image_path)
            
            # Remove itens antigos se exceder limite
            while len(self.cache) > self.limit:
                oldest_key, _ = self.cache.popitem(last=False)
                self.logger.debug("🗑️ Cache LRU: removido %s", oldest_key)
        
        except Exception as e:
            self.logger.warning("Erro ao adicionar ao cache: %s", e)
    
    def load_thumbnail(self, image_path):
        """
        Carrega e cacheia thumbnail de uma imagem.
        Retorna PhotoImage ou None.
        """
        # Verifica cache primeiro
        cached = self.get(image_path)
        if cached:
            return cached
        
        # Gera novo thumbnail
        try:
            img = Image.open(image_path)
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.set(image_path, photo)
            return photo
        
        except Exception as e:
            self.logger.warning("Erro ao gerar thumbnail de %s: %s", image_path, e)
            return None
    
    def find_first_image(self, project_path):
        """
        Encontra primeira imagem válida na pasta do projeto.
        Retorna caminho completo ou None.
        """
        valid_extensions = FILE_EXTENSIONS["images"]
        
        try:
            for item in os.listdir(project_path):
                if item.lower().endswith(valid_extensions):
                    return os.path.join(project_path, item)
        except Exception:
            self.logger.exception("Falha ao listar %s", project_path)
        
        return None
    
    def get_cover_image(self, project_path):
        """
        Retorna PhotoImage da capa do projeto (primeira imagem encontrada).
        Usa cache automaticamente.
        """
        img_path = self.find_first_image(project_path)
        if not img_path:
            return None
        
        return self.load_thumbnail(img_path)
    
    def clear(self):
        """
        Limpa todo o cache.
        """
        self.cache.clear()
        self.logger.info("🗑️ Cache de thumbnails limpo")
    
    def get_stats(self):
        """
        Retorna estatísticas do cache.
        """
        return {
            "size": len(self.cache),
            "limit": self.limit,
            "usage_pct": (len(self.cache) / self.limit * 100) if self.limit > 0 else 0
        }
