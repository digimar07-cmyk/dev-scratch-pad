"""
LASERFLIX v3.0 — Camada de Persistência: Database & Config
Responsável por toda a I/O de arquivos JSON (database e config).

Extraído da v7.4.0 para isolar operações de disco do core da aplicação.

Responsabilidades:
- Carregar/salvar database (laserflix_database.json)
- Carregar/salvar config (laserflix_config.json)
- Escrita atômica (tmp + replace) para evitar corrupção
- Backup automático antes de sobrescrever
- Migração de schema legacy (category → categories)
"""

import json
import os
import shutil
from typing import Dict, Any, List
from datetime import datetime

from config import CONFIG_FILE, DB_FILE, LOGGER


def load_config() -> Dict[str, Any]:
    """
    Carrega configurações da aplicação do arquivo JSON.
    
    Estrutura esperada:
    {
        "folders": [lista de paths],
        "models": {dicionário de modelos Ollama}
    }
    
    Returns:
        Dict com configurações. Se arquivo não existir, retorna defaults.
    
    Exemplos:
        >>> config = load_config()
        >>> config['folders']
        ['C:/Projects/Creative_Fabrica', 'C:/Projects/Etsy']
    """
    if not os.path.exists(CONFIG_FILE):
        LOGGER.info("Config não encontrado, retornando defaults")
        return {"folders": [], "models": {}}
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            LOGGER.info("Config carregado: %d pastas, %d modelos", 
                       len(config.get("folders", [])), 
                       len(config.get("models", {})))
            return config
    except Exception as e:
        LOGGER.error("Erro ao carregar config: %s", e, exc_info=True)
        return {"folders": [], "models": {}}


def save_config(folders: List[str], models: Dict[str, str]) -> bool:
    """
    Salva configurações da aplicação no arquivo JSON (escrita atômica).
    
    Args:
        folders: Lista de paths de pastas monitoradas
        models: Dicionário de modelos Ollama ativos
    
    Returns:
        True se salvou com sucesso, False caso contrário
    
    Exemplos:
        >>> save_config(
        ...     folders=['C:/Projects/CF'],
        ...     models={'text_quality': 'qwen2.5:7b'}
        ... )
        True
    """
    config = {"folders": folders, "models": models}
    return _save_json_atomic(CONFIG_FILE, config, make_backup=True)


def load_database() -> Dict[str, Dict[str, Any]]:
    """
    Carrega database de projetos do arquivo JSON.
    
    Estrutura:
    {
        "/path/to/project1": {
            "name": "Easter Bunny Frame",
            "categories": ["Páscoa", "Porta-Retrato", "Quarto"],
            "tags": ["easter", "bunny", "frame"],
            "favorite": false,
            "done": false,
            ...
        },
        ...
    }
    
    Aplica migrações automáticas:
    - Legacy "category" (string) → "categories" (lista)
    
    Returns:
        Dict com database completo. Se arquivo não existir, retorna {}.
    
    Exemplos:
        >>> db = load_database()
        >>> len(db)
        342
        >>> db['/path/to/project1']['name']
        'Easter Bunny Frame'
    """
    if not os.path.exists(DB_FILE):
        LOGGER.info("Database não encontrado, criando novo")
        return {}
    
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            database = json.load(f)
            
        # Migração: category (string) → categories (lista)
        migrated_count = 0
        for path, data in database.items():
            if "category" in data and "categories" not in data:
                old_cat = data.get("category", "")
                data["categories"] = [old_cat] if (old_cat and old_cat != "Sem Categoria") else []
                del data["category"]
                migrated_count += 1
        
        if migrated_count > 0:
            LOGGER.info("Migrado %d projetos: category → categories", migrated_count)
            # Salva database migrado
            _save_json_atomic(DB_FILE, database, make_backup=True)
        
        LOGGER.info("Database carregado: %d projetos", len(database))
        return database
        
    except Exception as e:
        LOGGER.error("Erro ao carregar database: %s", e, exc_info=True)
        return {}


def save_database(database: Dict[str, Dict[str, Any]]) -> bool:
    """
    Salva database de projetos no arquivo JSON (escrita atômica).
    
    Args:
        database: Dict completo do database
    
    Returns:
        True se salvou com sucesso, False caso contrário
    
    Exemplos:
        >>> db = load_database()
        >>> db['/new/project'] = {'name': 'New Project', 'categories': []}
        >>> save_database(db)
        True
    """
    return _save_json_atomic(DB_FILE, database, make_backup=True)


