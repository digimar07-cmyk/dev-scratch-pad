"""
LASERFLIX v3.0 — Testes de Caracterização
Documenta comportamento atual das funções puras da v7.4.0
sem tocar no código de produção (rede de segurança).

Objetivo: proteger lógica de domínio antes de extrair para módulos.
"""

import unittest
import sys
import os

# Adiciona o path da v740 para importar funções originárias
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Nota: Por enquanto, vamos criar stubs das funções que queremos testar.
# Na próxima etapa, importaremos da v740 real.

class TestExtractTagsFromName(unittest.TestCase):
    """Testa extração de tags a partir do nome do projeto"""
    
    def setUp(self):
        """Simulação temporária da função original"""
        import re
        
        def extract_tags_from_name(name):
            name_clean = name
            for ext in [".zip", ".rar", ".7z", ".svg", ".pdf", ".dxf"]:
                name_clean = name_clean.replace(ext, "")
            name_clean = re.sub(r"[-_]\d{5,}", "", name_clean)
            name_clean = name_clean.replace("-", " ").replace("_", " ")
            stop_words = {"file", "files", "project", "design", "laser", "cut", "svg",
                          "pdf", "vector", "bundle", "pack", "set", "collection"}
            words = [w for w in name_clean.split() if len(w) >= 2 and not w.isdigit() and w.lower() not in stop_words]
            tags = []
            if len(words) >= 2:
                phrase = " ".join(words[:4])
                if len(phrase) > 3:
                    tags.append(phrase.title())
            for w in words[:5]:
                if len(w) >= 3:
                    tags.append(w.capitalize())
            seen, unique = set(), []
            for t in tags:
                if t.lower() not in seen:
                    seen.add(t.lower())
                    unique.append(t)
            return unique[:5]
        
        self.extract_tags_from_name = extract_tags_from_name
    
    def test_simple_name(self):
        """Caso básico: nome limpo sem extensões"""
        result = self.extract_tags_from_name("Easter Bunny Frame")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("Easter Bunny Frame", result)
    
    def test_name_with_extensions(self):
        """Remove extensões de arquivo"""
        result = self.extract_tags_from_name("Christmas Tree.svg.zip")
        # Não deve conter extensões nas tags
        self.assertTrue(all(".svg" not in tag.lower() and ".zip" not in tag.lower() for tag in result))
    
    def test_name_with_codes(self):
        """Remove códigos numéricos longos"""
        result = self.extract_tags_from_name("Baby Name-123456.pdf")
        # Não deve conter códigos
        self.assertTrue(all("123456" not in tag for tag in result))
    
    def test_filters_stop_words(self):
        """Filtra stop words genéricas"""
        result = self.extract_tags_from_name("laser cut file design bundle")
        # Não deve conter stop words
        stop_words = {"laser", "cut", "file", "design", "bundle"}
        self.assertTrue(all(tag.lower() not in stop_words for tag in result))
    
    def test_max_five_tags(self):
        """Limita a 5 tags no máximo"""
        result = self.extract_tags_from_name("One Two Three Four Five Six Seven Eight")
        self.assertLessEqual(len(result), 5)


