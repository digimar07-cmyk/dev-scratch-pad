"""
utils/duplicate_detector.py - Detector de Duplicatas PRECISO

KENT BECK STYLE:
  1. Simple Design - Compare EXATAMENTE o que o usuário vê (nome completo)
  2. Reveal Intent - "is_duplicate" é óbvio, sem mágica
  3. No Duplication - DRY na normalização
  4. Minimal Elements - Apenas o necessário

REGRAS (conforme solicitação):
  ✔️ DUPLICADO se nome COMPLETO é idêntico:
     - Nursery-Name-Sign-Laser-Cut
     - Nursery-Name-Sign-Laser-Cut
  
  ✔️ DUPLICADO se nome COMPLETO com espaços é idêntico:
     - Nursery Name Sign Laser Cut
     - Nursery Name Sign Laser Cut
  
  ✔️ DUPLICADO se nome COMPLETO com código é idêntico:
     - Nursery-Name-Sign-Laser-Cut-134888530
     - Nursery-Name-Sign-Laser-Cut-134888530
  
  ❌ NÃO DUPLICADO se códigos diferentes:
     - Nursery-Name-Sign-Laser-Cut-134888530
     - Nursery-Name-Sign-Laser-Cut-134888536  ← PRODUTOS DIFERENTES!
  
  ❌ NÃO DUPLICADO se qualquer diferença:
     - Nursery Name Sign Laser Cut 134888530
     - Nursery Name Sign Laser Cut 134888536  ← PRODUTOS DIFERENTES!

NORMALIZAÇÃO (apenas para consistência):
  - Case insensitive (Nursery = nursery)
  - Espaços múltiplos -> 1 espaço
  - Strip espaços laterais
  - Hifens/underscores -> espaços (para comparar)
  - MAS: CÓDIGOS NUMÉRICOS SÃO PRESERVADOS!
"""
import os
import re
from collections import defaultdict
from typing import Dict, List, Set
from utils.logging_setup import LOGGER


class DuplicateDetector:
    """
    Detector de duplicatas baseado em NOME COMPLETO da pasta.
    
    FILOSOFIA KENT BECK:
    "The code should say what it does, and do what it says."
    
    Este detector faz EXATAMENTE o que o nome diz:
    - Compara nomes COMPLETOS
    - Ignora APENAS case e espaçamentos
    - PRESERVA códigos numéricos
    """

    def __init__(self):
        self.logger = LOGGER

    def normalize_folder_name(self, folder_name: str) -> str:
        """
        Normaliza nome da pasta para comparação.
        
        REGRAS:
        1. Lowercase (case insensitive)
        2. Hifens/underscores -> espaços
        3. Espaços múltiplos -> 1 espaço
        4. Strip laterais
        5. PRESERVA códigos numéricos (CRUCIAL!)
        
        EXEMPLOS:
        >>> normalize_folder_name("Nursery-Name-Sign-Laser-Cut-134888530")
        "nursery name sign laser cut 134888530"
        
        >>> normalize_folder_name("Nursery-Name-Sign-Laser-Cut-134888536")
        "nursery name sign laser cut 134888536"
        
        >>> normalize_folder_name("Nursery Name Sign Laser Cut")
        "nursery name sign laser cut"
        
        Args:
            folder_name: Nome da pasta (raw)
        
        Returns:
            Nome normalizado para comparação
        """
        # 1. Lowercase
        normalized = folder_name.lower()
        
        # 2. Hifens/underscores -> espaços
        normalized = normalized.replace("-", " ").replace("_", " ")
        
        # 3. Espaços múltiplos -> 1 espaço
        normalized = re.sub(r"\s+", " ", normalized)
        
        # 4. Strip laterais
        normalized = normalized.strip()
        
        # 5. PRESERVA códigos numéricos (NÃO REMOVE NADA!)
        # Antes (bugado): clean = re.sub(r"[-_]\d{5,}", "", clean)
        # Depois (correto): PRESERVA TUDO!
        
        return normalized

    def find_duplicates(self, database: Dict[str, dict]) -> Dict[str, List[str]]:
        """
        Encontra grupos de duplicatas no banco.
        
        ALGORITMO:
        1. Normaliza todos os nomes
        2. Agrupa por nome normalizado
        3. Retorna apenas grupos com 2+ itens
        
        Args:
            database: Dict {path: project_data}
        
        Returns:
            Dict {normalized_name: [path1, path2, ...]}
            Apenas grupos com 2+ itens (duplicatas)
        
        EXEMPLO:
        {
            "nursery name sign laser cut": [
                "/path/Nursery-Name-Sign-Laser-Cut",
                "/path/Nursery_Name_Sign_Laser_Cut",
            ],
            # NOTA: Códigos diferentes NÃO aparecem aqui:
            # "nursery name sign laser cut 134888530" -> 1 item (não duplicata)
            # "nursery name sign laser cut 134888536" -> 1 item (não duplicata)
        }
        """
        # Agrupa por nome normalizado
        groups = defaultdict(list)
        
        for path in database.keys():
            folder_name = os.path.basename(path)
            normalized = self.normalize_folder_name(folder_name)
            groups[normalized].append(path)
        
        # Filtra apenas grupos com 2+ itens (duplicatas)
        duplicates = {
            norm_name: paths
            for norm_name, paths in groups.items()
            if len(paths) >= 2
        }
        
        self.logger.info(
            f"🔍 Duplicatas encontradas: {len(duplicates)} grupos, "
            f"{sum(len(paths) for paths in duplicates.values())} projetos afetados"
        )
        
        return duplicates

    def is_duplicate(self, path1: str, path2: str) -> bool:
        """
        Verifica se 2 paths são duplicatas.
        
        SIMPLES E DIRETO (Kent Beck):
        - Pega nome completo da pasta
        - Normaliza ambos
        - Compara
        
        Args:
            path1: Caminho completo do projeto 1
            path2: Caminho completo do projeto 2
        
        Returns:
            True se duplicata, False caso contrário
        
        EXEMPLOS:
        >>> is_duplicate(
        ...     "/path/Nursery-Name-Sign-Laser-Cut-134888530",
        ...     "/path/Nursery-Name-Sign-Laser-Cut-134888536"
        ... )
        False  # ← Códigos diferentes = produtos diferentes!
        
        >>> is_duplicate(
        ...     "/path/Nursery-Name-Sign-Laser-Cut",
        ...     "/path/Nursery_Name_Sign_Laser_Cut"
        ... )
        True  # ← Mesmo nome, apenas hifens vs underscores
        """
        name1 = os.path.basename(path1)
        name2 = os.path.basename(path2)
        
        norm1 = self.normalize_folder_name(name1)
        norm2 = self.normalize_folder_name(name2)
        
        return norm1 == norm2

    def get_duplicate_summary(self, database: Dict[str, dict]) -> dict:
        """
        Retorna resumo estatístico de duplicatas.
        
        Returns:
            Dict com estatísticas:
            - total_projects: Total de projetos
            - duplicate_groups: Número de grupos de duplicatas
            - duplicate_count: Total de projetos duplicados
            - examples: Lista de exemplos (até 5 grupos)
        """
        duplicates = self.find_duplicates(database)
        
        total_duplicates = sum(len(paths) for paths in duplicates.values())
        
        # Pega exemplos (até 5 grupos)
        examples = []
        for norm_name, paths in list(duplicates.items())[:5]:
            examples.append({
                "normalized_name": norm_name,
                "count": len(paths),
                "paths": [os.path.basename(p) for p in paths],
            })
        
        return {
            "total_projects": len(database),
            "duplicate_groups": len(duplicates),
            "duplicate_count": total_duplicates,
            "examples": examples,
        }


