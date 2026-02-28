# -*- coding: utf-8 -*-
"""
Modelos de dados
"""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Media:
    """Modelo base de mídia"""
    id: str
    title: str
    path: str
    duration: Optional[int] = None
    thumbnail: Optional[str] = None

@dataclass
class Movie(Media):
    """Modelo de filme"""
    year: Optional[int] = None
    genre: List[str] = None

@dataclass
class Episode(Media):
    """Modelo de episódio"""
    season: int = 1
    episode: int = 1
    series_id: str = ""

@dataclass
class Series:
    """Modelo de série"""
    id: str
    title: str
    episodes: List[Episode] = None
