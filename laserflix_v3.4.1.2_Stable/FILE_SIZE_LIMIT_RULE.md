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

## 🤖 VALIDAÇÃO AUTOMÁTICA OBRIGATÓRIA (NOVA REGRA)

### **CHECAGEM ANTES DE QUALQUER RESPOSTA/AÇÃO**

**TODA IA/ASSISTENTE/DESENVOLVEDOR DEVE:**

```python
# PASSO 1: ANTES DE FAZER QUALQUER MODIFICAÇÃO
def validar_tamanho_arquivo():
    """
    Valida se arquivo respeita limite ANTES de modificar.
    CHAMADA OBRIGATÓRIA antes de qualquer edit/refactor/feature.
    """
    limites = {
        "ui/main_window.py": 200,
        "ui/project_card.py": 150,
        "ui/project_modal.py": 250,
        "ui/header.py": 150,
        "ui/sidebar.py": 200,
        # Qualquer outro arquivo UI: 300
    }
    
    for arquivo, limite in limites.items():
        if os.path.exists(arquivo):
            with open(arquivo) as f:
                linhas = [l for l in f if l.strip() and not l.strip().startswith('#')]
                total = len(linhas)
                
                if total > limite:
                    print(f"🚨 VIOLAÇÃO: {arquivo}")
                    print(f"   Atual: {total} linhas")
                    print(f"   Limite: {limite} linhas")
                    print(f"   Excesso: {total - limite} linhas ({((total/limite - 1) * 100):.1f}%)")
                    print(f"   ❌ AÇÃO OBRIGATÓRIA: PARAR + REFATORAR")
                    return False
    
    return True

# PASSO 2: SE VALIDAÇÃO FALHAR
if not validar_tamanho_arquivo():
    print("🚨 DESENVOLVIMENTO CONGELADO")
    print("❌ NÃO é permitido:")
    print("   - Adicionar features")
    print("   - Modificar código existente")
    print("   - Fazer commits")
    print()
    print("✅ ÚNICA AÇÃO PERMITIDA:")
    print("   - Refatorar/extrair código para controllers/components")
    print("   - Reduzir arquivo para < limite")
    exit(1)
```

### **REGRA #0: VALIDAÇÃO PRÉ-RESPOSTA**

```
TODA vez que uma IA for responder sobre código do Laserflix:

1. ANTES de sugerir modificações
2. ANTES de criar patches
3. ANTES de aprovar código
4. ANTES de dizer "está bom"

DEVE executar:
→ validar_tamanho_arquivo()
→ Se FALHAR: DENUNCIAR violação + PARAR + PLANO de refatoração
→ Se PASSAR: Pode prosseguir
```

### **PENALIDADES POR NÃO VALIDAR:**

```
❌ IA que aprovar código > limite:
   → Falha crítica de execução
   → Deve se autocorrigir imediatamente
   → Deve reconhecer o erro explicitamente

❌ IA que disser "está bom" sem validar:
   → Violação de protocolo
   → Deve reprocessar resposta
   → Deve aplicar validação obrigatória
```

---

## 🔒 PROTOCOLO DE SEGURANÇA (ANTI-DERIVA)

### **PROBLEMA: Deriva de Contexto em LLMs**

```
LLMs tendem a:
- Esquecer regras após N mensagens
- Ignorar limites em conversas longas
- Priorizar "fazer funcionar" sobre "seguir regras"

RESULTADO: Código cresce, limites violados, regras ignoradas
```

### **SOLUÇÃO: Validação Compulsória**

```python
# Em TODA resposta sobre código, incluir seção obrigatória:

## 📏 VALIDAÇÃO DE LIMITES (OBRIGATÓRIA)

Arquivo: ui/main_window.py
Linhas atuais: XXX
Limite: 200
Status: ✅ OK / ❌ VIOLAÇÃO

[Se violação detectada]
🚨 AÇÃO IMEDIATA NECESSÁRIA:
- Desenvolvimento PAUSADO
- Refatoração OBRIGATÓRIA
- Plano de redução anexado
```

### **FORÇAR RECALIBRAÇÃO PERIÓDICA**

```
A CADA 5 MENSAGENS sobre código:
1. Revalidar TODOS os limites
2. Relembrar regras (FILE_SIZE_LIMIT_RULE.md)
3. Checar conformidade arquitetural
4. Reportar status

OBJETIVO: Prevenir deriva de contexto
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
1. validar_tamanho_arquivo() retorna True? ✓
2. main_window.py tem < 200 linhas? ✓
3. Feature nova exige controller? → CRIAR CONTROLLER PRIMEIRO
4. Feature nova exige componente? → CRIAR COMPONENTE PRIMEIRO
5. Método tem > 20 linhas? → EXTRAIR PARA CLASSE SEPARADA
6. Arquivo passa de 80% do limite? → REFATORAR ANTES
```

