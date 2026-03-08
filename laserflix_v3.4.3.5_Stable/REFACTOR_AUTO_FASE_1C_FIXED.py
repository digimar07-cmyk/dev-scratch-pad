#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE REFATORAÇÃO 100% AUTOMÁTICO - FASE 1C (CORRIGIDO)

Versão corrigida com padrão de busca ajustado.

USO: python REFACTOR_AUTO_FASE_1C_FIXED.py

Criado: 08/03/2026 08:30 BRT
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
        print("🔧 FASE 1C: EXTRAIR _build_navigation_controls() [CORRIGIDO]")
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
        if 'if total_count > 0:' not in content:
            raise ValueError("Bloco 'if total_count > 0:' não encontrado")
        
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
        
        # Encontrar início: procurar "# Navigation" seguido (na próxima linha) de "if total_count > 0:"
        start_idx = None
        for i, line in enumerate(lines):
            if '# Navigation' in line:
                # Verificar se próxima linha tem "if total_count > 0:"
                if i + 1 < len(lines) and 'if total_count > 0:' in lines[i + 1]:
                    start_idx = i  # Começar do comentário
                    break
        
        if start_idx is None:
            raise ValueError("Início do bloco não encontrado")
        
        print(f"   -> Início encontrado na linha {start_idx}")
        
        # Encontrar fim do bloco: último botão de navegação (⏭)
        end_idx = None
        for i in range(start_idx, len(lines)):
            if 'tk.Button(nav_frame, text="⏭"' in lines[i]:
                # Procurar .pack() deste botão (pode estar até 5 linhas depois)
                for j in range(i, min(i + 10, len(lines))):
                    if ').pack(side="left", padx=1)' in lines[j]:
                        end_idx = j + 1
                        break
                if end_idx:
                    break
        
        if end_idx is None:
            raise ValueError("Fim do bloco não encontrado")
        
        print(f"   -> Fim encontrado na linha {end_idx}")
        print(f"   -> Extraindo {end_idx - start_idx} linhas")
        
        # Criar novo método (pegando conteúdo do bloco original e adaptando)
        new_method = self._build_new_method()
        
        # Substituir bloco inline por chamada simples
        replacement = [
            "        # Navigation\n",
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
        
        # Inserir novo método antes de # DISPLAY
        display_idx = None
        for i, line in enumerate(new_lines):
            if '    # DISPLAY' in line:
                display_idx = i
                break
        
        if display_idx is None:
            raise ValueError("# DISPLAY não encontrado")
        
        # Inserir novo método antes de # DISPLAY
        final_lines = (
            new_lines[:display_idx] +
            new_method +
            ["\n"] +
            new_lines[display_idx:]
        )
        
        # Salvar
        self.main_window.write_text(''.join(final_lines), encoding='utf-8')
        
        lines_before = len(lines)
        lines_after = len(final_lines)
        reduction = lines_before - lines_after
        
        self.changes_made.append(
            f"Método _build_navigation_controls() extraído (redução: {reduction} linhas)"
        )
    
    def _build_new_method(self):
        """Constrói o novo método com conteúdo correto."""
        return [
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
        ]
    
    def _validate_syntax(self):
        content = self.main_window.read_text(encoding='utf-8')
        try:
            compile(content, str(self.main_window), 'exec')
        except SyntaxError as e:
            raise SyntaxError(f"Erro de sintaxe na linha {e.lineno}: {e.msg}")
    
    def _update_header(self):
        content = self.main_window.read_text(encoding='utf-8')
        
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
        print("\n🎉 FASE-1C CONCLUÍDA!\n")
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
        print(f"   ACUMULADO:")
        print(f"   Inicial: 868")
        print(f"   Atual: {final_lines}")
        print(f"   TOTAL: -{868 - final_lines} linhas ({((868 - final_lines) / 868 * 100):.1f}%)")
        
        print(f"\n💾 BACKUP: {self.backups[0][1].name}")
        
        print("\n✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar: python main.py")
        print("   2. Commit: git add . && git commit -m 'refactor(FASE-1C): extract navigation'")
        print("   3. Deletar scripts antigos (REFACTOR_AUTO_FASE_1C.py)\n")
        
        print("   🗑️  Auto-deletando...")
        try:
            Path(__file__).unlink()
            # Deletar script antigo tb
            old_script = self.base_dir / "REFACTOR_AUTO_FASE_1C.py"
            if old_script.exists():
                old_script.unlink()
            print("   ✓ Scripts removidos\n")
        except:
            print("   ⚠️  Delete manualmente\n")
        
        print("="*70 + "\n")


def main():
    print("\n🚀 Iniciando FASE-1C [CORRIGIDO]...\n")
    
    refactor = AutoRefactorFase1C()
    
    try:
        success = refactor.run()
        
        if success:
            print("✅ SUCESSO!\n")
            input("Pressione ENTER para sair...")
            sys.exit(0)
        else:
            print("❌ Falhou.\n")
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
