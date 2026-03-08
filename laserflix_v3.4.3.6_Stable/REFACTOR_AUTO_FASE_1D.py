#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE REFATORAÇÃO 100% AUTOMÁTICO - FASE 1D

Este script EXTRAI o método _build_header():
1. Backup automático
2. Extrai bloco de construção do header (linhas ~267-282)
3. Cria novo método _build_header()
4. Substitui bloco inline por chamada ao método
5. Valida sintaxe Python
6. Atualiza cabeçalho do arquivo
7. Se auto-deleta após sucesso

REDUÇÃO ESPERADA: ~28 linhas líquidas
ARQUIVO FINAL: ~568 linhas

FILOSOFIA: "Extract Method" (Kent Beck - Tidy First)

USO: python REFACTOR_AUTO_FASE_1D.py

Criado: 08/03/2026 08:51 BRT
Modelo: Claude Sonnet 4.5
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path


class AutoRefactorFase1D:
    """Refatoração 100% automática FASE 1D."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.main_window = self.base_dir / "ui" / "main_window.py"
        self.backups = []
        self.changes_made = []
        
    def run(self):
        print("\n" + "="*70)
        print("🔧 FASE 1D: EXTRAIR _build_header()")
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
        
        # Verificar que bloco alvo existe
        if '# Header' not in content:
            raise ValueError("Bloco '# Header' não encontrado")
        
        if 'title_map = {' not in content:
            raise ValueError("title_map não encontrado")
        
        # Verificar que método ainda não existe
        if 'def _build_header' in content:
            raise ValueError(
                "Método _build_header() já existe. "
                "FASE-1D já foi aplicada!"
            )
    
    def _backup_files(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = self.main_window.with_suffix(f".py.backup_{timestamp}")
        shutil.copy2(self.main_window, backup)
        self.backups.append((self.main_window, backup))
    
    def _extract_method(self):
        content = self.main_window.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True)
        
        # Encontrar início: "# Header"
        start_idx = None
        for i, line in enumerate(lines):
            if '        # Header' in line:
                start_idx = i
                break
        
        if start_idx is None:
            raise ValueError("Início do bloco não encontrado")
        
        print(f"   -> Início encontrado na linha {start_idx}")
        
        # Encontrar fim: linha com "# Navigation"
        end_idx = None
        for i in range(start_idx, len(lines)):
            if '        # Navigation' in lines[i]:
                end_idx = i
                break
        
        if end_idx is None:
            raise ValueError("Fim do bloco não encontrado")
        
        print(f"   -> Fim encontrado na linha {end_idx}")
        print(f"   -> Extraindo {end_idx - start_idx} linhas")
        
        # Criar novo método
        new_method = self._build_new_method()
        
        # Substituir bloco inline por chamada simples
        replacement = [
            "        self._build_header(total_count, page_info)\n",
            "        \n",
        ]
        
        # Reconstruir arquivo
        new_lines = (
            lines[:start_idx] +  # Tudo antes do bloco
            replacement +  # Chamada ao método
            lines[end_idx:]  # Tudo depois (inclui # Navigation)
        )
        
        # Inserir novo método após _build_navigation_controls()
        nav_method_idx = None
        for i, line in enumerate(new_lines):
            if '                  ).pack(side="left", padx=1)' in line:
                # Última linha do _build_navigation_controls
                nav_method_idx = i + 1
                break
        
        if nav_method_idx is None:
            raise ValueError("Posição de inserção não encontrada")
        
        # Inserir novo método após _build_navigation_controls
        final_lines = (
            new_lines[:nav_method_idx] +
            ["\n"] +
            new_method +
            new_lines[nav_method_idx:]
        )
        
        # Salvar
        self.main_window.write_text(''.join(final_lines), encoding='utf-8')
        
        lines_before = len(lines)
        lines_after = len(final_lines)
        reduction = lines_before - lines_after
        
        self.changes_made.append(
            f"Método _build_header() extraído (redução: {reduction} linhas)"
        )
    
    def _build_new_method(self):
        """Constrói o novo método com conteúdo correto."""
        return [
            "    def _build_header(self, total_count: int, page_info: dict) -> None:\n",
            "        \"\"\"Constrói header com título + navegação (FASE-1D).\"\"\"\n",
            "        title_map = {\n",
            "            \"favorite\": \"⭐ Favoritos\", \"done\": \"✓ Já Feitos\",\n",
            "            \"good\": \"👍 Bons\", \"bad\": \"👎 Ruins\",\n",
            "        }\n",
            "        title = title_map.get(self.display_ctrl.current_filter, \"Todos os Projetos\")\n",
            "        if self.display_ctrl.current_origin != \"all\":\n",
            "            title += f\" — {self.display_ctrl.current_origin}\"\n",
            "        if self.display_ctrl.current_categories:\n",
            "            title += f\" — {', '.join(self.display_ctrl.current_categories)}\"\n",
            "        if self.display_ctrl.current_tag:\n",
            "            title += f\" — #{self.display_ctrl.current_tag}\"\n",
            "        if self.display_ctrl.search_query:\n",
            "            title += f' — \"{self.display_ctrl.search_query}\"'\n",
            "        \n",
            "        header_frame = tk.Frame(self.scrollable_frame, bg=BG_PRIMARY)\n",
            "        header_frame.grid(row=0, column=0, columnspan=COLS, sticky=\"ew\", padx=10, pady=(0, 5))\n",
            "        \n",
            "        tk.Label(header_frame, text=title,\n",
            "                 font=(\"Arial\", 20, \"bold\"), bg=BG_PRIMARY, fg=FG_PRIMARY, anchor=\"w\"\n",
            "                 ).pack(side=\"left\")\n",
            "        \n",
            "        if total_count > 0:\n",
            "            self._build_navigation_controls(header_frame, page_info)\n",
        ]
    
    def _validate_syntax(self):
        content = self.main_window.read_text(encoding='utf-8')
        try:
            compile(content, str(self.main_window), 'exec')
        except SyntaxError as e:
            raise SyntaxError(f"Erro de sintaxe na linha {e.lineno}: {e.msg}")
    
    def _update_header(self):
        content = self.main_window.read_text(encoding='utf-8')
        
        if 'REFACTOR-FASE-1D' not in content:
            content = content.replace(
                'REFACTOR-FASE-1C: _build_navigation_controls() extraído ✅',
                'REFACTOR-FASE-1C: _build_navigation_controls() extraído ✅\n'
                'REFACTOR-FASE-1D: _build_header() extraído ✅'
            )
            self.main_window.write_text(content, encoding='utf-8')
            self.changes_made.append("Cabeçalho atualizado")
    
    def _restore_backups(self):
        for original, backup in self.backups:
            if backup.exists():
                shutil.copy2(backup, original)
    
    def _report(self):
        print("="*70)
        print("\n🎉 FASE-1D CONCLUÍDA!\n")
        print("="*70)
        
        print("\n📝 MUDANÇAS:\n")
        for i, change in enumerate(self.changes_made, 1):
            print(f"   {i}. {change}")
        
        content = self.main_window.read_text(encoding='utf-8')
        final_lines = len(content.splitlines())
        
        print(f"\n📊 ESTATÍSTICAS:\n")
        print(f"   main_window.py: {final_lines} linhas")
        print(f"   Antes: 596 linhas")
        print(f"   Redução: -{596 - final_lines} linhas\n")
        print(f"   ACUMULADO:")
        print(f"   Inicial: 868")
        print(f"   Atual: {final_lines}")
        print(f"   TOTAL: -{868 - final_lines} linhas ({((868 - final_lines) / 868 * 100):.1f}%)")
        
        print(f"\n💾 BACKUP: {self.backups[0][1].name}")
        
        print("\n✅ PRÓXIMOS PASSOS:\n")
        print("   1. Testar: python main.py")
        print("   2. Commit: git add . && git commit -m 'refactor(FASE-1D): extract header'")
        print("   3. Continuar FASE-1E\n")
        
        print("   🗑️  Auto-deletando...")
        try:
            Path(__file__).unlink()
            print("   ✓ Script removido\n")
        except:
            print("   ⚠️  Delete manualmente\n")
        
        print("="*70 + "\n")


def main():
    print("\n🚀 Iniciando FASE-1D...\n")
    
    refactor = AutoRefactorFase1D()
    
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
