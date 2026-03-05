#!/usr/bin/env python3
"""
translate_all_names.py — Traduz nomes de todos os projetos no banco.

F-01.2: Script one-time para popular name_ptbr em projetos existentes.

Uso:
    python translate_all_names.py

O que faz:
  1. Carrega banco atual
  2. Backup automático
  3. Traduz todos os projetos sem name_ptbr
  4. Salva banco atualizado
  5. Mostra estatísticas
"""
import json
import os
import sys
from datetime import datetime

# Adiciona path do projeto
sys.path.insert(0, os.path.dirname(__file__))

from ai.translator import Translator
from ai.ollama_client import OllamaClient
from utils.logging_setup import LOGGER


def load_database():
    """Carrega banco de dados."""
    db_path = "laserflix_database.json"
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        sys.exit(1)
    
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_database(database):
    """Salva banco de dados."""
    db_path = "laserflix_database.json"
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)


def backup_database():
    """Cria backup do banco antes de modificar."""
    db_path = "laserflix_database.json"
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"laserflix_database_{timestamp}_pre_translate.json")
    
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path


def translate_all_names():
    """
    Traduz nomes de todos os projetos que ainda não têm name_ptbr.
    """
    print("="*70)
    print("  TRADUTOR DE NOMES - Laserflix v3.4.0.0 F-01.2")
    print("="*70)
    print()
    
    # 1. CARREGA BANCO
    print("[1/5] Carregando banco de dados...")
    database = load_database()
    total = len(database)
    print(f"✅ {total} projetos no banco\n")
    
    # 2. BACKUP
    print("[2/5] Criando backup de segurança...")
    backup_path = backup_database()
    print()
    
    # 3. INICIALIZA TRADUTOR
    print("[3/5] Inicializando tradutor...")
    print("➡️  Sistema DUAL ativo:")
    print("   - Dicionário: 1000+ termos especializados")
    print("   - IA (opcional): Ollama (se disponível)")
    
    # Tenta inicializar Ollama (opcional)
    try:
        config = {}
        if os.path.exists("laserflix_config.json"):
            with open("laserflix_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
        
        ollama = OllamaClient(config.get("models"))
        translator = Translator(ollama)
        print("✅ Ollama disponível (tradução híbrida)")
    except Exception as e:
        translator = Translator(None)
        print(f"⚠️  Ollama indisponível, usando só dicionário: {e}")
    
    print()
    
    # 4. IDENTIFICA PROJETOS SEM TRADUÇÃO
    print("[4/5] Identificando projetos sem tradução...")
    to_translate = []
    for path, data in database.items():
        if not data.get("name_ptbr"):
            to_translate.append((path, data))
    
    if not to_translate:
        print("✅ Todos os projetos já têm name_ptbr!")
        print("   Nada a fazer.")
        return
    
    print(f"🔍 Encontrados {len(to_translate)} projetos sem name_ptbr\n")
    
    # 5. TRADUZ
    print(f"[5/5] Traduzindo {len(to_translate)} nomes...")
    print("-" * 70)
    
    translated = 0
    skipped = 0
    
    for i, (path, data) in enumerate(to_translate, 1):
        original_name = data.get("name", os.path.basename(path))
        
        # Progress
        pct = (i / len(to_translate)) * 100
        print(f"[{i}/{len(to_translate)} - {pct:.1f}%] {original_name[:50]}...", end="")
        
        try:
            # Traduz
            translated_name = translator.translate_project_name(original_name)
            
            # Salva
            database[path]["name_ptbr"] = translated_name
            
            # Log se diferente
            if translated_name != original_name:
                print(f" → {translated_name[:40]}")
            else:
                print(" (sem mudança)")
            
            translated += 1
            
            # Salva a cada 10 projetos
            if translated % 10 == 0:
                save_database(database)
        
        except Exception as e:
            print(f" ❌ ERRO: {e}")
            skipped += 1
    
    print("-" * 70)
    print()
    
    # SALVA FINAL
    print("Salvando banco de dados...")
    save_database(database)
    print("✅ Banco salvo com sucesso!\n")
    
    # ESTATÍSTICAS
    print("="*70)
    print("  RESULTADO")
    print("="*70)
    print(f"✅ Traduzidos:  {translated}")
    print(f"❌ Erro/pulado: {skipped}")
    print(f"💾 Backup:      {backup_path}")
    print()
    print("✨ Conclusão: Todos os nomes agora aparecerão traduzidos no modal!")
    print("="*70)


if __name__ == "__main__":
    try:
        translate_all_names()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO FATAL: {e}")
        LOGGER.exception("Erro ao traduzir nomes")
        sys.exit(1)
