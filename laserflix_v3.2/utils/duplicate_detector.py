#!/usr/bin/env python3
"""
duplicate_detector.py — Detecta e gerencia produtos duplicados.

DETECÇÃO INTELIGENTE:
  - Compara nomes normalizados via normalize_project_name() de text_utils
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

from typing import List, Dict, Set, Tuple, Optional
from utils.logging_setup import LOGGER
from utils.text_utils import normalize_project_name


class DuplicateDetector:
    """
    Detecta e resolve produtos duplicados.

    Usa normalize_project_name() de text_utils como única fonte
    de verdade para normalização — baseada em unicodedata (cobertura
    completa de acentos, não apenas os 12 do dicionário manual anterior).
    """

    def __init__(self, database=None):
        """
        Args:
            database: Instância do banco de dados (opcional)
        """
        self.database = database
        self.logger = LOGGER

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
                    'normalized_name': 'produto x',
                    'new': {...},
                    'existing': {...},
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
                    norm_name = normalize_project_name(name)
                    existing_map[norm_name] = {
                        'source': 'database',
                        'data': project
                    }

        # 2. Adiciona produtos da lista fornecida
        if existing_products:
            for product in existing_products:
                name = product.get('name', '')
                if name:
                    norm_name = normalize_project_name(name)
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

            norm_name = normalize_project_name(name)

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
                "Encontradas %d duplicatas: %s...",
                len(duplicates),
                [d['name'] for d in duplicates[:5]]
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
                    names.add(normalize_project_name(name))

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
                to_skip.append(dup['new'])
                self.logger.info("SKIP: %s (mantido existente)", dup['name'])

            elif choice == 'replace':
                to_import.append(dup['new'])
                self.logger.info("REPLACE: %s (substituindo)", dup['name'])

            elif choice == 'merge':
                merged = self._merge_products(dup['existing'], dup['new'])
                to_import.append(merged)
                self.logger.info("MERGE: %s (mesclado)", dup['name'])

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
        """
        merged = existing.copy()

        # Atualiza path para novo (se diferente)
        if new.get('path') and new['path'] != existing.get('path'):
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

            norm_name = normalize_project_name(name)

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
                self.logger.info("%s - pulando automaticamente", msg)
            else:
                self.logger.warning("%s - requer ação do usuário", msg)

        return new, duplicates, dup_info
