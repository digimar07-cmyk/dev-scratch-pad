#!/usr/bin/env python3
"""
refactor_navigation_FASE_1_1.py — Script cirúrgico para FASE-1.1

O que faz:
1. Localiza método _build_navigation_controls() no main_window.py
2. Substitui por versão simplificada que usa NavigationBuilder
3. Cria backup automático
4. Valida sintaxe Python
5. Mostra diff das mudanças

Redução: ~64 linhas (609 → 545)

Uso:
    cd laserflix_v3.4.4.0_Stable
    python refactor_navigation_FASE_1_1.py
"""

import os
import re
import ast
import shutil
import difflib
from datetime import datetime

# Configurações
TARGET_FILE = "ui/main_window.py"
BACKUP_SUFFIX = ".backup_FASE_1_1_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S"))

# Método antigo (padrão de busca)
OLD_METHOD_START = '    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:'
OLD_METHOD_END_MARKER = '                  ).pack(side="left", padx=1)'  # Último pack() do método

# Método novo (simplificado)
NEW_METHOD = '''    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:
        """Constrói controles de ordenação + navegação usando NavigationBuilder (FASE-1.1)."""
        from ui.builders.navigation_builder import NavigationBuilder
        NavigationBuilder.build(parent, page_info, self.display_ctrl)
'''


def validate_python_syntax(content: str) -> bool:
    """
    Valida se o conteúdo é Python válido.
    
    Args:
        content: Código Python como string
        
    Returns:
        True se válido, False caso contrário
    """
    try:
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.msg}")
        print(f"   {e.text}")
        return False


def create_backup(filepath: str) -> str:
    """
    Cria backup do arquivo.
    
    Args:
        filepath: Caminho do arquivo
        
    Returns:
        Caminho do arquivo de backup
    """
    backup_path = filepath + BACKUP_SUFFIX
    shutil.copy2(filepath, backup_path)
    return backup_path


def show_diff(original: str, modified: str, filename: str) -> None:
    """
    Mostra diff entre versão original e modificada.
    
    Args:
        original: Conteúdo original
        modified: Conteúdo modificado
        filename: Nome do arquivo
    """
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (refatorado)",
        lineterm=''
    )
    
    print("\n" + "=" * 80)
    print("📋 DIFF DAS MUDANÇAS")
    print("=" * 80)
    print()
    
    diff_lines = list(diff)
    if not diff_lines:
        print("❌ Nenhuma mudança detectada!")
        return
    
    # Mostrar apenas contexto relevante (±5 linhas)
    for line in diff_lines[:50]:  # Limitar output
        if line.startswith('+') and not line.startswith('+++'):
            print(f"\033[92m{line}\033[0m", end='')  # Verde
        elif line.startswith('-') and not line.startswith('---'):
            print(f"\033[91m{line}\033[0m", end='')  # Vermelho
        elif line.startswith('@@'):
            print(f"\033[94m{line}\033[0m", end='')  # Azul
        else:
            print(line, end='')
    
    if len(diff_lines) > 50:
        print(f"\n... (mais {len(diff_lines) - 50} linhas)")


def refactor_main_window(content: str) -> tuple[str, int, int]:
    """
    Refatora main_window.py substituindo _build_navigation_controls().
    
    Args:
        content: Conteúdo original do arquivo
        
    Returns:
        Tupla (conteúdo_refatorado, linhas_removidas, linhas_adicionadas)
    """
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    method_found = False
    lines_removed = 0
    in_method = False
    
    while i < len(lines):
        line = lines[i]
        
        # Detectar início do método
        if OLD_METHOD_START in line:
            method_found = True
            in_method = True
            
            print(f"\n✓ Método encontrado na linha {i + 1}")
            
            # Adicionar método novo
            new_lines.append(NEW_METHOD.rstrip())
            
            # Pular linhas do método antigo até encontrar o marcador de fim
            lines_skipped = 0
            i += 1
            
            while i < len(lines):
                lines_skipped += 1
                lines_removed += 1
                
                # Verificar se é a última linha do método (último .pack)
                if OLD_METHOD_END_MARKER in lines[i]:
                    # Encontrou o fim, pular esta linha também
                    i += 1
                    in_method = False
                    break
                
                i += 1
            
            print(f"✓ Removidas {lines_skipped} linhas do método antigo")
            continue
        
        # Adicionar linha normal
        new_lines.append(line)
        i += 1
    
    if not method_found:
        print("\n❌ ERRO: Método _build_navigation_controls() NÃO encontrado!")
        return content, 0, 0
    
    # Contar linhas adicionadas (método novo)
    lines_added = len(NEW_METHOD.strip().split('\n'))
    
    return '\n'.join(new_lines), lines_removed, lines_added


def count_lines(content: str) -> int:
    """Conta linhas de código (exclui comentários e linhas vazias)."""
    lines = content.split('\n')
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    return len(code_lines)