def _save_json_atomic(filepath: str, data: Dict, make_backup: bool = True) -> bool:
    """
    Salva JSON com segurança:
    1. Escreve em arquivo temporário (.tmp)
    2. Cria backup do arquivo atual (.bak) se solicitado
    3. Substitui o arquivo original atomicamente (os.replace)
    
    Garante que nunca teremos um arquivo JSON corrompido pela metade.
    
    Args:
        filepath: Caminho completo do arquivo JSON
        data: Dados para serializar
        make_backup: Se True, cria .bak antes de sobrescrever
    
    Returns:
        True se sucesso, False se falhou
    
    Exemplos:
        >>> _save_json_atomic('test.json', {'key': 'value'}, make_backup=False)
        True
    """
    tmp_file = filepath + ".tmp"
    
    try:
        # 1. Escreve no .tmp
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 2. Backup do original (se existir e solicitado)
        if make_backup and os.path.exists(filepath):
            try:
                shutil.copy2(filepath, filepath + ".bak")
            except Exception as e:
                LOGGER.warning("Falha ao criar .bak de %s: %s", filepath, e)
        
        # 3. Substitui atomicamente
        os.replace(tmp_file, filepath)
        
        LOGGER.debug("JSON salvo com sucesso: %s (%d bytes)", 
                    filepath, os.path.getsize(filepath))
        return True
        
    except Exception as e:
        LOGGER.error("Falha ao salvar JSON atômico %s: %s", filepath, e, exc_info=True)
        
        # Limpa arquivo temporário se sobrou
        try:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        except Exception:
            pass
        
        return False


def create_backup(source_file: str, backup_folder: str) -> bool:
    """
    Cria backup timestamped de um arquivo no folder de backups.
    
    Args:
        source_file: Arquivo fonte (ex: laserflix_database.json)
        backup_folder: Pasta de destino (ex: laserflix_backups)
    
    Returns:
        True se backup criado com sucesso
    
    Exemplos:
        >>> create_backup('laserflix_database.json', 'laserflix_backups')
        True
        # Cria: laserflix_backups/laserflix_database_20260227_180530.json
    """
    if not os.path.exists(source_file):
        LOGGER.warning("Arquivo fonte não existe para backup: %s", source_file)
        return False
    
    try:
        os.makedirs(backup_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(source_file)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_{timestamp}{ext}"
        backup_path = os.path.join(backup_folder, backup_filename)
        
        shutil.copy2(source_file, backup_path)
        LOGGER.info("✅ Backup criado: %s", backup_filename)
        return True
        
    except Exception as e:
        LOGGER.error("Falha ao criar backup de %s: %s", source_file, e, exc_info=True)
        return False


def cleanup_old_backups(backup_folder: str, prefix: str, keep_last: int = 10) -> int:
    """
    Remove backups antigos, mantendo apenas os N mais recentes.
    
    Args:
        backup_folder: Pasta de backups
        prefix: Prefixo dos arquivos de backup (ex: 'auto_backup_')
        keep_last: Quantos backups manter (default: 10)
    
    Returns:
        Número de backups removidos
    
    Exemplos:
        >>> cleanup_old_backups('laserflix_backups', 'auto_backup_', keep_last=5)
        3  # Removeu 3 backups antigos
    """
    try:
        if not os.path.exists(backup_folder):
            return 0
        
        backups = sorted([
            f for f in os.listdir(backup_folder) 
            if f.startswith(prefix)
        ])
        
        if len(backups) <= keep_last:
            return 0
        
        to_remove = backups[:-keep_last]
        removed_count = 0
        
        for backup_file in to_remove:
            try:
                os.remove(os.path.join(backup_folder, backup_file))
                removed_count += 1
            except Exception as e:
                LOGGER.warning("Falha ao remover backup %s: %s", backup_file, e)
        
        if removed_count > 0:
            LOGGER.info("🗑️ Removidos %d backups antigos (mantendo últimos %d)", 
                       removed_count, keep_last)
        
        return removed_count
        
    except Exception as e:
        LOGGER.error("Falha ao limpar backups: %s", e, exc_info=True)
        return 0
