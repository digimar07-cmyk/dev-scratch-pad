# ⚠️ REGRA ABSOLUTA E INATACÁVEL - LIMITES DE TAMANHO DE ARQUIVO

## 🔴 ESTA REGRA É INVIOLÁVEL - NENHUMA EXCEÇÃO PERMITIDA

### LIMITES MÁXIMOS POR ARQUIVO (LINHAS DE CÓDIGO)

```
main_window.py           : 200 linhas (MÁXIMO ABSOLUTO)
project_card.py          : 150 linhas (MÁXIMO ABSOLUTO)
project_modal.py         : 250 linhas (MÁXIMO ABSOLUTO)
header.py                : 150 linhas (MÁXIMO ABSOLUTO)
sidebar.py               : 200 linhas (MÁXIMO ABSOLUTO)
QUALQUER OUTRO ARQUIVO UI: 300 linhas (MÁXIMO ABSOLUTO)
```

---

## ❌ PROIBIÇÕES ABSOLUTAS

### 1. **NUNCA ADICIONAR CÓDIGO DIRETAMENTE AO `main_window.py`**

- ✅ PERMITIDO: Chamar métodos de controllers
- ❌ PROIBIDO: Implementar lógica diretamente no main_window.py
- ❌ PROIBIDO: Adicionar novos métodos longos (>10 linhas)
- ❌ PROIBIDO: Callbacks inline complexos

### 2. **ANTES DE ADICIONAR QUALQUER FEATURE**

```python
# CHECKLIST OBRIGATÓRIO:
1. main_window.py tem < 200 linhas? ✓
2. Feature nova exige controller? → CRIAR CONTROLLER PRIMEIRO
3. Feature nova exige componente? → CRIAR COMPONENTE PRIMEIRO
4. Método tem > 20 linhas? → EXTRAIR PARA CLASSE SEPARADA
5. Arquivo passa de 80% do limite? → REFATORAR ANTES
```

### 3. **SE ARQUIVO PASSAR DO LIMITE**

```bash
🚨 AÇÃO OBRIGATÓRIA IMEDIATA:

1. PARAR TODO DESENVOLVIMENTO
2. EXTRAIR código para controllers/components
3. REDUZIR arquivo para 70% do limite
4. DOCUMENTAR extração no commit
5. SÓ ENTÃO continuar feature
```

---

## 🏗️ ARQUITETURA OBRIGATÓRIA

### **main_window.py DEVE CONTER APENAS:**

```python
class LaserflixMainWindow:
    def __init__(self):      # Instancia controllers
        self.display_ctrl = DisplayController(...)
        self.analysis_ctrl = AnalysisController(...)
        self.collection_ctrl = CollectionController(...)
    
    def _build_ui(self):     # Monta UI (delega para components)
        self.header = HeaderBar(...)
        self.sidebar = SidebarPanel(...)
    
    # Callbacks SIMPLES (1-3 linhas) que delegam
    def on_filter(self, f):
        self.display_ctrl.set_filter(f)
```

**TOTAL: ~150 linhas**

---

### **CONTROLLERS (onde a lógica vai)**

```
ui/controllers/
├── display_controller.py   # Filtros, ordenação, paginação
├── analysis_controller.py  # Análise AI, descrições, tradução
├── collection_controller.py # Coleções, add/remove
└── selection_controller.py  # Modo seleção, bulk operations
```

### **COMPONENTS (widgets reutilizáveis)**

```
ui/components/
├── chips_bar.py            # Barra de filtros ativos
├── status_bar.py           # Barra de status + progress
├── selection_bar.py        # Barra de seleção múltipla
└── pagination_controls.py  # Controles de página
```

---

## 📏 COMO MEDIR TAMANHO

```bash
# Conta apenas linhas de código (exclui comentários/espaços)
wc -l ui/main_window.py

# OU no Python:
import os
with open('ui/main_window.py') as f:
    lines = [l for l in f if l.strip() and not l.strip().startswith('#')]
    print(f"Linhas de código: {len(lines)}")
```

---

## 🚨 CONSEQUÊNCIAS DE VIOLAÇÃO

### **SE ARQUIVO PASSAR DE 250 LINHAS:**

1. **DESENVOLVIMENTO CONGELADO**
2. **ROLLBACK FORÇADO** do último commit
3. **REFATORAÇÃO OBRIGATÓRIA** antes de continuar
4. **NENHUMA FEATURE NOVA** até resolver

### **SE ARQUIVO PASSAR DE 300 LINHAS:**

1. **CÓDIGO REJEITADO**
2. **REVERT COMPLETO** da branch
3. **REESCREVER** do zero com arquitetura correta

---

## ✅ EXEMPLO DE EXTRAÇÃO CORRETA

### ❌ ANTES (ERRADO - código no main_window.py):

```python
class LaserflixMainWindow:
    def translate_all_names(self):
        # 80 linhas de lógica aqui... ❌
        targets = [...]
        for path, name in targets:
            # processamento...
            # salva database...
            # atualiza UI...
```

### ✅ DEPOIS (CORRETO - delegado para controller):

```python
# ui/main_window.py
class LaserflixMainWindow:
    def translate_all_names(self):
        self.analysis_ctrl.translate_names()  # 1 linha! ✓

# ui/controllers/analysis_controller.py (NOVO ARQUIVO)
class AnalysisController:
    def translate_names(self):
        # 80 linhas aqui (separado) ✓
```

---

## 📋 CHECKLIST PRÉ-COMMIT

```bash
☐ main_window.py < 200 linhas?
☐ Nenhum arquivo UI > limite?
☐ Lógica complexa em controllers?
☐ Componentes UI reutilizáveis extraídos?
☐ Callbacks delegam para controllers?
☐ Código segue arquitetura MVC/MVVM?

✅ TODOS checados? → PODE COMMITAR
❌ Algum falhou? → REFATORAR PRIMEIRO
```

---

## 🎯 RESUMO EXECUTIVO

```
1. main_window.py = ORQUESTRADOR (< 200 linhas)
2. LÓGICA = CONTROLLERS (arquivos separados)
3. UI = COMPONENTS (widgets reutilizáveis)
4. LIMITE VIOLADO = PARAR + REFATORAR
5. SEM EXCEÇÕES, SEM DESCULPAS
```

---

## ⚡ ESTA REGRA É:

- ✅ **ABSOLUTA**: Nenhuma exceção
- ✅ **INATACÁVEL**: Não pode ser ignorada
- ✅ **INVIOLÁVEL**: Quebrar = rollback forçado
- ✅ **REDUNDANTE**: Repetida em TODOS os .md
- ✅ **AUTOMÁTICA**: Checada antes de cada commit

---

**ÚLTIMA ATUALIZAÇÃO**: 2026-03-06  
**VERSÃO**: 1.0.0 (DEFINITIVA)  
**STATUS**: ATIVA E OBRIGATÓRIA
