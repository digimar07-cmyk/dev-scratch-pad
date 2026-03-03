#!/usr/bin/env python3
"""
duplicate_detector.py — Detecta e gerencia produtos duplicados.

DETECÇÃO INTELIGENTE:
  - Compara nomes normalizados (case-insensitive, sem espaços extras)
  - Detecta duplicatas entre:
    * Produtos já no banco
    * Produtos sendo importados
    * Produtos em importações diferentes

OPÇÕES DE RESOLUÇÃO:
  - SKIP: Ignora novos (mantém existente)
  - REPLACE: Substitui existente por novo
  - MERGE: Mescla informações (prioriza mais completo)
  - ASK: Pergunta ao usuário

USO:
    detector = DuplicateDetector(database)
    
    # Verifica duplicatas antes de importar
    duplicates = detector.find_duplicates(new_products, existing_products)
    
    if duplicates:
        # Mostra dialog para usuário decidir
        resolution = show_duplicate_dialog(duplicates)
        products_to_import = detector.resolve_duplicates(duplicates, resolution)
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from utils.logging_setup import LOGGER


class DuplicateDetector:
    """
    Detecta e resolve produtos duplicados.
    
    Normaliza nomes de produtos para comparação precisa,
    detecta duplicatas e oferece opções de resolução.
    """

    def __init__(self, database=None):
        """
        Args:
            database: Instância do banco de dados (opcional)
        """
        self.database = database
        self.logger = LOGGER

    # ================================================================
    # NORMALIZAÇÃO DE NOMES
    # ================================================================

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normaliza nome de produto para comparação.
        
        Remove:
        - Espaços extras
        - Caracteres especiais
        - Acentos
        - Case sensitivity
        
        Args:
            name: Nome original
        
        Returns:
            Nome normalizado
        
        Exemplo:
            "  Cabeça de Leão  " -> "cabeca-de-leao"
            "DRAGAO 3D" -> "dragao-3d"
        """
        if not name:
            return ""
        
        # Remove acentos
        replacements = {
            'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        
        normalized = name.lower()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove caracteres especiais (exceto alfanuméricos e espaços)
        normalized = re.sub(r'[^a-z0-9\s-]', '', normalized)
        
        # Substitui múltiplos espaços/hifens por um único hífen
        normalized = re.sub(r'[\s-]+', '-', normalized)
        
        # Remove hifens do início e fim
        normalized = normalized.strip('-')
        
        return normalized

    # ================================================================
    # DETECÇÃO DE DUPLICATAS
    # ================================================================

    def find_duplicates(
        self,
        new_products: List[Dict],
        existing_products: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Encontra produtos duplicados.
        
        Compara:
        1. Novos produtos entre si
        2. Novos produtos vs existentes no banco
        3. Novos produtos vs lista de existentes fornecida
        
        Args:
            new_products: Lista de produtos a importar
            existing_products: Lista de produtos já existentes (opcional)
        
        Returns:
            Lista de duplicatas encontradas:
            [
                {
                    'name': 'Produto X',
                    'normalized_name': 'produto-x',
                    'new': {...},  # Produto novo
                    'existing': {...},  # Produto existente
                    'conflict_type': 'database' | 'import_batch' | 'cross_import'
                },
                ...
            ]
        """
        duplicates = []
        
        # Mapa: nome_normalizado -> produto
        existing_map = {}
        
        # 1. Carrega produtos existentes do banco
        if self.database:
            for path, project in self.database.items():
                name = project.get('name', '')
                if name:
                    norm_name = self.normalize_name(name)
                    existing_map[norm_name] = {
                        'source': 'database',
                        'data': project
                    }
        
        # 2. Adiciona produtos da lista fornecida
        if existing_products:
            for product in existing_products:
                name = product.get('name', '')
                if name:
                    norm_name = self.normalize_name(name)
                    if norm_name not in existing_map:
                        existing_map[norm_name] = {
                            'source': 'existing_list',
                            'data': product
                        }
        
        # 3. Verifica novos produtos
        new_map = {}
        for product in new_products:
            name = product.get('name', '')
            if not name:
                continue
            
            norm_name = self.normalize_name(name)
            
            # Duplicata com existente?
            if norm_name in existing_map:
                duplicates.append({
                    'name': name,
                    'normalized_name': norm_name,
                    'new': product,
                    'existing': existing_map[norm_name]['data'],
                    'conflict_type': existing_map[norm_name]['source']
                })
            
            # Duplicata entre novos?
            elif norm_name in new_map:
                duplicates.append({
                    'name': name,
                    'normalized_name': norm_name,
                    'new': product,
                    'existing': new_map[norm_name],
                    'conflict_type': 'import_batch'
                })
            
            else:
                new_map[norm_name] = product
        
        if duplicates:
            self.logger.warning(
                f"Encontradas {len(duplicates)} duplicatas: "
                f"{[d['name'] for d in duplicates[:5]]}..."
            )
        
        return duplicates

    def get_existing_names(self) -> Set[str]:
        """
        Obtém todos os nomes normalizados já existentes no banco.
        
        Returns:
            Set de nomes normalizados
        """
        names = set()
        
        if self.database:
            for path, project in self.database.items():
                name = project.get('name', '')
                if name:
                    norm_name = self.normalize_name(name)
                    names.add(norm_name)
        
        return names

    # ================================================================
    # RESOLUÇÃO DE DUPLICATAS
    # ================================================================

    def resolve_duplicates(
        self,
        duplicates: List[Dict],
        strategy: str = 'skip',
        user_choices: Optional[Dict] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Resolve duplicatas baseado na estratégia escolhida.
        
        Args:
            duplicates: Lista de duplicatas (retorno de find_duplicates)
            strategy: 'skip', 'replace', 'merge', ou 'ask'
            user_choices: Dict {normalized_name: 'skip'|'replace'|'merge'}
        
        Returns:
            (products_to_import, products_to_skip)
        """
        to_import = []
        to_skip = []
        
        for dup in duplicates:
            norm_name = dup['normalized_name']
            
            # Usuário decidiu?
            if user_choices and norm_name in user_choices:
                choice = user_choices[norm_name]
            else:
                choice = strategy
            
            if choice == 'skip':
                # Ignora novo, mantém existente
                to_skip.append(dup['new'])
                self.logger.info(f"SKIP: {dup['name']} (mantido existente)")
            
            elif choice == 'replace':
                # Substitui existente por novo
                to_import.append(dup['new'])
                self.logger.info(f"REPLACE: {dup['name']} (substituindo)")
            
            elif choice == 'merge':
                # Mescla informações
                merged = self._merge_products(dup['existing'], dup['new'])
                to_import.append(merged)
                self.logger.info(f"MERGE: {dup['name']} (mesclado)")
            
            else:
                # Padrão: skip
                to_skip.append(dup['new'])
        
        return to_import, to_skip

    def _merge_products(self, existing: Dict, new: Dict) -> Dict:
        """
        Mescla informações de dois produtos.
        
        Prioriza:
        - Dados mais completos
        - Imagens do novo (se existente não tiver)
        - Mantém metadados do existente (favorito, done, etc)
        
        Args:
            existing: Produto existente
            new: Produto novo
        
        Returns:
            Produto mesclado
        """
        merged = existing.copy()
        
        # Atualiza path para novo (se diferente)
        if new.get('path') and new['path'] != existing.get('path'):
            # Adiciona path antigo como referência
            if 'alternative_paths' not in merged:
                merged['alternative_paths'] = []
            merged['alternative_paths'].append(existing.get('path'))
            merged['path'] = new['path']
        
        # Atualiza cover_image se novo tiver e existente não
        if new.get('cover_image') and not existing.get('cover_image'):
            merged['cover_image'] = new['cover_image']
        
        # Mescla imagens (sem duplicar)
        existing_images = set(existing.get('images', []))
        new_images = set(new.get('images', []))
        merged['images'] = list(existing_images | new_images)
        
        # Adiciona nota sobre mesclagem
        merge_note = f"Mesclado com pasta: {new.get('path', 'desconhecida')}"
        if 'notes' in merged:
            merged['notes'] += f"\n{merge_note}"
        else:
            merged['notes'] = merge_note
        
        return merged

    # ================================================================
    # FILTRO DE IMPORTAÇÃO
    # ================================================================

    def filter_new_products(
        self,
        products: List[Dict],
        auto_skip_duplicates: bool = False
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Filtra produtos antes de importar.
        
        Args:
            products: Lista de produtos a verificar
            auto_skip_duplicates: Se True, pula duplicatas automaticamente
        
        Returns:
            (novos, duplicados, produtos_duplicados_info)
        """
        existing_names = self.get_existing_names()
        
        new = []
        duplicates = []
        dup_info = []
        
        for product in products:
            name = product.get('name', '')
            if not name:
                continue
            
            norm_name = self.normalize_name(name)
            
            if norm_name in existing_names:
                duplicates.append(product)
                dup_info.append({
                    'name': name,
                    'normalized_name': norm_name,
                    'product': product
                })
            else:
                new.append(product)
        
        if duplicates:
            msg = f"Encontradas {len(duplicates)} duplicatas"
            if auto_skip_duplicates:
                self.logger.info(f"{msg} - pulando automaticamente")
            else:
                self.logger.warning(f"{msg} - requer ação do usuário")
        
        return new, duplicates, dup_info


# ================================================================
# FUNÇÕES UTILITÁRIAS
# ================================================================

def are_duplicates(name1: str, name2: str) -> bool:
    """
    Verifica se dois nomes são duplicatas.
    
    Args:
        name1: Primeiro nome
        name2: Segundo nome
    
    Returns:
        True se forem duplicatas
    
    Exemplo:
        >>> are_duplicates("Cabeça de Leão", "cabeca de leao")
        True
        >>> are_duplicates("Dragão 3D", "Dragao-3D")
        True
    """
    norm1 = DuplicateDetector.normalize_name(name1)
    norm2 = DuplicateDetector.normalize_name(name2)
    return norm1 == norm2


def group_duplicates(products: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Agrupa produtos por nome normalizado.
    
    Args:
        products: Lista de produtos
    
    Returns:
        Dict {nome_normalizado: [produtos_com_mesmo_nome]}
    
    Exemplo:
        >>> products = [
        ...     {'name': 'Dragão', 'path': '/a/dragao'},
        ...     {'name': 'dragao', 'path': '/b/dragao'},
        ...     {'name': 'Leão', 'path': '/a/leao'}
        ... ]
        >>> groups = group_duplicates(products)
        >>> len(groups['dragao'])
        2
    """
    groups = {}
    
    for product in products:
        name = product.get('name', '')
        if not name:
            continue
        
        norm_name = DuplicateDetector.normalize_name(name)
        
        if norm_name not in groups:
            groups[norm_name] = []
        
        groups[norm_name].append(product)
    
    # Retorna apenas grupos com duplicatas
    return {k: v for k, v in groups.items() if len(v) > 1}


# ================================================================
# TESTE
# ================================================================
if __name__ == '__main__':
    # Teste de normalização
    print("=== TESTE DE NORMALIZAÇÃO ===")
    test_names = [
        "Cabeça de Leão",
        "cabeca de leao",
        "  DRAGÃO 3D  ",
        "dragao-3d",
        "Flor de Lótus!!!",
        "flor_de_lotus"
    ]
    
    for name in test_names:
        normalized = DuplicateDetector.normalize_name(name)
        print(f"{name:30} -> {normalized}")
    
    # Teste de duplicatas
    print("\n=== TESTE DE DUPLICATAS ===")
    products = [
        {'name': 'Dragão 3D', 'path': '/pasta1/dragao'},
        {'name': 'dragao 3d', 'path': '/pasta2/dragao'},
        {'name': 'Leão', 'path': '/pasta1/leao'},
        {'name': 'Tigre', 'path': '/pasta1/tigre'}
    ]
    
    detector = DuplicateDetector()
    duplicates = detector.find_duplicates(products)
    
    print(f"Encontradas {len(duplicates)} duplicatas:")
    for dup in duplicates:
        print(f"  - {dup['name']} ({dup['conflict_type']})")
