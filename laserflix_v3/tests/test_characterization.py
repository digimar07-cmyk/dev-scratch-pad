"""
LASERFLIX v3.0 — Testes de Caracterização
Documenta comportamento atual das funções puras da v7.4.0
sem tocar no código de produção (rede de segurança).

Objetivo: proteger lógica de domínio antes de extrair para módulos.
"""

import unittest
import sys
import os

# Adiciona o path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Agora importa do módulo de domínio real (não mais stubs!)
from domain.projects import extract_tags_from_name, fallback_categories, get_origin_from_path


class TestExtractTagsFromName(unittest.TestCase):
    """Testa extração de tags a partir do nome do projeto"""
    
    def test_simple_name(self):
        """Caso básico: nome limpo sem extensões"""
        result = extract_tags_from_name("Easter Bunny Frame")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("Easter Bunny Frame", result)
    
    def test_name_with_extensions(self):
        """Remove extensões de arquivo"""
        result = extract_tags_from_name("Christmas Tree.svg.zip")
        # Não deve conter extensões nas tags
        self.assertTrue(all(".svg" not in tag.lower() and ".zip" not in tag.lower() for tag in result))
    
    def test_name_with_codes(self):
        """Remove códigos numéricos longos"""
        result = extract_tags_from_name("Baby Name-123456.pdf")
        # Não deve conter códigos
        self.assertTrue(all("123456" not in tag for tag in result))
    
    def test_filters_stop_words(self):
        """Filtra stop words genéricas"""
        result = extract_tags_from_name("laser cut file design bundle")
        # Não deve conter stop words
        stop_words = {"laser", "cut", "file", "design", "bundle"}
        self.assertTrue(all(tag.lower() not in stop_words for tag in result))
    
    def test_max_five_tags(self):
        """Limita a 5 tags no máximo"""
        result = extract_tags_from_name("One Two Three Four Five Six Seven Eight")
        self.assertLessEqual(len(result), 5)


class TestFallbackCategories(unittest.TestCase):
    """Testa categorização automática por palavras-chave"""
    
    def test_easter_project(self):
        """Detecta projetos de Páscoa"""
        result = fallback_categories("/path/to/easter_bunny_frame", [])
        self.assertIn("Páscoa", result)
    
    def test_christmas_project(self):
        """Detecta projetos de Natal"""
        result = fallback_categories("/path/to/christmas_tree_ornament", [])
        self.assertIn("Natal", result)
    
    def test_frame_function(self):
        """Detecta função porta-retrato"""
        result = fallback_categories("/path/to/photo_frame", [])
        self.assertIn("Porta-Retrato", result)
    
    def test_baby_room_ambiente(self):
        """Detecta ambiente quarto de bebê"""
        result = fallback_categories("/path/to/nursery_decoration", [])
        self.assertIn("Quarto de Bebê", result)
    
    def test_always_three_categories(self):
        """Sempre retorna pelo menos 3 categorias"""
        result = fallback_categories("/path/to/unknown_project", [])
        self.assertGreaterEqual(len(result), 3)
    
    def test_preserves_existing(self):
        """Preserva categorias existentes"""
        result = fallback_categories("/path/to/project", ["Categoria Existente"])
        self.assertIn("Categoria Existente", result)


class TestGetOriginFromPath(unittest.TestCase):
    """Testa detecção de origem baseada no path"""
    
    def test_creative_fabrica(self):
        """Detecta Creative Fabrica no path"""
        result = get_origin_from_path("/storage/CREATIVE_FABRICA_2024/project1")
        self.assertEqual(result, "Creative Fabrica")
    
    def test_etsy(self):
        """Detecta Etsy no path"""
        result = get_origin_from_path("/downloads/etsy_products/project2")
        self.assertEqual(result, "Etsy")
    
    def test_other_folder(self):
        """Retorna nome da pasta pai quando não é origem conhecida"""
        result = get_origin_from_path("/my_projects/custom_folder/project3")
        self.assertEqual(result, "custom_folder")
    
    def test_invalid_path_returns_empty(self):
        """Path vazio retorna string vazia (comportamento atual v740)"""
        result = get_origin_from_path("")
        # BUG DOCUMENTADO: v740 retorna "" em vez de "Diversos" para paths vazios
        # Será corrigido quando extrairmos para domain/
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
