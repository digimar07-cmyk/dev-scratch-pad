#!/usr/bin/env python3
"""
REFACTOR_AUTO_FASE_1B.py — Script automático para FASE-1B

O que faz:
1. Adiciona import do NavigationBuilder
2. Simplifica método _build_navigation_controls() (70 linhas → 3 linhas)
3. Remove código duplicado de navegação/ordenação
4. Cria backup automático
5. Valida sintaxe Python

Redução esperada: ~67 linhas (609 → 542)

Uso:
    python REFACTOR_AUTO_FASE_1B.py
"""

import os
import re
import ast
import shutil
from datetime import datetime

# Configurações
TARGET_FILE = "ui/main_window.py"
BACKUP_SUFFIX = ".backup_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S"))


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
        print(f"❌ Erro de sintaxe: {e}")
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
    print(f"✅ Backup criado: {backup_path}")
    return backup_path


def refactor_main_window(content: str) -> str:
    """
    Refatora main_window.py para usar NavigationBuilder.
    
    Args:
        content: Conteúdo original do arquivo
        
    Returns:
        Conteúdo refatorado
    """
    # PASSO 1: Adicionar import do NavigationBuilder
    print("\n🔧 PASSO 1: Adicionando import do NavigationBuilder...")
    
    # Encontrar a linha com UIBuilder import
    ui_builder_pattern = r"(from ui\.builders\.ui_builder import UIBuilder)"
    
    if not re.search(ui_builder_pattern, content):
        print("❌ Erro: Não encontrei import do UIBuilder")
        return content
    
    # Adicionar import do NavigationBuilder logo após UIBuilder
    content = re.sub(
        ui_builder_pattern,
        r"\1\nfrom ui.builders.navigation_builder import NavigationBuilder",
        content
    )
    print("✅ Import adicionado")
    
    # PASSO 2: Simplificar método _build_navigation_controls()
    print("\n🔧 PASSO 2: Simplificando _build_navigation_controls()...")
    
    # Padrão: encontrar o método inteiro (linhas 317-379)
    old_method_pattern = r'(    def _build_navigation_controls\(self, parent: tk\.Frame, page_info: dict\) -> None:\s*'
    old_method_pattern += r'"""Constrói controles de ordenação \+ navegação \(FASE-1C\)\."""\s*'
    old_method_pattern += r'right_controls = tk\.Frame\(parent, bg=BG_PRIMARY\).*?'
    old_method_pattern += r'state="normal" if page_info\["current_page"\] < page_info\["total_pages"\] else "disabled"'
    old_method_pattern += r'\s*\)\.pack\(side="left", padx=1\))'
    
    # Novo método simplificado
    new_method = '''    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:
        """Constrói controles de ordenação + navegação usando NavigationBuilder (FASE-1B)."""  
        NavigationBuilder.build(parent, page_info, self.display_ctrl)'''
    
    # Tentar substituição com regex complexo
    content_temp = re.sub(old_method_pattern, new_method, content, flags=re.DOTALL)
    
    if content_temp == content:
        # Se regex falhou, usar abordagem de linhas
        print("⚠️  Regex falhou, usando abordagem de linhas...")
        lines = content.split('\n')
        new_lines = []
        skip_until_next_def = False
        found_method = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detectar início do método
            if '    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:' in line:
                found_method = True
                skip_until_next_def = True
                # Adicionar método novo
                new_lines.append('    def _build_navigation_controls(self, parent: tk.Frame, page_info: dict) -> None:')
                new_lines.append('        """Constrói controles de ordenação + navegação usando NavigationBuilder (FASE-1B)."""')
                new_lines.append('        NavigationBuilder.build(parent, page_info, self.display_ctrl)')
                i += 1
                continue
            
            # Pular linhas do método antigo até próximo def
            if skip_until_next_def:
                # Verificar se chegou no próximo método
                if line.strip().startswith('def ') and i > 0:
                    skip_until_next_def = False
                    new_lines.append('')  # Linha em branco antes do próximo método
                    new_lines.append(line)
                else:
                    i += 1
                    continue
            else:
                new_lines.append(line)
            
            i += 1
        
        if not found_method:
            print("❌ Erro: Método _build_navigation_controls() não encontrado")
            return content
        
        content = '\n'.join(new_lines)
        print("✅ Método simplificado (abordagem de linhas)")
    else:
        content = content_temp
        print("✅ Método simplificado (regex)")
    
    # PASSO 3: Atualizar comentário do header
    print("\n🔧 PASSO 3: Atualizando comentário do header...")
    content = re.sub(
        r'REFACTOR-FASE-1C: _build_navigation_controls\(\) extraído ✅',
        'REFACTOR-FASE-1B: NavigationBuilder extraído ✅',
        content
    )
    print("✅ Header atualizado")
    
    return content


