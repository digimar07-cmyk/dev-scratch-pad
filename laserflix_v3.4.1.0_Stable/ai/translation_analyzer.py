"""
translation_analyzer.py — Análise de tradução de nomes PT-BR

GARANTIAS:
  1. Funciona com E sem Ollama (fallback sempre disponível)
  2. Retorna None apenas se nome já está em PT-BR
  3. Usa TRANSLATION_MAP (279 palavras) para fallback
  4. Análise em lote otimizada

INTEGRAÇÃO:
  - Chamado pelo menu "🌐 Traduzir Nomes (PT-BR)"
  - Salva resultado em database.projects[].name_pt
  - Usado por busca estendida, cards e modal

MODELO: Claude Sonnet 4.5
"""

import os
from typing import Optional, Dict, List
from utils.logging_setup import LOGGER


class TranslationAnalyzer:
    """
    Analisador de tradução EN→PT-BR para nomes de projetos.
    
    Estratégia:
      1. Tenta Ollama (se disponível) para tradução contextual
      2. Fallback com TRANSLATION_MAP (palavra por palavra)
      3. Retorna None se nome já é PT ou não mudou
    
    Uso:
        analyzer = TranslationAnalyzer(fallback_generator, ollama_client)
        result = analyzer.analyze_single("path/to/Nursery Mirror.zip")
        # result = {"name_pt": "Espelho de Quarto de Bebê", "method": "ollama"}
    """
    
    def __init__(self, fallback_generator, ollama_client=None):
        """
        Args:
            fallback_generator: Instância de FallbackGenerator
            ollama_client: Instância de OllamaClient (opcional)
        """
        self.fallback = fallback_generator
        self.ollama_client = ollama_client
        self.ollama_available = False
        self.logger = LOGGER
        
        # Detecta se Ollama está disponível
        if ollama_client:
            try:
                # Testa conexão com timeout curto
                models = ollama_client.list_models()
                self.ollama_available = len(models) > 0
                if self.ollama_available:
                    self.logger.info("TranslationAnalyzer: Ollama disponível para traduções")
            except Exception as e:
                self.logger.warning(f"TranslationAnalyzer: Ollama indisponível, usando fallback: {e}")
                self.ollama_available = False
    
    def analyze_single(self, project_path: str, raw_name: str) -> Dict[str, Optional[str]]:
        """
        Traduz um único nome de projeto.
        
        Args:
            project_path: Caminho do projeto (para logs)
            raw_name: Nome original do arquivo/pasta
        
        Returns:
            {
                "name_pt": str ou None (None = já está em PT),
                "method": "ollama" | "fallback" | "unchanged"
            }
        """
        # 1. Tenta Ollama (se disponível)
        if self.ollama_available:
            try:
                ollama_result = self._translate_with_ollama(raw_name)
                if ollama_result:
                    self.logger.info(f"Traduzido via Ollama: '{raw_name}' → '{ollama_result}'")
                    return {
                        "name_pt": ollama_result,
                        "method": "ollama"
                    }
            except Exception as e:
                self.logger.warning(f"Erro no Ollama, usando fallback: {e}")
        
        # 2. Fallback com TRANSLATION_MAP (SEMPRE funciona)
        fallback_result = self.fallback.translate_name(raw_name)
        
        if fallback_result:
            self.logger.info(f"Traduzido via Fallback: '{raw_name}' → '{fallback_result}'")
            return {
                "name_pt": fallback_result,
                "method": "fallback"
            }
        
        # 3. Sem tradução necessária (já é PT-BR ou não mudou)
        self.logger.debug(f"Tradução não necessária: '{raw_name}'")
        return {
            "name_pt": None,
            "method": "unchanged"
        }
    
    def analyze_batch(self, projects: List[Dict]) -> Dict[str, Dict]:
        """
        Traduz lote de projetos.
        
        Args:
            projects: Lista de dicts com {"path": str, "name": str, ...}
        
        Returns:
            {
                "path/to/project1": {"name_pt": "...", "method": "..."},
                "path/to/project2": {"name_pt": None, "method": "unchanged"},
                ...
            }
        """
        results = {}
        total = len(projects)
        
        self.logger.info(f"Iniciando tradução em lote de {total} projetos")
        
        for i, project in enumerate(projects, 1):
            path = project.get("path")
            raw_name = project.get("name", os.path.basename(path))
            
            # Traduz
            result = self.analyze_single(path, raw_name)
            results[path] = result
            
            # Log de progresso a cada 50 projetos
            if i % 50 == 0:
                self.logger.info(f"Progresso: {i}/{total} projetos traduzidos")
        
        # Estatísticas finais
        stats = self._calculate_stats(results)
        self.logger.info(
            f"Tradução concluída: {stats['translated']} traduzidos, "
            f"{stats['unchanged']} já em PT-BR, "
            f"{stats['ollama']} via IA, {stats['fallback']} via dicionário"
        )
        
        return results
    
    def _translate_with_ollama(self, raw_name: str) -> Optional[str]:
        """
        Traduz usando modelo Ollama.
        
        Args:
            raw_name: Nome original em inglês
        
        Returns:
            Tradução em PT-BR ou None se falhar
        """
        if not self.ollama_client:
            return None
        
        # Prompt otimizado para tradução contextual
        prompt = f"""Traduza o nome deste produto de corte a laser para PT-BR.

Nome original: {raw_name}

Regras:
- Tradução natural e fluente (não literal)
- Contexto: produtos artesanais de corte laser
- Se já estiver em PT-BR, retorne o mesmo texto
- APENAS a tradução, sem explicações ou aspas

Tradução:"""
        
        try:
            # Usa modelo de qualidade de texto configurado
            response = self.ollama_client.generate(
                prompt=prompt,
                model="text_quality",  # Definido em settings.py
                max_tokens=50,
                temperature=0.3  # Baixa para tradução consistente
            )
            
            translation = response.strip()
            
            # Valida se não retornou lixo
            if translation and len(translation) > 2 and translation.lower() != raw_name.lower():
                return translation
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao traduzir '{raw_name}' com Ollama: {e}")
            return None
    
    def _calculate_stats(self, results: Dict) -> Dict[str, int]:
        """Calcula estatísticas da tradução em lote."""
        stats = {
            "translated": 0,
            "unchanged": 0,
            "ollama": 0,
            "fallback": 0
        }
        
        for result in results.values():
            method = result.get("method", "unchanged")
            
            if method == "unchanged":
                stats["unchanged"] += 1
            else:
                stats["translated"] += 1
                stats[method] += 1
        
        return stats
