#!/usr/bin/env python3
"""
Teste de Validação de Imports
Verifica estrutura modular sem executar a UI
"""

import sys
import importlib
from pathlib import Path

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def test_module(module_path, description):
    """Testa import de um módulo"""
    try:
        mod = importlib.import_module(module_path)
        print(f"{GREEN}✓{RESET} {description:<50} {BLUE}{module_path}{RESET}")
        return True, mod
    except ImportError as e:
        print(f"{RED}✗{RESET} {description:<50} {RED}{e}{RESET}")
        return False, None
    except Exception as e:
        print(f"{YELLOW}⚠{RESET} {description:<50} {YELLOW}{e}{RESET}")
        return False, None

def test_class_instantiation(module, class_name, description):
    """Testa se uma classe pode ser instanciada (sem executar)"""
    try:
        cls = getattr(module, class_name)
        print(f"  {GREEN}✓{RESET} {description:<48} {class_name}")
        return True
    except AttributeError:
        print(f"  {RED}✗{RESET} {description:<48} {RED}{class_name} não encontrada{RESET}")
        return False
    except Exception as e:
        print(f"  {YELLOW}⚠{RESET} {description:<48} {YELLOW}{e}{RESET}")
        return False

def main():
    print("\n" + "="*80)
    print(f"{BLUE}LASERFLIX - Teste de Validação de Módulos{RESET}")
    print("="*80 + "\n")

    results = {"success": 0, "failed": 0}

    # ========================================================================
    print(f"\n{YELLOW}[•] CORE MODULES{RESET}")
    print("-" * 80)
    
    success, db_mod = test_module("laserflix.core.database", "Database")
    if success:
        results["success"] += 1
        test_class_instantiation(db_mod, "Database", "Classe Database")
    else:
        results["failed"] += 1

    success, backup_mod = test_module("laserflix.core.backup", "Backup Manager")
    if success:
        results["success"] += 1
        test_class_instantiation(backup_mod, "BackupManager", "Classe BackupManager")
    else:
        results["failed"] += 1

    success, config_mod = test_module("laserflix.core.config", "Config")
    if success:
        results["success"] += 1
        test_class_instantiation(config_mod, "Config", "Classe Config")
    else:
        results["failed"] += 1

    success, filter_mod = test_module("laserflix.core.filter", "Filter")
    if success:
        results["success"] += 1
        test_class_instantiation(filter_mod, "Filter", "Classe Filter")
    else:
        results["failed"] += 1

    # ========================================================================
    print(f"\n{YELLOW}[•] OLLAMA MODULES{RESET}")
    print("-" * 80)

    success, client_mod = test_module("laserflix.ollama.client", "Ollama Client")
    if success:
        results["success"] += 1
        test_class_instantiation(client_mod, "OllamaClient", "Classe OllamaClient")
    else:
        results["failed"] += 1

    success, vision_mod = test_module("laserflix.ollama.vision", "Vision")
    if success:
        results["success"] += 1
        test_class_instantiation(vision_mod, "VisionAnalyzer", "Classe VisionAnalyzer")
    else:
        results["failed"] += 1

    success, analyzer_mod = test_module("laserflix.ollama.analyzer", "Analyzer")
    if success:
        results["success"] += 1
        test_class_instantiation(analyzer_mod, "ProjectAnalyzer", "Classe ProjectAnalyzer")
    else:
        results["failed"] += 1

    success, desc_mod = test_module("laserflix.ollama.description", "Description Generator")
    if success:
        results["success"] += 1
        test_class_instantiation(desc_mod, "DescriptionGenerator", "Classe DescriptionGenerator")
    else:
        results["failed"] += 1

    # ========================================================================
    print(f"\n{YELLOW}[•] MEDIA MODULES{RESET}")
    print("-" * 80)

    success, thumb_mod = test_module("laserflix.media.thumbnails", "Thumbnails")
    if success:
        results["success"] += 1
        test_class_instantiation(thumb_mod, "ThumbnailCache", "Classe ThumbnailCache")
    else:
        results["failed"] += 1

    success, files_mod = test_module("laserflix.media.files", "Files")
    if success:
        results["success"] += 1
        test_class_instantiation(files_mod, "FileAnalyzer", "Classe FileAnalyzer")
    else:
        results["failed"] += 1

    # ========================================================================
    print(f"\n{YELLOW}[•] UI MODULES{RESET}")
    print("-" * 80)

    success, mw_mod = test_module("laserflix.ui.main_window", "Main Window")
    if success:
        results["success"] += 1
        test_class_instantiation(mw_mod, "MainWindow", "Classe MainWindow")
    else:
        results["failed"] += 1

    success, sb_mod = test_module("laserflix.ui.sidebar", "Sidebar")
    if success:
        results["success"] += 1
        test_class_instantiation(sb_mod, "SidebarManager", "Classe SidebarManager")
    else:
        results["failed"] += 1

    success, card_mod = test_module("laserflix.ui.project_card", "Project Card")
    if success:
        results["success"] += 1
        test_class_instantiation(card_mod, "ProjectCard", "Classe ProjectCard")
    else:
        results["failed"] += 1

    # ========================================================================
    print(f"\n{YELLOW}[•] WORKERS MODULES{RESET}")
    print("-" * 80)

    success, worker_mod = test_module("laserflix.workers.analysis", "Analysis Worker")
    if success:
        results["success"] += 1
        test_class_instantiation(worker_mod, "AnalysisWorker", "Classe AnalysisWorker")
    else:
        results["failed"] += 1

    # ========================================================================
    print(f"\n{YELLOW}[•] APP CORE{RESET}")
    print("-" * 80)

    success, app_mod = test_module("laserflix.core.app", "Laserflix App")
    if success:
        results["success"] += 1
        test_class_instantiation(app_mod, "LaserflixApp", "Classe LaserflixApp")
    else:
        results["failed"] += 1

    # ========================================================================
    print(f"\n{YELLOW}[•] VERIFICAÇÃO DE ESTRUTURA{RESET}")
    print("-" * 80)

    # Verifica existência de arquivos
    base_path = Path("laserflix")
    required_files = [
        "core/__init__.py",
        "ollama/__init__.py",
        "media/__init__.py",
        "ui/__init__.py",
        "workers/__init__.py",
    ]

    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"{GREEN}✓{RESET} Arquivo existe: {file_path}")
        else:
            print(f"{RED}✗{RESET} Arquivo faltando: {file_path}")
            results["failed"] += 1

    # ========================================================================
    print("\n" + "="*80)
    total = results["success"] + results["failed"]
    success_rate = (results["success"] / total * 100) if total > 0 else 0
    
    if results["failed"] == 0:
        print(f"{GREEN}✓ TODOS OS TESTES PASSARAM!{RESET}")
    else:
        print(f"{YELLOW}⚠ {results['failed']} teste(s) falharam{RESET}")
    
    print(f"\nResultado: {results['success']}/{total} ({success_rate:.1f}%)")
    print("="*80 + "\n")

    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
