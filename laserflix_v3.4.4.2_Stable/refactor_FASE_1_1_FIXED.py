#!/usr/bin/env python3
"""
refactor_FASE_1_1_FIXED.py — Script cirúrgico CORRETO para FASE-1.1

ABORDAGEM CORRETA:
- Usa análise de INDENTAÇÃO (não marcadores de linha)
- Detecta início/fim do método por nível de indentação
- Substitui BLOCO COMPLETO sem quebrar código adjacente

O que faz:
1. Localiza método _build_navigation_controls() por indentação
2. Captura TODO o bloco (até próximo método ou fim de indentação)
3. Substitui por versão simplificada que usa NavigationBuilder
4. Cria backup automático
5. Valida sintaxe Python
6. Mostra diff real

Redução: ~64 linhas (609 → 545)

Uso:
    cd laserflix_v3.4.4.0_Stable
    python refactor_FASE_1_1_FIXED.py
"""

import os
import ast
import shutil
import difflib
from datetime import datetime
from typing import Tuple, List

# Configurações
TARGET_FILE = "ui/main_window.py"
BACKUP_SUFFIX = ".backup_FASE_1_1_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S"))

# Assinatura do método a ser substituído
METHOD_SIGNATURE = "def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:"

# Novo método (simplificado)
NEW_METHOD = '''    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:
        """Constrói controles de ordenação + navegação usando NavigationBuilder (FASE-1.1)."""
        from ui.builders.navigation_builder import NavigationBuilder
        NavigationBuilder.build(parent, page_info, self.display_ctrl)
'''


def get_indentation(line: str) -> int:
    """
    Retorna o nível de indentação da linha (número de espaços no início).
    
    Args:
        line: Linha de código
        
    Returns:
        Número de espaços de indentação
    """
    return len(line) - len(line.lstrip())


def find_method_block(lines: List[str], method_signature: str) -> Tuple[int, int]:
    """
    Encontra o início e fim de um método por análise de indentação.
    
    Args:
        lines: Lista de linhas do arquivo
        method_signature: Assinatura do método a procurar
        
    Returns:
        Tupla (start_line, end_line) ou (-1, -1) se não encontrado
    """
    start_line = -1
    
    # Encontrar linha de início
    for i, line in enumerate(lines):
        if method_signature in line:
            start_line = i
            break
    
    if start_line == -1:
        return (-1, -1)
    
    # Nível de indentação base do método (deve ser 4 espaços para métodos de classe)
    base_indent = get_indentation(lines[start_line])
    
    # Encontrar linha de fim
    end_line = start_line + 1
    
    while end_line < len(lines):
        line = lines[end_line]
        
        # Linha vazia: continua
        if not line.strip():
            end_line += 1
            continue
        
        current_indent = get_indentation(line)
        
        # Se indentação voltou ao nível base (ou menor), acabou o método
        if current_indent <= base_indent:
            # Verificar se é início de novo método ou fim da classe
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                # Voltar para a linha anterior (última linha do método anterior)
                end_line -= 1
                # Pular linhas vazias ao final
                while end_line > start_line and not lines[end_line].strip():
                    end_line -= 1
                break
        
        end_line += 1
    
    # Ajustar end_line para incluir a última linha do método
    if end_line >= len(lines):
        end_line = len(lines) - 1
    
    return (start_line, end_line)


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
        if e.text:
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
    diff = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (refatorado)",
        lineterm=''
    ))
    
    if not diff:
        print("❌ Nenhuma mudança detectada!")
        return
    
    print("\n" + "=" * 80)
    print("📋 DIFF DAS MUDANÇAS")
    print("=" * 80)
    print()
    
    # Mostrar contexto relevante (limitar a 60 linhas)
    for i, line in enumerate(diff):
        if i >= 60:
            print(f"\n... (mais {len(diff) - 60} linhas de diff)")
            break
        
        if line.startswith('+') and not line.startswith('+++'):
            print(f"\033[92m{line}\033[0m", end='')  # Verde
        elif line.startswith('-') and not line.startswith('---'):
            print(f"\033[91m{line}\033[0m", end='')  # Vermelho
        elif line.startswith('@@'):
            print(f"\033[94m{line}\033[0m", end='')  # Azul
        else:
            print(line, end='')


def refactor_main_window(content: str) -> Tuple[str, int, int]:
    """
    Refatora main_window.py substituindo _build_navigation_controls().
    
    Args:
        content: Conteúdo original do arquivo
        
    Returns:
        Tupla (conteúdo_refatorado, linhas_removidas, linhas_adicionadas)
    """
    lines = content.split('\n')
    
    # Encontrar bloco do método
    start_line, end_line = find_method_block(lines, METHOD_SIGNATURE)
    
    if start_line == -1:
        print("\n❌ ERRO: Método _build_navigation_controls() NÃO encontrado!")
        return content, 0, 0
    
    print(f"\n✓ Método encontrado: linhas {start_line + 1} a {end_line + 1}")
    print(f"✓ Total de linhas do método: {end_line - start_line + 1}")
    
    # Contar linhas do método antigo
    lines_removed = end_line - start_line + 1
    
    # Construir novo conteúdo
    new_lines = []
    
    # Adicionar linhas ANTES do método
    new_lines.extend(lines[:start_line])
    
    # Adicionar método NOVO
    new_method_lines = NEW_METHOD.rstrip().split('\n')
    new_lines.extend(new_method_lines)
    
    # Adicionar linhas DEPOIS do método
    new_lines.extend(lines[end_line + 1:])
    
    # Contar linhas adicionadas
    lines_added = len(new_method_lines)
    
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
    print("🚀 REFATORAÇÃO CIRÚRGICA - FASE-1.1 (VERSÃO CORRIGIDA)")
    print("=" * 80)
    print("\n🎯 Objetivo: Extrair _build_navigation_controls() → NavigationBuilder")
    print("📉 Redução esperada: ~64 linhas (609 → 545)")
    print("✅ Método: Análise de INDENTAÇÃO (não marcadores)")
    print("\n" + "=" * 80)
    
    # Verificar se arquivo existe
    if not os.path.exists(TARGET_FILE):
        print(f"\n❌ ERRO: Arquivo {TARGET_FILE} não encontrado!")
        print("\n💡 Dica: Execute o script da raiz do projeto:")
        print("   cd laserflix_v3.4.4.0_Stable")
        print("   python refactor_FASE_1_1_FIXED.py")
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
    print("   ✓ Cards aparecem após importação")
    print("   ✓ Combobox de ordenação funciona")
    print("   ✓ Botões ⏮ ◀ ▶ ⏭ navegam páginas")
    print("   ✓ Label 'Pág X/Y' atualiza")
    
    print("\n3. Se funcionar:")
    print("   git add .")
    print('   git commit -m "refactor(FASE-1.1): integrate NavigationBuilder (-64 lines)"')
    print("   git push origin main")
    
    print("\n4. Se quebrou:")
    print(f"   cp {backup_path} {TARGET_FILE}")
    print("   python main.py  # testar se voltou ao normal")
    
    print("")
    
    return 0


if __name__ == "__main__":
    exit(main())