### 3. **SE ARQUIVO PASSAR DO LIMITE**

```bash
🚨 AÇÃO OBRIGATÓRIA IMEDIATA:

1. PARAR TODO DESENVOLVIMENTO
2. EXECUTAR validar_tamanho_arquivo()
3. IDENTIFICAR código a extrair
4. EXTRAIR código para controllers/components
5. REDUZIR arquivo para 70% do limite
6. VALIDAR novamente
7. DOCUMENTAR extração no commit
8. SÓ ENTÃO continuar feature
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

### **SE ARQUIVO PASSAR DE 200 LINHAS (main_window.py):**

1. **🚨 ALARME CRÍTICO**
2. **DESENVOLVIMENTO CONGELADO**
3. **ROLLBACK FORÇADO** do último commit
4. **REFATORAÇÃO OBRIGATÓRIA** antes de continuar
5. **NENHUMA FEATURE NOVA** até resolver

### **SE ARQUIVO PASSAR DE 250 LINHAS:**

1. **🔥 EMERGÊNCIA CRÍTICA**
2. **DESENVOLVIMENTO CONGELADO**
3. **ROLLBACK FORÇADO** do último commit
4. **REFATORAÇÃO OBRIGATÓRIA** antes de continuar
5. **NENHUMA FEATURE NOVA** até resolver

### **SE ARQUIVO PASSAR DE 300 LINHAS:**

1. **💀 CÓDIGO REJEITADO**
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

## 📋 CHECKLIST PRÉ-COMMIT (ATUALIZADO)

```bash
☐ Executei validar_tamanho_arquivo()? ✓
☐ main_window.py < 200 linhas? ✓
☐ Nenhum arquivo UI > limite? ✓
☐ Lógica complexa em controllers? ✓
☐ Componentes UI reutilizáveis extraídos? ✓
☐ Callbacks delegam para controllers? ✓
☐ Código segue arquitetura MVC/MVVM? ✓

✅ TODOS checados? → PODE COMMITAR
❌ Algum falhou? → REFATORAR PRIMEIRO
```

---

## 🎯 RESUMO EXECUTIVO

```
0. VALIDAR limites ANTES de tudo (NOVA REGRA)
1. main_window.py = ORQUESTRADOR (< 200 linhas)
2. LÓGICA = CONTROLLERS (arquivos separados)
3. UI = COMPONENTS (widgets reutilizáveis)
4. LIMITE VIOLADO = PARAR + REFATORAR
5. SEM EXCEÇÕES, SEM DESCULPAS
6. VALIDAÇÃO AUTOMÁTICA OBRIGATÓRIA
```

---

## ⚡ ESTA REGRA É:

- ✅ **ABSOLUTA**: Nenhuma exceção
- ✅ **INATACÁVEL**: Não pode ser ignorada
- ✅ **INVIOLÁVEL**: Quebrar = rollback forçado
- ✅ **REDUNDANTE**: Repetida em TODOS os .md
- ✅ **AUTOMÁTICA**: Checada ANTES de cada ação
- ✅ **COMPULSÓRIA**: IAs DEVEM validar antes de responder

---

## 🛡️ GARANTIAS DE CONFORMIDADE

### **PARA IAs/ASSISTENTES:**

```python
# TODA IA deve incluir este trecho em TODA resposta sobre código:

## 🔍 VALIDAÇÃO EXECUTADA

Arquivo verificado: ui/main_window.py
Linhas: XXX
Limite: 200
Status: [✅ CONFORME / ❌ VIOLAÇÃO]

[Se violação]
🚨 DESENVOLVIMENTO PAUSADO
📋 Plano de refatoração gerado
⏳ Aguardando correção antes de prosseguir
```

### **MECANISMO ANTI-DERIVA:**

```
Mensagem #1-5: Trabalho normal
Mensagem #6: RECALIBRAÇÃO OBRIGATÓRIA
  → Revalidar limites
  → Reler FILE_SIZE_LIMIT_RULE.md
  → Reportar status

Mensagem #7-11: Trabalho normal
Mensagem #12: RECALIBRAÇÃO OBRIGATÓRIA
  → (repetir ciclo)
```

---

**ÚLTIMA ATUALIZAÇÃO**: 2026-03-06 22:35 BRT  
**VERSÃO**: 2.0.0 (COM VALIDAÇÃO AUTOMÁTICA)  
**STATUS**: ATIVA E OBRIGATÓRIA + VALIDAÇÃO COMPULSÓRIA

---

**ALTERAÇÕES v2.0.0:**
- ✅ Adicionada validação automática obrigatória
- ✅ Protocolo de segurança anti-deriva
- ✅ Checklist pré-commit atualizado
- ✅ Penalidades por não validação
- ✅ Mecanismo de recalibração periódica
