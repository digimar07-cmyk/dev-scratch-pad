"""
conftest.py — fixtures compartilhados para os testes do Laserflix v7.4.0.

EVITA importar tkinter diretamente: a classe principal (LaserflixNetflix)
depende de tk.Tk(), então isolamos os métodos testáveis em uma subclasse
que substitui __init__ por um setup mínimo sem UI.
"""
from __future__ import annotations

import json
import os
import logging
from collections import OrderedDict

import pytest
import requests


# ---------------------------------------------------------------------------
# Stub mínimo de tkinter para ambientes sem display (CI, headless)
# ---------------------------------------------------------------------------
class _FakeRoot:
    """Substituto de tk.Tk() que não exige display."""
    def after(self, *a, **kw): pass
    def update_idletasks(self): pass
    def title(self, *a): pass
    def state(self, *a): pass
    def configure(self, **kw): pass
    def protocol(self, *a, **kw): pass
    def mainloop(self): pass


class _FakeStatusBar:
    def config(self, **kw): pass


# ---------------------------------------------------------------------------
# Wrapper de lógica sem UI
# ---------------------------------------------------------------------------
class LaserflixLogic:
    """
    Expõe apenas os métodos de lógica pura do LaserflixNetflix.
    Não cria nenhum widget tkinter — seguro para rodar em CI/headless.
    """

    def __init__(self, folders=None, database=None):
        from laserflix_v740_Ofline_Stable import OLLAMA_MODELS  # noqa: F401

        self.logger = logging.getLogger("LaserflixTest")
        self.root = _FakeRoot()
        self.status_bar = _FakeStatusBar()

        self.folders = folders or []
        self.database = database or {}
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.analyzing = False
        self.stop_analysis = False

        self.http_session = requests.Session()
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_retries = 1
        self.ollama_health_timeout = 1
        self._ollama_health_cache = {"ts": 0.0, "ok": None}

        self.active_models = dict(OLLAMA_MODELS)
        self.thumbnail_cache = OrderedDict()
        self.thumbnail_cache_limit = 300

        # Injeta os métodos de lógica da classe real
        self._bind_logic_methods()

    def _bind_logic_methods(self):
        """Liga os métodos de lógica pura da classe original a esta instância."""
        from laserflix_v740_Ofline_Stable import LaserflixNetflix
        _METHODS = [
            "extract_tags_from_name",
            "fallback_categories",
            "fallback_analysis",
            "generate_fallback_description",
            "analyze_project_structure",
            "get_filtered_projects",
            "get_origin_from_path",
            "save_json_atomic",
            "_image_quality_score",
            "_find_first_image_path",
            "_model_name",
            "_timeout",
            "_choose_text_role",
            "_ollama_is_available",
        ]
        for name in _METHODS:
            bound = getattr(LaserflixNetflix, name).__get__(self, self.__class__)
            setattr(self, name, bound)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def logic():
    """Instância reutilizável de LaserflixLogic (sem UI)."""
    return LaserflixLogic()


@pytest.fixture()
def tmp_project(tmp_path):
    """
    Pasta de projeto temporária com arquivos típicos:
      design.svg, print.pdf, preview.png, variantes/v2.svg
    """
    proj = tmp_path / "Porta-Retrato Familia Natal-00123"
    proj.mkdir()
    (proj / "design.svg").write_text("<svg/>", encoding="utf-8")
    (proj / "print.pdf").write_bytes(b"%PDF-1.4")
    (proj / "preview.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    sub = proj / "variantes"
    sub.mkdir()
    (sub / "v2.svg").write_text("<svg/>", encoding="utf-8")
    return str(proj)


@pytest.fixture()
def tmp_db(tmp_path):
    """Path de um arquivo JSON de banco de dados temporário e vazio."""
    db = tmp_path / "laserflix_database.json"
    db.write_text("{}", encoding="utf-8")
    return str(db)


@pytest.fixture()
def sample_database():
    """
    Banco de dados de exemplo com 4 projetos cobrindo
    favorito, feito, sem categoria, e analisado com descrição.
    """
    return {
        "/projetos/Porta-Retrato-Bebe": {
            "name": "Porta-Retrato-Bebe",
            "origin": "Etsy",
            "favorite": True,
            "done": False,
            "good": True,
            "bad": False,
            "categories": ["Chá de Bebê", "Porta-Retrato", "Quarto de Bebê"],
            "tags": ["Porta Retrato Bebe", "Porta", "Retrato", "Bebê", "personalizado"],
            "analyzed": True,
            "ai_description": "Porta Retrato Bebe\n\n🎨 Por Que Este Produto é Especial:\nUm porta-retrato encantador...",
        },
        "/projetos/Mandala-Natal": {
            "name": "Mandala-Natal",
            "origin": "Creative Fabrica",
            "favorite": False,
            "done": True,
            "good": False,
            "bad": False,
            "categories": ["Natal", "Mandala", "Sala"],
            "tags": ["Mandala Natal", "Mandala", "Natal", "decoração", "artesanal"],
            "analyzed": True,
            "ai_description": "",
        },
        "/projetos/Quadro-Sem-Categoria": {
            "name": "Quadro-Sem-Categoria",
            "origin": "Diversos",
            "favorite": False,
            "done": False,
            "good": False,
            "bad": True,
            "categories": [],
            "tags": [],
            "analyzed": False,
            "ai_description": "",
        },
        "/projetos/Luminaria-Led": {
            "name": "Luminaria-Led",
            "origin": "Etsy",
            "favorite": False,
            "done": False,
            "good": False,
            "bad": False,
            "categories": ["Aniversário", "Luminária", "Quarto"],
            "tags": ["Luminaria Led", "Luminaria", "Led", "presente", "artesanal"],
            "analyzed": True,
            "ai_description": "Luminaria Led\n\n🎨 Por Que Este Produto é Especial:\nUma luminária única...",
        },
    }


@pytest.fixture()
def logic_with_db(logic, sample_database):
    """logic fixture com banco de dados sample carregado."""
    logic.database = dict(sample_database)
    logic.current_filter = "all"
    logic.current_categories = []
    logic.current_tag = None
    logic.current_origin = "all"
    logic.search_query = ""
    return logic
