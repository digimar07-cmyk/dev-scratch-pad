#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE REFATORAÇÃO 100% AUTOMÁTICO - FASE 1C

Este script EXTRAI o método _build_navigation_controls():
1. Backup automático
2. Extrai bloco de ordenação + navegação (linhas 340-390)
3. Cria novo método _build_navigation_controls()
4. Substitui bloco inline por chamada ao método
5. Valida sintaxe Python
6. Atualiza cabeçalho do arquivo
7. Se auto-deleta após sucesso

REDUÇÃO ESPERADA: ~35 linhas líquidas
ARQUIVO FINAL: ~596 linhas

FILOSOFIA: "Extract Method" (Kent Beck - Tidy First)

USO: python REFACTOR_AUTO_FASE_1C.py

Criado: 08/03/2026 08:25 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path


class AutoRefactorFase1C:
    """Refatoração 100% automática FASE 1C."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.backups = []
        self.changes_made = []
        
    def run(self):
        print("\n" + "="*70)
        print("🔧 REFATORAÇÃO AUTOMÁTICA FASE 1C: EXTRAIR _build_navigation_controls()")
        print("="*70 + "\n")
        
        try:
            print("✅ [1/6] Validando...")
            self._validate()
            print("   ✓ Arquivo OK\n")
            
            print("💾 [2/6] Backup...")
            self._backup_files()
            print(f"   ✓ Backup criado\n")
            
            print("✂️  [3/6] Extraindo método...")
            self._extract_method()
            print("   ✓ Método extraído\n")
            
            print("✅ [4/6] Validando sintaxe...")
            self._validate_syntax()
            print("   ✓ Sintaxe válida\n")
            
            print("📝 [5/6] Atualizando cabeçalho...")
            self._update_header()
            print("   ✓ Cabeçalho atualizado\n")
            
            print("📊 [6/6] Relatório...\n")
            self._report()
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            print("🔄 Restaurando backup...")
            self._restore_backups()
            print("   ✓ Restaurado\n")
            return False
    
    def _validate(self):
        if not self.main_window.exists():
            raise FileNotFoundError("main_window.py não encontrado")
        
        content = self.main_window.read_text(encoding='utf-8')
        
        # Verificar que o bloco alvo existe
        if '# Navigation' not in content:
            raise ValueError("Bloco # Navigation não encontrado")
        
        if 'right_controls = tk.Frame(header_frame, bg=BG_PRIMARY)' not in content:
            raise ValueError("Bloco de controles não encontrado")
        
        # Verificar que método ainda não existe
        if 'def _build_navigation_controls' in content:
            raise ValueError(
                "Método _build_navigation_controls() já existe. "
                "FASE-1C já foi aplicada!"
            )
    
    def _backup_files(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = self.main_window.with_suffix(f".py.backup_{timestamp}")
        shutil.copy2(self.main_window, backup)
        self.backups.append((self.main_window, backup))
    
    def _extract_method(self):
        content = self.main_window.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True)
        
        # Encontrar linha de início do bloco (# Navigation)
        start_idx = None
        for i, line in enumerate(lines):
            if '# Navigation' in line and 'if total_count > 0:' in lines[i-1]:
                start_idx = i - 1  # Incluir o if
                break
        
        if start_idx is None:
            raise ValueError("Início do bloco não encontrado")
        
        # Encontrar fim do bloco (até último .pack(side="left", padx=1) da navegação)
        end_idx = None
        for i in range(start_idx, len(lines)):
            if 'tk.Button(nav_frame, text="⏭"' in lines[i]:
                # Procurar .pack() deste botão
                for j in range(i, min(i+5, len(lines))):
                    if '.pack(side="left", padx=1)' in lines[j]:
                        end_idx = j + 1
                        break
                break
        
        if end_idx is None:
            raise ValueError("Fim do bloco não encontrado")
        
        # Extrair bloco
        block_lines = lines[start_idx:end_idx]
        
        # Criar novo método
        new_method = [
            "    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:\n",
            "        \"\"\"Constrói controles de ordenação + navegação (FASE-1C).\"\"\"\n",
            "        right_controls = tk.Frame(parent, bg=BG_PRIMARY)\n",
            "        right_controls.pack(side=\"right\", padx=10)\n",
            "        \n",
            "        # Ordenação\n",
            "        sort_frame = tk.Frame(right_controls, bg=BG_PRIMARY)\n",
            "        sort_frame.pack(side=\"left\", padx=(0, 15))\n",
            "        \n",
            "        tk.Label(sort_frame, text=\"📊\", bg=BG_PRIMARY,\n",
            "                 fg=FG_TERTIARY, font=(\"Arial\", 12)).pack(side=\"left\", padx=(0, 5))\n",
            "        \n",
            "        sort_labels = {\n",
            "            \"date_desc\": \"📅 Recentes\", \"date_asc\": \"📅 Antigos\",\n",
            "            \"name_asc\": \"🔤 A→Z\", \"name_desc\": \"🔥 Z→A\",\n",
            "            \"origin\": \"🏛️ Origem\", \"analyzed\": \"🤖 Analisados\", \"not_analyzed\": \"⏳ Pendentes\",\n",
            "        }\n",
            "        \n",
            "        sort_var = tk.StringVar(value=self.display_ctrl.current_sort)\n",
            "        style = ttk.Style()\n",
            "        style.theme_use(\"clam\")\n",
            "        style.configure(\"Sort.TCombobox\", fieldbackground=\"#222222\", background=\"#222222\",\n",
            "                        foreground=FG_PRIMARY, arrowcolor=FG_PRIMARY, borderwidth=0)\n",
            "        style.map(\"Sort.TCombobox\",\n",
            "            fieldbackground=[(\"readonly\", \"#222222\")],\n",
            "            selectbackground=[(\"readonly\", \"#222222\")],\n",
            "            selectforeground=[(\"readonly\", FG_PRIMARY)])\n",
            "        \n",
            "        sort_combo = ttk.Combobox(sort_frame, textvariable=sort_var,\n",
            "                                  values=list(sort_labels.values()), state=\"readonly\",\n",
            "                                  width=14, font=(\"Arial\", 9), style=\"Sort.TCombobox\")\n",
            "        sort_combo.pack(side=\"left\")\n",
            "        sort_combo.set(sort_labels[self.display_ctrl.current_sort])\n",
            "        \n",
            "        def on_sort_change(event):\n",
            "            selected_label = sort_combo.get()\n",
            "            for key, label in sort_labels.items():\n",
            "                if label == selected_label:\n",
            "                    self.display_ctrl.set_sorting(key)\n",
            "                    break\n",
            "        \n",
            "        sort_combo.bind(\"<<ComboboxSelected>>\", on_sort_change)\n",
            "        \n",
            "        # Navegação\n",
            "        nav_frame = tk.Frame(right_controls, bg=BG_PRIMARY)\n",
            "        nav_frame.pack(side=\"left\")\n",
            "        \n",
            "        tk.Button(nav_frame, text=\"⏮\", command=self.display_ctrl.first_page,\n",
            "                  bg=\"#333333\", fg=FG_PRIMARY, font=(\"Arial\", 9),\n",
            "                  relief=\"flat\", cursor=\"hand2\", padx=6, pady=3,\n",
            "                  state=\"normal\" if page_info[\"current_page\"] > 1 else \"disabled\"\n",
            "                  ).pack(side=\"left\", padx=1)\n",
            "        \n",
            "        tk.Button(nav_frame, text=\"◀\", command=self.display_ctrl.prev_page,\n",
            "                  bg=\"#444444\", fg=FG_PRIMARY, font=(\"Arial\", 9),\n",
            "                  relief=\"flat\", cursor=\"hand2\", padx=6, pady=3,\n",
            "                  state=\"normal\" if page_info[\"current_page\"] > 1 else \"disabled\"\n",
            "                  ).pack(side=\"left\", padx=1)\n",
            "        \n",
            "        tk.Label(nav_frame, text=f\"Pág {page_info['current_page']}/{page_info['total_pages']}\",\n",
            "                 bg=BG_PRIMARY, fg=ACCENT_GOLD, font=(\"Arial\", 10, \"bold\")\n",
            "                 ).pack(side=\"left\", padx=8)\n",
            "        \n",
            "        tk.Button(nav_frame, text=\"▶\", command=self.display_ctrl.next_page,\n",
            "                  bg=\"#444444\", fg=FG_PRIMARY, font=(\"Arial\", 9),\n",
            "                  relief=\"flat\", cursor=\"hand2\", padx=6, pady=3,\n",
            "                  state=\"normal\" if page_info[\"current_page\"] < page_info[\"total_pages\"] else \"disabled\"\n",
            "                  ).pack(side=\"left\", padx=1)\n",
            "        \n",
            "        tk.Button(nav_frame, text=\"⏭\", command=self.display_ctrl.last_page,\n",
            "                  bg=\"#333333\", fg=FG_PRIMARY, font=(\"Arial\", 9),\n",
            "                  relief=\"flat\", cursor=\"hand2\", padx=6, pady=3,\n",
            "                  state=\"normal\" if page_info[\"current_page\"] < page_info[\"total_pages\"] else \"disabled\"\n",
            "                  ).pack(side=\"left\", padx=1)\n",
            "    \n",
        ]
        
        # Substituir bloco inline por chamada ao método
        replacement = [
            "        if total_count > 0:\n",
            "            self._build_navigation_controls(header_frame, page_info)\n",
            "        \n",
        ]
        
        # Reconstruir arquivo
        new_lines = (
            lines[:start_idx] +  # Tudo antes do bloco
            replacement +  # Chamada ao método
            lines[end_idx:]  # Tudo depois do bloco
        )
        
        # Inserir novo método após _on_collection_filter() (antes de # DISPLAY)
        display_idx = None
        for i, line in enumerate(new_lines):
            if '# DISPLAY' in line:
                display_idx = i
                break
        
        if display_idx is None:
            raise ValueError("# DISPLAY não encontrado")
        
        # Inserir novo método antes de # DISPLAY
        final_lines = (
            new_lines[:display_idx] +
            new_method +
            new_lines[display_idx:]
        )
        
        # Salvar
        self.main_window.write_text(''.join(final_lines), encoding='utf-8')
        
        lines_before = len(lines)
        lines_after = len(final_lines)
        
        self.changes_made.append(
            f"Método _build_navigation_controls() extraído ({lines_before - lines_after} linhas reduzidas)"
        )
    
    def _validate_syntax(self):
        content = self.main_window.read_text(encoding='utf-8')
        try:
            compile(content, str(self.main_window), 'exec')
        except SyntaxError as e:
            raise SyntaxError(f"Erro de sintaxe na linha {e.lineno}: {e.msg}")
    
    def _update_header(self):
        content = self.main_window.read_text(encoding='utf-8')
        
        # Adicionar linha REFACTOR-FASE-1C no cabeçalho
        if 'REFACTOR-FASE-1C' not in content:
            content = content.replace(
                'REFACTOR-CORREÇÃO: Código duplicado REMOVIDO ✅',
                'REFACTOR-CORREÇÃO: Código duplicado REMOVIDO ✅\n'
                'REFACTOR-FASE-1C: _build_navigation_controls() extraído ✅'
            )
            self.main_window.write_text(content, encoding='utf-8')
            self.changes_made.append("Cabeçalho atualizado")
    
    def _restore_backups(self):
        for original, backup in self.backups:
            if backup.exists():
                shutil.copy2(backup, original)
    
    def _report(self):
        print("="*70)
        print("\n🎉 REFATORAÇÃO FASE-1C CONCLUÍDA!\n")
        print("="*70)
        
        print("\n📝 MUDANÇAS:\n")
        for i, change in enumerate(self.changes_made, 1):
            print(f"   {i}. {change}")
        
        content = self.main_window.read_text(encoding='utf-8')
        final_lines = len(content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS:\n")
        print(f"   main_window.py: {final_lines} linhas")
        print(f"   Antes: 631 linhas")
        print(f"   Redução: -{631 - final_lines} linhas\n")
        print(f"   ACUMULADO GERAL:")
        print(f"   Inicial: 868 linhas")
        print(f"   Atual: {final_lines} linhas")
        print(f"   TOTAL: -{868 - final_lines} linhas ({((868 - final_lines) / 868 * 100):.1f}%)")
        
        print(f"\n💾 BACKUP:\n")
        for _, backup in self.backups:
            print(f"   • {backup.name}")
        
        print("\n✅ VALIDAÇÃO:\n")
        print("   ✓ Sintaxe Python válida")
        print("   ✓ Método _build_navigation_controls() criado")
        print("   ✓ Chamada integrada em display_projects()")
        print("   ✓ Cabeçalho atualizado")
        
        print("\n🚀 PRÓXIMOS PASSOS:\n")
        print("   1. Testar app: python main.py")
        print("   2. Testar navegação e ordenação")
        print("   3. Commit: git commit -m 'refactor(FASE-1C): extract _build_navigation_controls()'")
        print("   4. Continuar FASE-1D\n")
        
        print("   🗑️  Auto-deletando este script...")
        try:
            Path(__file__).unlink()
            print("   ✓ REFACTOR_AUTO_FASE_1C.py removido\n")
        except:
            print("   ⚠️  Não foi possível auto-deletar\n")
        
        print("="*70 + "\n")


def main():
    print("\n🚀 Iniciando FASE-1C...\n")
    
    refactor = AutoRefactorFase1C()
    
    try:
        success = refactor.run()
        
        if success:
            print("✅ FASE-1C COMPLETA! Método extraído com sucesso.\n")
            input("Pressione ENTER para sair...")
            sys.exit(0)
        else:
            print("❌ Falhou. Backup restaurado.\n")
            input("Pressione ENTER para sair...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}\n")
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para sair...")
        sys.exit(1)


if __name__ == "__main__":
    main()