class TestFallbackCategories(unittest.TestCase):
    """Testa categorização automática por palavras-chave"""
    
    def setUp(self):
        """Simulação temporária da função original"""
        def fallback_categories(project_path, existing_categories):
            name = os.path.basename(project_path).lower()
            date_map = {
                "pascoa": "Páscoa", "easter": "Páscoa",
                "natal": "Natal", "christmas": "Natal",
                "mae": "Dia das Mães", "mother": "Dia das Mães",
                "pai": "Dia dos Pais", "father": "Dia dos Pais",
                "crianca": "Dia das Crianças", "children": "Dia das Crianças",
                "baby": "Chá de Bebê", "bebe": "Chá de Bebê",
                "wedding": "Casamento", "casamento": "Casamento",
                "birthday": "Aniversário", "aniversario": "Aniversário",
            }
            function_map = {
                "frame": "Porta-Retrato", "foto": "Porta-Retrato",
                "box": "Caixa Organizadora", "caixa": "Caixa Organizadora",
                "name": "Nome Decorativo", "nome": "Nome Decorativo",
                "sign": "Plaquinha Divertida", "placa": "Plaquinha Divertida",
                "quadro": "Quadro Decorativo", "painel": "Painel de Parede",
            }
            ambiente_map = {
                "nursery": "Quarto de Bebê", "baby": "Quarto de Bebê",
                "bedroom": "Quarto", "quarto": "Quarto",
                "kitchen": "Cozinha", "cozinha": "Cozinha",
                "living": "Sala", "sala": "Sala",
                "kids": "Quarto Infantil", "infantil": "Quarto Infantil",
            }
            result = list(existing_categories)
            date_cats = ["Páscoa", "Natal", "Dia das Mães", "Dia dos Pais", "Casamento", "Chá de Bebê", "Aniversário", "Dia das Crianças"]
            if not any(c in date_cats for c in result):
                for key, val in date_map.items():
                    if key in name:
                        result.insert(0, val)
                        break
                else:
                    result.insert(0, "Diversos")
            if len(result) < 2:
                for key, val in function_map.items():
                    if key in name:
                        result.append(val)
                        break
                else:
                    result.append("Diversos")
            if len(result) < 3:
                for key, val in ambiente_map.items():
                    if key in name:
                        result.append(val)
                        break
                else:
                    result.append("Diversos")
            return result
        
        self.fallback_categories = fallback_categories
    
    def test_easter_project(self):
        """Detecta projetos de Páscoa"""
        result = self.fallback_categories("/path/to/easter_bunny_frame", [])
        self.assertIn("Páscoa", result)
    
    def test_christmas_project(self):
        """Detecta projetos de Natal"""
        result = self.fallback_categories("/path/to/christmas_tree_ornament", [])
        self.assertIn("Natal", result)
    
    def test_frame_function(self):
        """Detecta função porta-retrato"""
        result = self.fallback_categories("/path/to/photo_frame", [])
        self.assertIn("Porta-Retrato", result)
    
    def test_baby_room_ambiente(self):
        """Detecta ambiente quarto de bebê"""
        result = self.fallback_categories("/path/to/nursery_decoration", [])
        self.assertIn("Quarto de Bebê", result)
    
    def test_always_three_categories(self):
        """Sempre retorna pelo menos 3 categorias"""
        result = self.fallback_categories("/path/to/unknown_project", [])
        self.assertGreaterEqual(len(result), 3)
    
    def test_preserves_existing(self):
        """Preserva categorias existentes"""
        result = self.fallback_categories("/path/to/project", ["Categoria Existente"])
        self.assertIn("Categoria Existente", result)


class TestGetOriginFromPath(unittest.TestCase):
    """Testa detecção de origem baseada no path"""
    
    def setUp(self):
        """Simulação temporária da função original"""
        def get_origin_from_path(project_path):
            try:
                parent_folder = os.path.basename(os.path.dirname(project_path))
                parent_upper = parent_folder.upper()
                if "CREATIVE" in parent_upper or "FABRICA" in parent_upper:
                    return "Creative Fabrica"
                elif "ETSY" in parent_upper:
                    return "Etsy"
                else:
                    return parent_folder
            except Exception:
                return "Diversos"
        
        self.get_origin_from_path = get_origin_from_path
    
    def test_creative_fabrica(self):
        """Detecta Creative Fabrica no path"""
        result = self.get_origin_from_path("/storage/CREATIVE_FABRICA_2024/project1")
        self.assertEqual(result, "Creative Fabrica")
    
    def test_etsy(self):
        """Detecta Etsy no path"""
        result = self.get_origin_from_path("/downloads/etsy_products/project2")
        self.assertEqual(result, "Etsy")
    
    def test_other_folder(self):
        """Retorna nome da pasta pai quando não é origem conhecida"""
        result = self.get_origin_from_path("/my_projects/custom_folder/project3")
        self.assertEqual(result, "custom_folder")
    
    def test_invalid_path_returns_empty(self):
        """Path vazio retorna string vazia (comportamento atual v740)"""
        result = self.get_origin_from_path("")
        # BUG DOCUMENTADO: v740 retorna "" em vez de "Diversos" para paths vazios
        # Será corrigido quando extrairmos para domain/
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
