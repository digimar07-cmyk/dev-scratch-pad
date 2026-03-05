"""
ai/translator.py — Tradutor EN→PT-BR com fallback inteligente.
Kent Beck: Dictionary first. Rules second. AI if available. Always works.
"""
import re
from typing import Optional
from ai.translation_dictionary import (
    FULL_DICTIONARY,
    COMPOUND_PATTERNS,
    COMMON_NOUNS,
)
from utils.logging_setup import LOGGER


class Translator:
    """
    Tradutor DUAL:
    - SEM Ollama: Dicionário + Regras (sempre funciona)
    - COM Ollama: Dicionário + Regras + IA (melhor qualidade)
    """
    
    def __init__(self, ollama_client=None):
        self.ollama = ollama_client
        self.logger = LOGGER
        self.cache = {}
        self.use_ai = ollama_client is not None
        
        mode = "COM Ollama" if self.use_ai else "SEM Ollama (apenas dicionário)"
        self.logger.info(f"✅ Tradutor inicializado {mode}")
    
    def translate_project_name(self, english_name: str) -> str:
        """
        Traduz nome de projeto.
        
        Fluxo:
        1. Normaliza
        2. Cache
        3. Dicionário direto
        4. Regras compostas
        5. IA (se disponível)
        6. Fallback: capitaliza original
        """
        if not english_name or not english_name.strip():
            return ""
        
        clean_name = self._normalize_name(english_name)
        
        # Cache
        if clean_name in self.cache:
            self.logger.debug(f"💾 Cache: {clean_name} → {self.cache[clean_name]}")
            return self.cache[clean_name]
        
        # Estratégia 1: Dicionário direto
        dict_result = self._dictionary_translate(clean_name)
        if dict_result:
            self.logger.info(f"📖 Dicionário: {clean_name} → {dict_result}")
            self.cache[clean_name] = dict_result
            return dict_result
        
        # Estratégia 2: Regras compostas (SEM IA)
        rules_result = self._rules_translate(clean_name)
        if rules_result:
            self.logger.info(f"📐 Regras: {clean_name} → {rules_result}")
            self.cache[clean_name] = rules_result
            return rules_result
        
        # Estratégia 3: IA (SE DISPONÍVEL)
        if self.use_ai:
            ai_result = self._ai_translate(clean_name)
            if ai_result and ai_result != clean_name:
                self.logger.info(f"🤖 IA: {clean_name} → {ai_result}")
                self.cache[clean_name] = ai_result
                return ai_result
        
        # Fallback: Capitaliza original
        fallback = self._capitalize(clean_name)
        self.logger.warning(f"⚠️ Fallback: {clean_name} → {fallback}")
        self.cache[clean_name] = fallback
        return fallback
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ESTRATÉGIA 1: DICIONÁRIO DIRETO
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _dictionary_translate(self, text: str) -> Optional[str]:
        """Traduz palavra por palavra. Retorna None se falhar."""
        words = text.lower().split()
        translated = []
        
        for word in words:
            if word in FULL_DICTIONARY:
                trans = FULL_DICTIONARY[word]
                if trans:  # Ignora conectores vazios
                    translated.append(trans)
            else:
                return None  # Palavra desconhecida
        
        if not translated:
            return None
        
        result = ' '.join(translated)
        return self._capitalize(result)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ESTRATÉGIA 2: REGRAS COMPOSTAS (SEM IA)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _rules_translate(self, text: str) -> Optional[str]:
        """Aplica regras de tradução compostas."""
        text_lower = text.lower()
        
        # Tenta cada padrão
        for pattern, replacement_func in COMPOUND_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    result = replacement_func(match)
                    return self._capitalize(result)
                except Exception as e:
                    self.logger.debug(f"Erro em padrão {pattern}: {e}")
                    continue
        
        # Fallback: melhor esforço
        return self._best_effort_translate(text)
    
    def _best_effort_translate(self, text: str) -> Optional[str]:
        """Traduz o máximo possível, mantém palavras desconhecidas."""
        words = text.lower().split()
        translated = []
        unknown_count = 0
        
        for word in words:
            if word in FULL_DICTIONARY:
                trans = FULL_DICTIONARY[word]
                if trans:
                    translated.append(trans)
            else:
                translated.append(word)
                unknown_count += 1
        
        # Se > 50% desconhecido, falha
        if unknown_count > len(words) / 2:
            return None
        
        result = ' '.join(translated)
        result = self._reorder_adjective_noun(result)
        return self._capitalize(result)
    
    def _reorder_adjective_noun(self, text: str) -> str:
        """Reordena ADJ+NOUN → NOUN+ADJ (português)."""
        nouns_pt = [
            'porta', 'janela', 'caixa', 'painel', 'moldura', 'suporte',
            'bandeja', 'luminária', 'mesa', 'cadeira', 'prateleira',
        ]
        
        words = text.split()
        if len(words) == 2:
            if words[1] in nouns_pt:
                return text  # Já correto
            elif words[0] in nouns_pt:
                return f"{words[1]} {words[0]}"  # Inverte
        
        return text
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ESTRATÉGIA 3: IA (OPCIONAL)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _ai_translate(self, text: str) -> str:
        """Traduz usando IA (SE DISPONÍVEL)."""
        if not self.ollama:
            return text
        
        prompt = f"""Traduza do inglês para português brasileiro de forma NATURAL:

"{text}"

Contexto: design, corte a laser, arquitetura, produtos.

Regras:
1. Use termos técnicos corretos
2. Ordem natural do português (ex: "decorative door" = "porta decorativa")
3. Mantenha siglas/códigos originais
4. RESPONDA APENAS COM A TRADUÇÃO, SEM EXPLICAÇÕES

Tradução:"""

        try:
            response = self.ollama.generate(
                prompt=prompt,
                model="gemma2:2b",
                temperature=0.3,
                max_tokens=50,
            )
            
            translated = response.strip().strip('"').strip("'")
            return self._capitalize(translated)
        
        except Exception as e:
            self.logger.error(f"❌ Erro IA: {e}")
            return text
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITÁRIOS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _normalize_name(self, name: str) -> str:
        """Remove extensões, limpa formatação."""
        name = re.sub(r'\.(ai|svg|pdf|dxf|dwg)$', '', name, flags=re.IGNORECASE)
        name = name.replace('_', ' ').replace('-', ' ')
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def _capitalize(self, text: str) -> str:
        """Capitaliza corretamente em português."""
        lowercase_words = {
            'de', 'da', 'do', 'dos', 'das', 'em', 'para',
            'com', 'a', 'o', 'e', 'ou', 'sem'
        }
        
        words = text.split()
        capitalized = []
        
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in lowercase_words:
                capitalized.append(word.capitalize())
            else:
                capitalized.append(word.lower())
        
        return ' '.join(capitalized)
