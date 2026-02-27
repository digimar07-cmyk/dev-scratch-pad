"""
LASERFLIX — Filter Manager
Lógica de filtros (favoritos, categorias, tags, busca)
"""


class Filter:
    """Gerencia filtros e busca de projetos"""

    def __init__(self, database):
        self.db = database
        self.current = "all"  # all | favorite | done | good | bad
        self.categories = []
        self.tag = None
        self.origin = "all"
        self.query = ""

    def get_filtered_projects(self):
        """Retorna lista de paths filtrados"""
        result = []
        for project_path, data in self.db.data.items():
            # Filtro principal
            if self.current == "favorite" and not data.get("favorite"):
                continue
            if self.current == "done" and not data.get("done"):
                continue
            if self.current == "good" and not data.get("good"):
                continue
            if self.current == "bad" and not data.get("bad"):
                continue

            # Filtro de origem
            if self.origin != "all" and data.get("origin") != self.origin:
                continue

            # Filtro de categorias (OR)
            if self.categories:
                project_cats = data.get("categories", [])
                if not any(cat in project_cats for cat in self.categories):
                    continue

            # Filtro de tag
            if self.tag:
                if self.tag not in data.get("tags", []):
                    continue

            # Busca por texto
            if self.query:
                name = data.get("name", "").lower()
                tags = " ".join(data.get("tags", [])).lower()
                cats = " ".join(data.get("categories", [])).lower()
                desc = data.get("ai_description", "").lower()
                searchable = f"{name} {tags} {cats} {desc}"
                if self.query not in searchable:
                    continue

            result.append(project_path)

        return result

    def set_category(self, categories):
        """Define filtro de categoria"""
        self.current = "all"
        self.categories = categories
        self.tag = None
        self.origin = "all"

    def set_tag(self, tag):
        """Define filtro de tag"""
        self.current = "all"
        self.tag = tag
        self.categories = []
        self.origin = "all"

    def set_origin(self, origin):
        """Define filtro de origem"""
        self.current = "all"
        self.origin = origin
        self.categories = []
        self.tag = None