def main():
    """
    Função principal do script.
    """
    print("=" * 80)
    print("🚀 REFATORAÇÃO CIRÚRGICA - FASE-1.1")
    print("=" * 80)
    print("\n🎯 Objetivo: Extrair _build_navigation_controls() → NavigationBuilder")
    print("📉 Redução esperada: ~64 linhas (609 → 545)")
    print("\n" + "=" * 80)
    
    # Verificar se arquivo existe
    if not os.path.exists(TARGET_FILE):
        print(f"\n❌ ERRO: Arquivo {TARGET_FILE} não encontrado!")
        print("\n💡 Dica: Execute o script da raiz do projeto:")
        print("   cd laserflix_v3.4.4.0_Stable")
        print("   python refactor_navigation_FASE_1_1.py")
        return 1
    
    # Ler arquivo original
    print(f"\n📖 Lendo {TARGET_FILE}...")
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    original_total_lines = len(original_content.split('\n'))
    original_code_lines = count_lines(original_content)
    print(f"✓ Arquivo lido: {original_total_lines} linhas totais ({original_code_lines} linhas de código)")
    
    # Criar backup
    print(f"\n💾 Criando backup...")
    backup_path = create_backup(TARGET_FILE)
    print(f"✓ Backup criado: {backup_path}")
    
    # Refatorar
    print(f"\n🔧 Aplicando refatoração...")
    refactored_content, lines_removed, lines_added = refactor_main_window(original_content)
    
    if lines_removed == 0:
        print("\n❌ ERRO: Nenhuma modificação foi feita!")
        print(f"💾 Backup disponível em: {backup_path}")
        return 1
    
    print(f"✓ Refatoração aplicada:")
    print(f"   - Linhas removidas: {lines_removed}")
    print(f"   - Linhas adicionadas: {lines_added}")
    print(f"   - Redução líquida: {lines_removed - lines_added} linhas")
    
    # Validar sintaxe
    print(f"\n✅ Validando sintaxe Python...")
    if not validate_python_syntax(refactored_content):
        print("\n❌ ERRO: Código inválido gerado!")
        print(f"💾 Backup disponível em: {backup_path}")
        print("\n🔧 Para restaurar:")
        print(f"   cp {backup_path} {TARGET_FILE}")
        return 1
    
    print("✓ Sintaxe válida!")
    
    # Mostrar diff
    show_diff(original_content, refactored_content, TARGET_FILE)
    
    # Confirmar antes de salvar
    print("\n" + "=" * 80)
    print("⚠️  CONFIRMAR MUDANÇAS")
    print("=" * 80)
    
    response = input("\nAplicar mudanças? [s/N]: ").strip().lower()
    
    if response != 's':
        print("\n❌ Operação cancelada pelo usuário")
        print(f"💾 Backup disponível em: {backup_path}")
        return 0
    
    # Salvar arquivo refatorado
    print(f"\n💾 Salvando arquivo refatorado...")
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.write(refactored_content)
    
    refactored_total_lines = len(refactored_content.split('\n'))
    refactored_code_lines = count_lines(refactored_content)
    reduction = original_total_lines - refactored_total_lines
    code_reduction = original_code_lines - refactored_code_lines
    
    print("✓ Arquivo salvo!")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("🎉 REFATORAÇÃO CONCLUÍDA!")
    print("=" * 80)
    
    print(f"\n📊 Estatísticas:")
    print(f"   Linhas totais:")
    print(f"      Antes:  {original_total_lines} linhas")
    print(f"      Depois: {refactored_total_lines} linhas")
    print(f"      Redução: {reduction} linhas ({(reduction/original_total_lines*100):.1f}%)")
    print()
    print(f"   Linhas de código:")
    print(f"      Antes:  {original_code_lines} linhas")
    print(f"      Depois: {refactored_code_lines} linhas")
    print(f"      Redução: {code_reduction} linhas ({(code_reduction/original_code_lines*100):.1f}%)")
    
    print(f"\n💾 Backup: {backup_path}")
    print(f"✅ Arquivo atualizado: {TARGET_FILE}")
    
    print("\n" + "=" * 80)
    print("👉 PRÓXIMOS PASSOS")
    print("=" * 80)
    
    print("\n1. Testar o app:")
    print("   python main.py")
    
    print("\n2. Verificar funcionalidade:")
    print("   ✓ App abre sem erro")
    print("   ✓ Combobox de ordenação funciona")
    print("   ✓ Botões ⏮ ◀ ▶ ⏭ navegam páginas")
    print("   ✓ Label 'Pág X/Y' atualiza")
    
    print("\n3. Se funcionar:")
    print("   git add .")
    print('   git commit -m "refactor(FASE-1.1): integrate NavigationBuilder (-64 lines)"')
    print("   git push origin main")
    
    print("\n4. Se quebrou:")
    print(f"   cp {backup_path} {TARGET_FILE}")
    
    print("")
    
    return 0


if __name__ == "__main__":
    exit(main())
