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

# =====================================================================
# CONFIGURAÇÃO FÁCIL - MODIFIQUE AQUI!
# =====================================================================
WINDOW_WIDTH = 700   # Largura da janela em pixels
WINDOW_HEIGHT = 750  # Altura da janela em pixels
# =====================================================================

# CONFIGURAÇÃO DO MONITOR
MAIN_WINDOW_PATH = "ui/main_window.py"

# HISTÓRICO DE FASES
LINHA_INICIAL = 609  # Linha antes de QUALQUER refatoração
META_FINAL = 200     # Meta final de 80% de redução

# FASES COMPLETAS
FASES = [
    {"nome": "INICIAL", "linhas": 609, "descricao": "Código original"},
    {"nome": "FASE-1.1", "linhas": 545, "descricao": "NavigationBuilder extraído"},
    {"nome": "FASE-1.2", "linhas": 490, "descricao": "HeaderBuilder + CardsGridBuilder (ESPERADO)"},
]

def contar_linhas(filepath):
    """Conta linhas totais e de código."""
    if not os.path.exists(filepath):
        return 0, 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    total = len(linhas)
    codigo = sum(1 for linha in linhas 
                 if linha.strip() 
                 and not linha.strip().startswith('#')
                 and not linha.strip().startswith('"""')
                 and not linha.strip() == '"""')
    
    return total, codigo

def calcular_metricas():
    """Calcula métricas de progresso."""
    total, codigo = contar_linhas(MAIN_WINDOW_PATH)
    
    # Fase atual esperada
    fase_atual = FASES[-1]
    linhas_esperadas = fase_atual["linhas"]
    
    # Diferença entre esperado e real
    diferenca = total - linhas_esperadas
    
    # Redução total desde o início
    reducao_total = LINHA_INICIAL - total
    reducao_percentual = (reducao_total / LINHA_INICIAL) * 100
    
    # Falta para meta
    falta_para_meta = total - META_FINAL
    progresso_meta = ((LINHA_INICIAL - total) / (LINHA_INICIAL - META_FINAL)) * 100
    
    # Status da fase
    if diferenca > 0:
        status_fase = "ACIMA DO ESPERADO"
        cor_status = "red"
    elif diferenca < 0:
        status_fase = "ABAIXO DO ESPERADO"
        cor_status = "green"
    else:
        status_fase = "CONFORME ESPERADO"
        cor_status = "green"
    
    return {
        'total': total,
        'codigo': codigo,
        'esperado': linhas_esperadas,
        'diferenca': diferenca,
        'status_fase': status_fase,
        'cor_status': cor_status,
        'reducao_total': reducao_total,
        'reducao_percentual': reducao_percentual,
        'falta_para_meta': falta_para_meta,
        'progresso_meta': progresso_meta,
        'fase_atual': fase_atual['nome']
    }

class RefactorMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("🔍 Laserflix Refactor Monitor")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")  # Usa as constantes definidas no topo
        self.configure(bg="#1a1a1a")
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', background='#1a1a1a', foreground='#ffffff', font=('Arial', 11))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#00d4ff')
        self.style.configure('Big.TLabel', font=('Arial', 32, 'bold'), foreground='#00ff88')
        self.style.configure('Red.TLabel', foreground='#ff4444', font=('Arial', 12, 'bold'))
        self.style.configure('Green.TLabel', foreground='#00ff88', font=('Arial', 12, 'bold'))
        self.style.configure('Yellow.TLabel', foreground='#ffaa00', font=('Arial', 12))
        self.style.configure('White.TLabel', foreground='#ffffff', font=('Arial', 12))
        
        self._build_ui()
        self.atualizar()
    
    def _build_ui(self):
        # Título
        ttk.Label(self, text="📊 MONITOR DE REFATORAÇÃO", style='Title.TLabel').pack(pady=20)
        
        # Frame principal
        main_frame = tk.Frame(self, bg="#2a2a2a", relief="solid", bd=2)
        main_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # COMPARAÇÃO: ESPERADO vs REAL
        ttk.Label(main_frame, text="⚠️  COMPARAÇÃO:", style='Title.TLabel').pack(pady=(20, 10))
        
        compare_frame = tk.Frame(main_frame, bg="#2a2a2a")
        compare_frame.pack(pady=10, fill="x", padx=40)
        
        # Esperado
        frame_esp = tk.Frame(compare_frame, bg="#2a2a2a")
        frame_esp.pack(fill="x", pady=5)
        ttk.Label(frame_esp, text="Esperado (após FASE-1.2):").pack(side="left")
        self.lbl_esperado = ttk.Label(frame_esp, text="---", style='White.TLabel')
        self.lbl_esperado.pack(side="right")
        
        # Real
        frame_real = tk.Frame(compare_frame, bg="#2a2a2a")
        frame_real.pack(fill="x", pady=5)
        ttk.Label(frame_real, text="Real (atual no GitHub):").pack(side="left")
        self.lbl_real = ttk.Label(frame_real, text="---", style='White.TLabel')
        self.lbl_real.pack(side="right")
        
        # Diferença
        frame_diff = tk.Frame(compare_frame, bg="#2a2a2a")
        frame_diff.pack(fill="x", pady=5)
        ttk.Label(frame_diff, text="Diferença:").pack(side="left")
        self.lbl_diferenca = ttk.Label(frame_diff, text="---", style='Red.TLabel')
        self.lbl_diferenca.pack(side="right")
        
        # Status
        self.lbl_status = ttk.Label(main_frame, text="---", style='Red.TLabel')
        self.lbl_status.pack(pady=10)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=20, pady=15)
        
        # Métricas gerais
        ttk.Label(main_frame, text="📈 PROGRESSO GERAL:", style='Title.TLabel').pack(pady=(10, 10))
        
        metrics_frame = tk.Frame(main_frame, bg="#2a2a2a")
        metrics_frame.pack(pady=10, fill="x", padx=40)
        
        # Redução total
        frame1 = tk.Frame(metrics_frame, bg="#2a2a2a")
        frame1.pack(fill="x", pady=5)
        ttk.Label(frame1, text="Redução desde início (609):").pack(side="left")
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
        self.progress = ttk.Progressbar(main_frame, length=450, mode='determinate', maximum=100)
        self.progress.pack(pady=10)
        self.lbl_progress = ttk.Label(main_frame, text="0%", style='Yellow.TLabel')
        self.lbl_progress.pack(pady=5)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=20, pady=15)
        
        # Timeline
        ttk.Label(main_frame, text="📅 HISTÓRICO DE FASES:", style='Title.TLabel').pack(pady=(10, 10))
        
        timeline_frame = tk.Frame(main_frame, bg="#1a1a1a", relief="sunken", bd=1)
        timeline_frame.pack(padx=40, pady=10, fill="x")
        
        for fase in FASES:
            status = "✅" if fase["nome"] != "FASE-1.2" else "⚠️ "
            linha_txt = f"{status} {fase['nome']}: {fase['linhas']} linhas - {fase['descricao']}"
            ttk.Label(timeline_frame, text=linha_txt, font=('Courier', 9)).pack(anchor="w", pady=2, padx=10)
        
        # Botões
        btn_frame = tk.Frame(self, bg="#1a1a1a")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="🔄 Atualizar", command=self.atualizar, 
                 bg="#00d4ff", fg="#000", font=('Arial', 10, 'bold'),
                 relief="flat", padx=20, pady=8).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="❌ Fechar", command=self.quit,
                 bg="#ff4444", fg="#fff", font=('Arial', 10, 'bold'),
                 relief="flat", padx=20, pady=8).pack(side="left", padx=5)
    
    def atualizar(self):
        """Atualiza as métricas na tela."""
        metricas = calcular_metricas()
        
        # Atualizar comparação
        self.lbl_esperado.config(text=f"{metricas['esperado']} linhas")
        self.lbl_real.config(text=f"{metricas['total']} linhas")
        
        if metricas['diferenca'] > 0:
            self.lbl_diferenca.config(
                text=f"+{metricas['diferenca']} linhas A MAIS",
                style='Red.TLabel'
            )
            self.lbl_status.config(
                text=f"❌ {metricas['status_fase']} - CÓDIGO NÃO FOI REMOVIDO!",
                style='Red.TLabel'
            )
        elif metricas['diferenca'] < 0:
            self.lbl_diferenca.config(
                text=f"{metricas['diferenca']} linhas A MENOS",
                style='Green.TLabel'
            )
            self.lbl_status.config(
                text=f"✅ {metricas['status_fase']} - ÓTIMO!",
                style='Green.TLabel'
            )
        else:
            self.lbl_diferenca.config(
                text="Exato!",
                style='Green.TLabel'
            )
            self.lbl_status.config(
                text=f"✅ {metricas['status_fase']}",
                style='Green.TLabel'
            )
        
        # Atualizar métricas gerais
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
        
        # Print no terminal
        print(f"\n{'='*70}")
        print(f"🔍 REFACTOR MONITOR - {os.path.basename(MAIN_WINDOW_PATH)}")
        print(f"{'='*70}")
        print(f"\n⚠️  COMPARAÇÃO ({metricas['fase_atual']}):")
        print(f"   Esperado:  {metricas['esperado']} linhas")
        print(f"   Real:      {metricas['total']} linhas")
        print(f"   Diferença: {'+' if metricas['diferenca'] > 0 else ''}{metricas['diferenca']} linhas")
        print(f"   Status:    {metricas['status_fase']}")
        print(f"\n📈 PROGRESSO GERAL:")
        print(f"   Redução total:  -{metricas['reducao_total']} linhas ({metricas['reducao_percentual']:.1f}%)")
        print(f"   Falta p/ meta:  {metricas['falta_para_meta']} linhas")
        print(f"   Progresso:      {progresso:.1f}%")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    # Verificar se arquivo existe
    if not os.path.exists(MAIN_WINDOW_PATH):
        print(f"❌ ERRO: Arquivo '{MAIN_WINDOW_PATH}' não encontrado!")
        print(f"Execute este script na raiz do projeto Laserflix.")
        exit(1)
    
    # Exibir métricas no terminal
    metricas = calcular_metricas()
    print(f"\n{'='*70}")
    print(f"🔍 REFACTOR MONITOR INICIADO")
    print(f"{'='*70}")
    print(f"\n⚠️  COMPARAÇÃO ({metricas['fase_atual']}):")
    print(f"   Esperado:  {metricas['esperado']} linhas")
    print(f"   Real:      {metricas['total']} linhas")
    print(f"   Diferença: {'+' if metricas['diferenca'] > 0 else ''}{metricas['diferenca']} linhas")
    print(f"   Status:    {metricas['status_fase']}")
    print(f"\n📈 PROGRESSO GERAL:")
    print(f"   Redução total:  -{metricas['reducao_total']} linhas ({metricas['reducao_percentual']:.1f}%)")
    print(f"   Falta p/ meta:  {metricas['falta_para_meta']} linhas")
    print(f"   Progresso:      {metricas['progresso_meta']:.1f}%")
    print(f"{'='*70}\n")
    
    # Abrir interface gráfica
    app = RefactorMonitor()
    app.mainloop()
