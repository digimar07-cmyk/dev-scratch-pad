"""Image processing service with caching and quality checks."""
import os
import io
import base64
import logging
from collections import OrderedDict
from typing import Optional, Dict, Any
from PIL import Image, ImageTk, ImageStat

logger = logging.getLogger("Laserflix.Image")


class ImageService:
    """Manages image operations with LRU caching."""
    
    def __init__(self, cache_limit: int = 300):
        self.cache_limit = cache_limit
        self.thumbnail_cache: OrderedDict = OrderedDict()
    
    def get_thumbnail(self, image_path: str, size: tuple = (220, 200)) -> Optional[ImageTk.PhotoImage]:
        """Get thumbnail with LRU caching."""
        if not os.path.exists(image_path):
            return None
        
        try:
            mtime = os.path.getmtime(image_path)
        except Exception:
            return None
        
        # Check cache
        cached = self.thumbnail_cache.get(image_path)
        if cached:
            cached_mtime, cached_photo = cached
            if cached_mtime == mtime:
                # Move to end (LRU)
                self.thumbnail_cache.move_to_end(image_path)
                return cached_photo
        
        # Generate new thumbnail
        try:
            photo = self._load_thumbnail(image_path, size)
            self.thumbnail_cache[image_path] = (mtime, photo)
            self.thumbnail_cache.move_to_end(image_path)
            
            # Evict old entries
            while len(self.thumbnail_cache) > self.cache_limit:
                self.thumbnail_cache.popitem(last=False)
            
            return photo
        except Exception as e:
            logger.error(f"Failed to generate thumbnail for {image_path}: {e}")
            return None
    
    def _load_thumbnail(self, image_path: str, size: tuple) -> ImageTk.PhotoImage:
        """Load and resize image to thumbnail."""
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    
    def get_hero_image(self, image_path: str, max_width: int = 800) -> Optional[ImageTk.PhotoImage]:
        """Load hero image with size constraint."""
        try:
            img = Image.open(image_path)
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"Failed to load hero image {image_path}: {e}")
            return None
    
    def assess_image_quality(self, image_path: str) -> Dict[str, Any]:
        """
        Assess image quality for vision analysis.
        
        Returns dict with:
        - brightness: average L channel value (0-255)
        - saturation: average S channel value (0-255)
        - white_pct: estimated percentage of white/blank background
        - use_vision: whether image is suitable for AI vision analysis
        
        Rejection criteria (ambiguous for vision):
        - brightness > 210 (overexposed/white background)
        - saturation < 25 (near-monochrome)
        - white_pct > 50% (mockup with dominant white background)
        """
        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                w, h = img_rgb.size
                
                # Analyze central area (remove watermarked borders)
                box = (int(w * 0.05), int(h * 0.10), int(w * 0.75), int(h * 0.90))
                center = img_rgb.crop(box)
                
                # Brightness (L channel)
                gray = center.convert("L")
                stat_g = ImageStat.Stat(gray)
                brightness = stat_g.mean[0]
                
                # Saturation (S channel from HSV)
                hsv = center.convert("HSV")
                stat_s = ImageStat.Stat(hsv)
                saturation = stat_s.mean[1]
                
                # White percentage approximation
                white_pct = (brightness / 255.0) * max(0, 1.0 - (stat_g.stddev[0] / 80.0))
                white_pct_normalized = white_pct * 100
                
                # Decision gate
                use_vision = not (
                    brightness > 210 or
                    saturation < 25 or
                    white_pct_normalized > 50
                )
                
                logger.info(
                    f"📊 Quality: brightness={brightness:.1f} sat={saturation:.1f} "
                    f"white~{white_pct_normalized:.1f}% → vision={use_vision}"
                )
                
                return {
                    "brightness": brightness,
                    "saturation": saturation,
                    "white_pct": white_pct_normalized,
                    "use_vision": use_vision,
                }
        except Exception as e:
            logger.warning(f"Quality assessment failed for {image_path}: {e}")
            return {
                "brightness": 0,
                "saturation": 100,
                "white_pct": 0,
                "use_vision": True
            }
    
    def prepare_image_for_vision(self, image_path: str, max_size: int = 512) -> Optional[str]:
        """
        Prepare image for vision API (resize + base64 encode).
        Returns base64 string or None if failed.
        """
        try:
            with Image.open(image_path) as img:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                return img_b64
        except Exception as e:
            logger.error(f"Failed to prepare image for vision: {e}")
            return None
    
    def clear_cache(self):
        """Clear thumbnail cache."""
        self.thumbnail_cache.clear()
        logger.info("Thumbnail cache cleared")
