"""
LASERFLIX — Dashboard de Estatísticas
Visão geral com métricas e gráficos
"""

import tkinter as tk
from tkinter import ttk
from collections import Counter


class Dashboard:
    """Dashboard Netflix-style com estatísticas do banco"""

    def __init__(self, app):
        self.app = app
        
        # Window
        self.window = tk.Toplevel(app.root)
        self.window.title("📊 Dashboard LASERFLIX")
        self.window.geometry("1000x700")
        self.window.configure(bg="#141414")
        self.window.transient(app.root)
        
        self._create_ui()
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # UI CREATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def _create_ui(self):
        # Scrollable container
        canvas = tk.Canvas(self.window, bg="#141414", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#141414")
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        tk.Label(
            scrollable,
            text="📊 DASHBOARD LASERFLIX",
            font=("Arial", 28, "bold"),
            fg="#E50914",
            bg="#141414"
        ).pack(pady=(0, 20))
        
        # Stats
        self._create_stats_cards(scrollable)
        
        # Categories & Tags
        self._create_top_categories(scrollable)
        self._create_top_tags(scrollable)
        
        # Origins
        self._create_origins_section(scrollable)
        
        # Analysis stats
        self._create_analysis_stats(scrollable)
        
    def _create_stats_cards(self, parent):
        """Cards com estatísticas principais"""
        stats = self._calculate_stats()
        
        cards_frame = tk.Frame(parent, bg="#141414")
        cards_frame.pack(fill="x", pady=10)
        
        # Row 1
        row1 = tk.Frame(cards_frame, bg="#141414")
        row1.pack(fill="x", pady=5)
        
        self._create_stat_card(row1, "📁 Total", stats["total"], "#E50914")
        self._create_stat_card(row1, "⭐ Favoritos", stats["favorites"], "#FFD700")
        self._create_stat_card(row1, "✓ Concluídos", stats["done"], "#00FF00")
        self._create_stat_card(row1, "👍 Good", stats["good"], "#00FF00")
        
        # Row 2
        row2 = tk.Frame(cards_frame, bg="#141414")
        row2.pack(fill="x", pady=5)
        
        self._create_stat_card(row2, "👎 Bad", stats["bad"], "#FF0000")
        self._create_stat_card(row2, "🤖 Analisados", stats["analyzed"], "#00BFFF")
        self._create_stat_card(row2, "📂 Categorias", stats["categories_count"], "#FFA500")
        self._create_stat_card(row2, "🏷️ Tags", stats["tags_count"], "#FF69B4")
        
    def _create_stat_card(self, parent, label, value, color):
        card = tk.Frame(parent, bg="#1a1a1a", relief="flat", bd=0)
        card.pack(side="left", fill="both", expand=True, padx=5)
        
        tk.Label(
            card,
            text=str(value),
            font=("Arial", 32, "bold"),
            fg=color,
            bg="#1a1a1a"
        ).pack(pady=(15, 0))
        
        tk.Label(
            card,
            text=label,
            font=("Arial", 11),
            fg="#999999",
            bg="#1a1a1a"
        ).pack(pady=(0, 15))
        
    def _create_top_categories(self, parent):
        """Top 10 categorias mais usadas"""
        tk.Label(
            parent,
            text="🔥 Top 10 Categorias",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#141414"
        ).pack(anchor="w", pady=(20, 10))
        
        categories = []
        for project in self.app.database.data.values():
            categories.extend(project.get("categories", []))
            
        if categories:
            top_10 = Counter(categories).most_common(10)
            self._create_bar_chart(parent, top_10, "#E50914")
        else:
            tk.Label(
                parent,
                text="Nenhuma categoria ainda",
                font=("Arial", 11),
                fg="#666666",
                bg="#141414"
            ).pack(anchor="w", padx=10)
            
    def _create_top_tags(self, parent):
        """Top 10 tags mais usadas"""
        tk.Label(
            parent,
            text="🏆 Top 10 Tags",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#141414"
        ).pack(anchor="w", pady=(20, 10))
        
        tags = []
        for project in self.app.database.data.values():
            tags.extend(project.get("tags", []))
            
        if tags:
            top_10 = Counter(tags).most_common(10)
            self._create_bar_chart(parent, top_10, "#00BFFF")
        else:
            tk.Label(
                parent,
                text="Nenhuma tag ainda",
                font=("Arial", 11),
                fg="#666666",
                bg="#141414"
            ).pack(anchor="w", padx=10)
            
    def _create_bar_chart(self, parent, data, color):
        """Gráfico de barras simples"""
        chart_frame = tk.Frame(parent, bg="#1a1a1a")
        chart_frame.pack(fill="x", pady=10)
        
        if not data:
            return
            
        max_value = max(count for _, count in data)
        
        for name, count in data:
            row = tk.Frame(chart_frame, bg="#1a1a1a")
            row.pack(fill="x", padx=10, pady=2)
            
            # Label
            tk.Label(
                row,
                text=name[:20],
                font=("Arial", 10),
                fg="white",
                bg="#1a1a1a",
                width=20,
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            
            # Bar
            bar_width = int((count / max_value) * 400) if max_value > 0 else 0
            bar = tk.Frame(row, bg=color, height=20, width=bar_width)
            bar.pack(side="left", fill="y")
            bar.pack_propagate(False)
            
            # Count
            tk.Label(
                bar,
                text=str(count),
                font=("Arial", 9, "bold"),
                fg="white",
                bg=color
            ).pack(side="right", padx=5)
            
    def _create_origins_section(self, parent):
        """Distribuição por origem"""
        tk.Label(
            parent,
            text="🌍 Distribuição por Origem",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#141414"
        ).pack(anchor="w", pady=(20, 10))
        
        origins = []
        for project in self.app.database.data.values():
            origins.append(project.get("origin", "Diversos"))
            
        if origins:
            origin_counts = Counter(origins).most_common()
            self._create_bar_chart(parent, origin_counts, "#FFA500")
        else:
            tk.Label(
                parent,
                text="Nenhum projeto ainda",
                font=("Arial", 11),
                fg="#666666",
                bg="#141414"
            ).pack(anchor="w", padx=10)
            
    def _create_analysis_stats(self, parent):
        """Estatísticas de análise"""
        tk.Label(
            parent,
            text="🤖 Estatísticas de Análise IA",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#141414"
        ).pack(anchor="w", pady=(20, 10))
        
        analyzed = sum(1 for p in self.app.database.data.values() if p.get("analyzed", False))
        not_analyzed = len(self.app.database.data) - analyzed
        
        stats_frame = tk.Frame(parent, bg="#1a1a1a")
        stats_frame.pack(fill="x", pady=10)
        
        # Analyzed
        row1 = tk.Frame(stats_frame, bg="#1a1a1a")
        row1.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            row1,
            text=f"✓ Analisados: {analyzed}",
            font=("Arial", 12),
            fg="#00FF00",
            bg="#1a1a1a"
        ).pack(side="left")
        
        # Not analyzed
        row2 = tk.Frame(stats_frame, bg="#1a1a1a")
        row2.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            row2,
            text=f"○ Não Analisados: {not_analyzed}",
            font=("Arial", 12),
            fg="#FF6600",
            bg="#1a1a1a"
        ).pack(side="left")
        
        # Progress bar
        if len(self.app.database.data) > 0:
            progress = (analyzed / len(self.app.database.data)) * 100
            
            tk.Label(
                stats_frame,
                text=f"Progresso: {progress:.1f}%",
                font=("Arial", 11),
                fg="#999999",
                bg="#1a1a1a"
            ).pack(pady=(10, 5))
            
            progress_bar_bg = tk.Frame(stats_frame, bg="#2a2a2a", height=30)
            progress_bar_bg.pack(fill="x", padx=10, pady=(0, 10))
            
            progress_width = int((progress / 100) * 920)
            progress_bar = tk.Frame(progress_bar_bg, bg="#00FF00", width=progress_width)
            progress_bar.pack(side="left", fill="y")
            
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CALCULATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def _calculate_stats(self):
        """Calcula todas as estatísticas"""
        data = self.app.database.data
        
        all_categories = set()
        all_tags = set()
        
        for project in data.values():
            all_categories.update(project.get("categories", []))
            all_tags.update(project.get("tags", []))
            
        return {
            "total": len(data),
            "favorites": sum(1 for p in data.values() if p.get("favorite", False)),
            "done": sum(1 for p in data.values() if p.get("done", False)),
            "good": sum(1 for p in data.values() if p.get("good", False)),
            "bad": sum(1 for p in data.values() if p.get("bad", False)),
            "analyzed": sum(1 for p in data.values() if p.get("analyzed", False)),
            "categories_count": len(all_categories),
            "tags_count": len(all_tags),
        }
