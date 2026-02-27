"""
LASERFLIX — Thumbnail Cache
Cache LRU de thumbnails com limite de 300 itens
"""

import os
from collections import OrderedDict
from PIL import Image, ImageTk
import logging

LOGGER = logging.getLogger("Laserflix")


class ThumbnailCache:
    """Cache LRU de thumbnails"""

    def __init__(self, cache_limit=300):
        self.cache = OrderedDict()
        self.cache_limit = cache_limit

    def get_thumbnail(self, project_path, file_analyzer):
        """Retorna thumbnail (220x200) do projeto"""
        if project_path in self.cache:
            self.cache.move_to_end(project_path)
            return self.cache[project_path]
        image_path = file_analyzer.find_first_image(project_path)
        if not image_path:
            return None
        try:
            with Image.open(image_path) as img:
                img.thumbnail((220, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.cache[project_path] = photo
                if len(self.cache) > self.cache_limit:
                    self.cache.popitem(last=False)
                return photo
        except Exception as e:
            LOGGER.warning(f"Falha ao criar thumbnail: {e}")
            return None
