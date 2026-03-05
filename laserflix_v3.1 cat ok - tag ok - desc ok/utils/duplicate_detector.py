"""
duplicate_detector.py — Detecta e gerencia produtos duplicados.
"""

from typing import List, Dict, Set, Tuple, Optional
from utils.logging_setup import LOGGER
from utils.text_utils import normalize_project_name


class DuplicateDetector:
    def __init__(self, database=None):
        self.database = database
        self.logger = LOGGER

    def find_duplicates(
        self,
        new_products: List[Dict],
        existing_products: Optional[List[Dict]] = None
    ) -> List[Dict]:
        duplicates = []
        existing_map = {}

        if self.database:
            for path, project in self.database.items():
                name = project.get('name', '')
                if name:
                    norm_name = normalize_project_name(name)
                    existing_map[norm_name] = {'source': 'database', 'data': project}

        if existing_products:
            for product in existing_products:
                name = product.get('name', '')
                if name:
                    norm_name = normalize_project_name(name)
                    if norm_name not in existing_map:
                        existing_map[norm_name] = {'source': 'existing_list', 'data': product}

        new_map = {}
        for product in new_products:
            name = product.get('name', '')
            if not name:
                continue
            norm_name = normalize_project_name(name)

            if norm_name in existing_map:
                duplicates.append({
                    'name': name,
                    'normalized_name': norm_name,
                    'new': product,
                    'existing': existing_map[norm_name]['data'],
                    'conflict_type': existing_map[norm_name]['source']
                })
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
        names = set()
        if self.database:
            for path, project in self.database.items():
                name = project.get('name', '')
                if name:
                    names.add(normalize_project_name(name))
        return names

    def resolve_duplicates(
        self,
        duplicates: List[Dict],
        strategy: str = 'skip',
        user_choices: Optional[Dict] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        to_import = []
        to_skip = []

        for dup in duplicates:
            norm_name = dup['normalized_name']
            choice = user_choices.get(norm_name, strategy) if user_choices else strategy

            if choice == 'skip':
                to_skip.append(dup['new'])
                self.logger.info("SKIP: %s", dup['name'])
            elif choice == 'replace':
                to_import.append(dup['new'])
                self.logger.info("REPLACE: %s", dup['name'])
            elif choice == 'merge':
                merged = self._merge_products(dup['existing'], dup['new'])
                to_import.append(merged)
                self.logger.info("MERGE: %s", dup['name'])
            else:
                to_skip.append(dup['new'])

        return to_import, to_skip

    def _merge_products(self, existing: Dict, new: Dict) -> Dict:
        merged = existing.copy()
        if new.get('path') and new['path'] != existing.get('path'):
            if 'alternative_paths' not in merged:
                merged['alternative_paths'] = []
            merged['alternative_paths'].append(existing.get('path'))
            merged['path'] = new['path']
        if new.get('cover_image') and not existing.get('cover_image'):
            merged['cover_image'] = new['cover_image']
        existing_images = set(existing.get('images', []))
        new_images = set(new.get('images', []))
        merged['images'] = list(existing_images | new_images)
        merge_note = f"Mesclado com pasta: {new.get('path', 'desconhecida')}"
        merged['notes'] = merged.get('notes', '') + ("\n" if merged.get('notes') else '') + merge_note
        return merged

    def filter_new_products(
        self,
        products: List[Dict],
        auto_skip_duplicates: bool = False
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
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
                dup_info.append({'name': name, 'normalized_name': norm_name, 'product': product})
            else:
                new.append(product)

        return new, duplicates, dup_info