def main():
    """
    Função principal do script.
    """
    print("=" * 70)
    print("🚀 REFACTORAÇÃO AUTOMÁTICA - FASE-1B")
    print("=" * 70)
    print("\n🎯 Objetivo: Integrar NavigationBuilder")
    print("📏 Redução esperada: ~67 linhas (609 → 542)")
    print("\n" + "=" * 70)
    
    # Verificar se arquivo existe
    if not os.path.exists(TARGET_FILE):
        print(f"\n❌ Erro: Arquivo {TARGET_FILE} não encontrado!")
        print("\n💡 Dica: Execute o script da raiz do projeto:")
        print("   cd laserflix_v3.4.4.0_Stable")
        print("   python REFACTOR_AUTO_FASE_1B.py")
        return 1
    
    # Ler arquivo original
    print(f"\n📝 Lendo {TARGET_FILE}...")
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    original_lines = len(original_content.split('\n'))
    print(f"✅ Arquivo lido: {original_lines} linhas")
    
    # Criar backup
    print(f"\n💾 Criando backup...")
    backup_path = create_backup(TARGET_FILE)
    
    # Refatorar
    print(f"\n🔧 Iniciando refatoração...")
    refactored_content = refactor_main_window(original_content)
    
    # Validar sintaxe
    print(f"\n✅ Validando sintaxe Python...")
    if not validate_python_syntax(refactored_content):
        print("\n❌ Erro: Código inválido gerado!")
        print(f"💾 Backup disponível em: {backup_path}")
        return 1
    
    print("✅ Sintaxe válida!")
    
    # Escrever arquivo refatorado
    print(f"\n💾 Salvando arquivo refatorado...")
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.write(refactored_content)
    
    refactored_lines = len(refactored_content.split('\n'))
    reduction = original_lines - refactored_lines
    
    print("✅ Arquivo salvo!")
    
    # Resumo
    print("\n" + "=" * 70)
    print("🎉 REFACTORAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print(f"\n📊 Estatísticas:")
    print(f"   Linhas originais: {original_lines}")
    print(f"   Linhas refatoradas: {refactored_lines}")
    print(f"   Redução: {reduction} linhas ({(reduction/original_lines*100):.1f}%)")
    print(f"\n💾 Backup: {backup_path}")
    print(f"\n✅ Arquivo atualizado: {TARGET_FILE}")
    
    print("\n" + "=" * 70)
    print("👉 PRÓXIMOS PASSOS:")
    print("=" * 70)
    print("\n1. Testar o app:")
    print("   python main.py")
    print("\n2. Verificar se navegação funciona:")
    print("   - Combobox de ordenação muda ordem")
    print("   - Botões ⏮ ◀ ▶ ⏭ navegam entre páginas")
    print("   - Label 'Pág X/Y' atualiza corretamente")
    print("\n3. Se funcionar:")
    print("   git add .")
    print('   git commit -m "refactor(FASE-1B): integrate NavigationBuilder (-67 lines)"')
    print("   git push origin main")
    print("\n4. Se quebrou:")
    print(f"   cp {backup_path} {TARGET_FILE}")
    print("")
    
    return 0


if __name__ == "__main__":
    exit(main())
