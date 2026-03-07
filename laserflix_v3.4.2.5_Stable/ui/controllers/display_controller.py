"""
ui/controllers/display_controller.py — Controller de Exibição (Fase 2)

Responsabilidades:
- Gerenciar estado de filtros (active_filters)
- Gerenciar estado de busca (search_query)
- Gerenciar estado de ordenação (current_sort)
- Gerenciar estado de paginação (current_page, items_per_page)
- Aplicar filtros ao database
- Aplicar ordenação aos projetos
- Paginar resultados
- Notificar UI sobre mudanças (callbacks)

EXTRAÍDO DE: main_window.py (~300 linhas)
TAMANHO: ~280 linhas
LIMITE: 300 linhas
STATUS: ✅ OK
"""
from typing import Any, Callable, Optional
from utils.logging_setup import LOGGER
from utils.name_translator import search_bilingual


class DisplayController:
    """
    Controller de exibição - gerencia filtros, ordenação e paginação.
    
    Princípio de Responsabilidade Única:
    - FILTROS: Gerencia active_filters, aplica ao database
    - ORDENAÇÃO: Aplica sorting aos resultados
    - PAGINAÇÃO: Gerencia current_page, items_per_page
    - NOTIFICAÇÃO: Dispara callbacks quando estado muda
    """
    
    def __init__(self, database: dict, collections_manager=None, items_per_page: int = 36):
        self.database = database
        self.collections_manager = collections_manager
        self.logger = LOGGER
        
        # Estado de filtros
        self.current_filter = "all"  # all/favorite/done/good/bad
        self.current_categories = []  # Lista de categorias
        self.current_tag = None  # Tag única
        self.current_origin = "all"  # Origem específica
        self.search_query = ""  # Busca textual
        self.active_filters = []  # Lista de {"type": str, "value": str}
        
        # Estado de ordenação
        self.current_sort = "date_desc"  # date_desc/date_asc/name_asc/name_desc/origin/analyzed/not_analyzed
        
        # Estado de paginação
        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_pages = 1
        
        # Callbacks (conectados pela UI)
        self.on_display_update: Optional[Callable] = None  # Chamado quando precisa re-renderizar
    
    # ═══════════════════════════════════════════════════════════════════
    # FILTROS
    # ═══════════════════════════════════════════════════════════════════
    
    def set_filter(self, filter_type: str) -> None:
        """
        Define filtro principal (all/favorite/done/good/bad).
        RESETA todos os outros filtros.
        """
        self.current_filter = filter_type
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.search_query = ""
        self.active_filters.clear()
        self.current_page = 1
        self._trigger_update()
    
    def add_filter_chip(self, filter_type: str, value: str) -> None:
        """
        Adiciona um filtro empilhável (chip AND).
        Tipos: category, tag, origin, collection, analysis_*
        """
        new_chip = {"type": filter_type, "value": value}
        
        if new_chip not in self.active_filters:
            self.active_filters.append(new_chip)
            self.current_page = 1
            self._trigger_update()
    
    def remove_filter_chip(self, filt: dict) -> None:
        """
        Remove um filtro específico.
        """
        if filt in self.active_filters:
            self.active_filters.remove(filt)
            self.current_page = 1
            self._trigger_update()
    
    def clear_all_filters(self) -> None:
        """
        Remove todos os filtros empilháveis.
        """
        self.active_filters.clear()
        self.current_page = 1
        self._trigger_update()
    
    def set_search_query(self, query: str) -> None:
        """
        Define busca textual (bilíngue EN + PT-BR).
        """
        self.search_query = query.strip().lower()
        self.current_page = 1
        self._trigger_update()
    
    def set_origin_filter(self, origin: str) -> None:
        """
        Filtro por origem (ex: "CGTrader").
        """
        self.current_filter = "all"
        self.current_origin = origin
        self.current_categories = []
        self.current_tag = None
        self.current_page = 1
        self.active_filters.clear()
        self.add_filter_chip("origin", origin)
    
    def set_category_filter(self, cats: list) -> None:
        """
        Filtro por categoria(s).
        """
        self.current_filter = "all"
        self.current_categories = cats
        self.current_tag = None
        self.current_origin = "all"
        self.current_page = 1
        self.active_filters.clear()
        for cat in cats:
            self.add_filter_chip("category", cat)
    
    def set_tag_filter(self, tag: str) -> None:
        """
        Filtro por tag única.
        """
        self.current_filter = "all"
        self.current_tag = tag
        self.current_categories = []
        self.current_origin = "all"
        self.current_page = 1
        self.active_filters.clear()
        self.add_filter_chip("tag", tag)
    
    def set_collection_filter(self, collection_name: str) -> None:
        """
        Filtro por coleção.
        """
        self.current_filter = "all"
        self.current_categories = []
        self.current_tag = None
        self.current_origin = "all"
        self.current_page = 1
        self.active_filters.clear()
        self.add_filter_chip("collection", collection_name)
    
    def get_filtered_projects(self) -> list:
        """
        Retorna lista de paths que passam por TODOS os filtros.
        
        Lógica de filtros:
        1. Aplica filtro principal (all/favorite/done/good/bad)
        2. Aplica active_filters (chips AND)
        3. Aplica filtros legados (origin, categories, tag)
        4. Aplica busca textual (bilíngue)
        
        Returns:
            list: Lista de project_paths
        """
        result = []
        
        for path, data in self.database.items():
            # 1. Filtro principal (header)
            ok = (
                self.current_filter == "all"
                or (self.current_filter == "favorite" and data.get("favorite"))
                or (self.current_filter == "done" and data.get("done"))
                or (self.current_filter == "good" and data.get("good"))
                or (self.current_filter == "bad" and data.get("bad"))
            )
            if not ok:
                continue
            
            # 2. Filtros empilháveis (chips AND)
            passes_all_filters = True
            for filt in self.active_filters:
                ftype, fval = filt["type"], filt["value"]
                
                if ftype == "category" and fval not in data.get("categories", []):
                    passes_all_filters = False
                    break
                elif ftype == "tag" and fval not in data.get("tags", []):
                    passes_all_filters = False
                    break
                elif ftype == "origin" and data.get("origin") != fval:
                    passes_all_filters = False
                    break
                elif ftype == "collection":
                    if not self.collections_manager:
                        passes_all_filters = False
                        break
                    if path not in self.collections_manager.get_collection_projects(fval):
                        passes_all_filters = False
                        break
                elif ftype == "analysis_ai" and not (data.get("analyzed") and data.get("analysis_type") == "ai"):
                    passes_all_filters = False
                    break
                elif ftype == "analysis_fallback" and not (data.get("analyzed") and data.get("analysis_type") == "fallback"):
                    passes_all_filters = False
                    break
                elif ftype == "analysis_pending" and data.get("analyzed"):
                    passes_all_filters = False
                    break
            
            if not passes_all_filters:
                continue
            
            # 3. Filtros legados (retrocompatibilidade)
            if self.current_origin != "all" and data.get("origin") != self.current_origin:
                continue
            if self.current_categories and not any(c in data.get("categories", []) for c in self.current_categories):
                continue
            if self.current_tag and self.current_tag not in data.get("tags", []):
                continue
            
            # 4. Busca textual (bilíngue)
            if self.search_query:
                name_en = data.get("name", "")
                if not search_bilingual(self.search_query, name_en):
                    continue
            
            result.append(path)
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # ORDENAÇÃO
    # ═══════════════════════════════════════════════════════════════════
    
    def set_sorting(self, sort_type: str) -> None:
        """
        Define tipo de ordenação.
        Valores: date_desc, date_asc, name_asc, name_desc, origin, analyzed, not_analyzed
        """
        self.current_sort = sort_type
        self.current_page = 1
        self._trigger_update()
    
    def apply_sorting(self, projects: list) -> list:
        """
        Aplica ordenação aos projetos.
        
        Args:
            projects: Lista de tuplas (path, data)
        
        Returns:
            list: Lista ordenada de tuplas (path, data)
        """
        if not projects:
            return projects
        
        try:
            if self.current_sort == "date_desc":
                return sorted(projects, key=lambda p: p[1].get("added_date", ""), reverse=True)
            elif self.current_sort == "date_asc":
                return sorted(projects, key=lambda p: p[1].get("added_date", ""))
            elif self.current_sort == "name_asc":
                return sorted(projects, key=lambda p: p[1].get("name", "").lower())
            elif self.current_sort == "name_desc":
                return sorted(projects, key=lambda p: p[1].get("name", "").lower(), reverse=True)
            elif self.current_sort == "origin":
                return sorted(projects, key=lambda p: (p[1].get("origin", "zzz"), p[1].get("name", "").lower()))
            elif self.current_sort == "analyzed":
                return sorted(projects, key=lambda p: (not p[1].get("analyzed", False), p[1].get("name", "").lower()))
            elif self.current_sort == "not_analyzed":
                return sorted(projects, key=lambda p: (p[1].get("analyzed", False), p[1].get("name", "").lower()))
            else:
                return projects
        except Exception as e:
            self.logger.error("Erro ao ordenar projetos: %s", e)
            return projects
    
    # ═══════════════════════════════════════════════════════════════════
    # PAGINAÇÃO
    # ═══════════════════════════════════════════════════════════════════
    
    def next_page(self) -> None:
        """Avança para próxima página."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._trigger_update()
    
    def prev_page(self) -> None:
        """Volta para página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self._trigger_update()
    
    def first_page(self) -> None:
        """Vai para primeira página."""
        self.current_page = 1
        self._trigger_update()
    
    def last_page(self) -> None:
        """Vai para última página."""
        self.current_page = self.total_pages
        self._trigger_update()
    
    def get_page_info(self, total_count: int) -> dict:
        """
        Calcula informações de paginação.
        
        Args:
            total_count: Número total de itens filtrados
        
        Returns:
            dict: {"current_page", "total_pages", "start_idx", "end_idx", "page_items"}
        """
        self.total_pages = max(1, (total_count + self.items_per_page - 1) // self.items_per_page)
        self.current_page = max(1, min(self.current_page, self.total_pages))
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_count)
        
        return {
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "start_idx": start_idx,
            "end_idx": end_idx,
            "items_per_page": self.items_per_page,
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # UTILIDADES
    # ═══════════════════════════════════════════════════════════════════
    
    def _trigger_update(self) -> None:
        """
        Notifica a UI que o estado mudou e precisa re-renderizar.
        """
        if self.on_display_update:
            self.on_display_update()
    
    def get_display_state(self) -> dict:
        """
        Retorna snapshot do estado atual (para cache/debug).
        """
        return {
            "filter": self.current_filter,
            "origin": self.current_origin,
            "categories": tuple(sorted(self.current_categories)),
            "tag": self.current_tag,
            "search": self.search_query,
            "sort": self.current_sort,
            "page": self.current_page,
            "active_filters": tuple((f["type"], f["value"]) for f in self.active_filters),
        }
