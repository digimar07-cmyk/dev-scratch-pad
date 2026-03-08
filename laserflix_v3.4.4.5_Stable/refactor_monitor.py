#!/usr/bin/env python3
"""
refactor_monitor.py — Monitor de Redução de Código em Tempo Real

Monitora o tamanho do main_window.py e exibe progresso visual da refatoração.

Uso:
    python refactor_monitor.py
"""
import os
import tkinter as tk
from tkinter import ttk

# CONFIGURAÇÃO
MAIN_WINDOW_PATH = "ui/main_window.py"
LINHA_INICIAL = 1000  # Meta original
META_FINAL = 200      # Meta de 80% de redução

def contar_linhas(filepath):
    """Conta linhas de código (excluindo vazias e comentários)."""
    if not os.path.exists(filepath):
        return 0, 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    total = len(linhas)
    codigo = sum(1 for linha in linhas if linha.strip() and not linha.strip().startswith('#'))
    
    return total, codigo

def calcular_metricas():
    """Calcula métricas de progresso."""
    total, codigo = contar_linhas(MAIN_WINDOW_PATH)
    
    reducao_total = LINHA_INICIAL - codigo
    reducao_percentual = (reducao_total / LINHA_INICIAL) * 100 if LINHA_INICIAL > 0 else 0
    
    falta_para_meta = codigo - META_FINAL
    progresso_meta = ((LINHA_INICIAL - codigo) / (LINHA_INICIAL - META_FINAL)) * 100
    
    return {
        'total': total,
        'codigo': codigo,
        'reducao_total': reducao_total,
        'reducao_percentual': reducao_percentual,
        'falta_para_meta': falta_para_meta,
        'progresso_meta': progresso_meta
    }

class RefactorMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("🔍 Laserflix Refactor Monitor")
        self.geometry("600x500")
        self.configure(bg="#1a1a1a")
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', background='#1a1a1a', foreground='#ffffff', font=('Arial', 11))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#00d4ff')
        self.style.configure('Big.TLabel', font=('Arial', 32, 'bold'), foreground='#00ff88')
        self.style.configure('Red.TLabel', foreground='#ff4444')
        self.style.configure('Green.TLabel', foreground='#00ff88')
        self.style.configure('Yellow.TLabel', foreground='#ffaa00')
        
        self._build_ui()
        self.atualizar()
    
    def _build_ui(self):
        # Título
        ttk.Label(self, text="📊 MONITOR DE REFATORAÇÃO", style='Title.TLabel').pack(pady=20)
        
        # Frame principal
        main_frame = tk.Frame(self, bg="#2a2a2a", relief="solid", bd=2)
        main_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Linha atual
        ttk.Label(main_frame, text="LINHAS ATUAIS:", style='TLabel').pack(pady=(20, 5))
        self.lbl_atual = ttk.Label(main_frame, text="---", style='Big.TLabel')
        self.lbl_atual.pack()
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=20, pady=15)
        
        # Métricas
        metrics_frame = tk.Frame(main_frame, bg="#2a2a2a")
        metrics_frame.pack(pady=10, fill="x", padx=40)
        
        # Redução total
        frame1 = tk.Frame(metrics_frame, bg="#2a2a2a")
        frame1.pack(fill="x", pady=5)
        ttk.Label(frame1, text="Redução total:").pack(side="left")
        self.lbl_reducao = ttk.Label(frame1, text="---", style='Green.TLabel')
        self.lbl_reducao.pack(side="right")
        
        # Percentual
        frame2 = tk.Frame(metrics_frame, bg="#2a2a2a")
        frame2.pack(fill="x", pady=5)
        ttk.Label(frame2, text="Percentual:").pack(side="left")
        self.lbl_percentual = ttk.Label(frame2, text="---", style='Green.TLabel')
        self.lbl_percentual.pack(side="right")
        
        # Falta para meta
        frame3 = tk.Frame(metrics_frame, bg="#2a2a2a")
        frame3.pack(fill="x", pady=5)
        ttk.Label(frame3, text="Falta para meta (200):").pack(side="left")
        self.lbl_falta = ttk.Label(frame3, text="---", style='Yellow.TLabel')
        self.lbl_falta.pack(side="right")
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=20, pady=15)
        
        # Barra de progresso
        ttk.Label(main_frame, text="PROGRESSO ATÉ A META:", style='TLabel').pack(pady=(10, 5))
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate', maximum=100)
        self.progress.pack(pady=10)
        self.lbl_progress = ttk.Label(main_frame, text="0%", style='Yellow.TLabel')
        self.lbl_progress.pack(pady=5)
        
        # Timeline
        ttk.Label(main_frame, text="HISTÓRICO:", style='TLabel').pack(pady=(20, 5))
        timeline_frame = tk.Frame(main_frame, bg="#1a1a1a")
        timeline_frame.pack(padx=20, pady=10, fill="x")
        
        timeline_text = [
            "✅ FASE-1.1: NavigationBuilder (609 → 545)",
            "✅ FASE-1.2: HeaderBuilder + CardsGridBuilder (545 → 421)",
            "📋 FASE-2+: Em andamento..."
        ]
        
        for line in timeline_text:
            ttk.Label(timeline_frame, text=line, font=('Courier', 9)).pack(anchor="w", pady=2)
        
        # Botões
        btn_frame = tk.Frame(self, bg="#1a1a1a")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔄 Atualizar", command=self.atualizar, 
                 bg="#00d4ff", fg="#000", font=('Arial', 10, 'bold'),
                 relief="flat", padx=20, pady=8).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="❌ Fechar", command=self.quit,
                 bg="#ff4444", fg="#fff", font=('Arial', 10, 'bold'),
                 relief="flat", padx=20, pady=8).pack(side="left", padx=5)
    
    def atualizar(self):
        """Atualiza as métricas na tela."""
        metricas = calcular_metricas()
        
        # Atualizar labels
        self.lbl_atual.config(text=f"{metricas['codigo']} linhas")
        self.lbl_reducao.config(text=f"-{metricas['reducao_total']} linhas")
        self.lbl_percentual.config(text=f"{metricas['reducao_percentual']:.1f}%")
        
        if metricas['falta_para_meta'] > 0:
            self.lbl_falta.config(text=f"{metricas['falta_para_meta']} linhas", style='Yellow.TLabel')
        else:
            self.lbl_falta.config(text="🎉 META ATINGIDA!", style='Green.TLabel')
        
        # Atualizar barra de progresso
        progresso = min(100, max(0, metricas['progresso_meta']))
        self.progress['value'] = progresso
        self.lbl_progress.config(text=f"{progresso:.1f}%")
        
        # Colorir barra baseado no progresso
        if progresso < 50:
            cor = '#ff4444'
        elif progresso < 80:
            cor = '#ffaa00'
        else:
            cor = '#00ff88'
        
        self.style.configure('TProgressbar', troughcolor='#333333', background=cor)
        
        print(f"\n{'='*60}")
        print(f"🔍 REFACTOR MONITOR - {os.path.basename(MAIN_WINDOW_PATH)}")
        print(f"{'='*60}")
        print(f"📊 Linhas totais:      {metricas['total']}")
        print(f"💻 Linhas de código:   {metricas['codigo']}")
        print(f"✂️  Redução total:      -{metricas['reducao_total']} linhas")
        print(f"📈 Percentual:         {metricas['reducao_percentual']:.1f}%")
        print(f"🎯 Falta para meta:    {metricas['falta_para_meta']} linhas")
        print(f"⚡ Progresso:          {progresso:.1f}%")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    # Verificar se arquivo existe
    if not os.path.exists(MAIN_WINDOW_PATH):
        print(f"❌ ERRO: Arquivo '{MAIN_WINDOW_PATH}' não encontrado!")
        print(f"Execute este script na raiz do projeto Laserflix.")
        exit(1)
    
    # Exibir métricas no terminal
    metricas = calcular_metricas()
    print(f"\n{'='*60}")
    print(f"🔍 REFACTOR MONITOR INICIADO")
    print(f"{'='*60}")
    print(f"📊 Linhas atuais:      {metricas['codigo']}")
    print(f"✂️  Redução total:      -{metricas['reducao_total']} linhas")
    print(f"📈 Percentual:         {metricas['reducao_percentual']:.1f}%")
    print(f"🎯 Falta para meta:    {metricas['falta_para_meta']} linhas")
    print(f"⚡ Progresso:          {metricas['progresso_meta']:.1f}%")
    print(f"{'='*60}\n")
    
    # Abrir interface gráfica
    app = RefactorMonitor()
    app.mainloop()