# =========================================================================
# TESTES UNITÁRIOS (Kent Beck: "Test First!")
# =========================================================================

if __name__ == "__main__":
    """
    Testes rápidos para validar lógica.
    """
    detector = DuplicateDetector()
    
    print("✅ TESTES DE NORMALIZAÇÃO:")
    
    # Teste 1: Preserva códigos
    assert detector.normalize_folder_name("Nursery-Name-Sign-Laser-Cut-134888530") == \
           "nursery name sign laser cut 134888530"
    print("  ✓ Preserva códigos numéricos")
    
    # Teste 2: Hifens vs underscores
    assert detector.normalize_folder_name("Nursery-Name-Sign") == \
           detector.normalize_folder_name("Nursery_Name_Sign")
    print("  ✓ Hifens = underscores")
    
    # Teste 3: Case insensitive
    assert detector.normalize_folder_name("Nursery Name Sign") == \
           detector.normalize_folder_name("nursery name sign")
    print("  ✓ Case insensitive")
    
    print("\n✅ TESTES DE DUPLICATAS:")
    
    # Teste 4: Códigos diferentes = NÃO duplicata
    assert not detector.is_duplicate(
        "/path/Nursery-Name-Sign-Laser-Cut-134888530",
        "/path/Nursery-Name-Sign-Laser-Cut-134888536"
    )
    print("  ✓ Códigos diferentes = produtos diferentes")
    
    # Teste 5: Mesmo nome = duplicata
    assert detector.is_duplicate(
        "/path/Nursery-Name-Sign-Laser-Cut",
        "/path/Nursery_Name_Sign_Laser_Cut"
    )
    print("  ✓ Mesmo nome = duplicata")
    
    # Teste 6: Mesmo nome + código = duplicata
    assert detector.is_duplicate(
        "/path/Nursery-Name-Sign-Laser-Cut-134888530",
        "/path/Nursery_Name_Sign_Laser_Cut_134888530"
    )
    print("  ✓ Mesmo nome + código = duplicata")
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
