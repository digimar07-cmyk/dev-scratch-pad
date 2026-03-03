# 🔒 ESTRUTURA DE IA PROTEGIDA - NÃO MODIFICAR SEM APROVAÇÃO

## ⚠️ AVISO CRÍTICO

**ESTA ESTRUTURA FOI REFINADA E TESTADA EXTENSIVAMENTE**  
**MODIFICAÇÕES PODEM CAUSAR REGRESSÃO E BUGS**

---

## 📋 VERSÃO ATUAL: v741

**Data de Lock**: 02/03/2026  
**Status**: ✅ ESTÁVEL E PROTEGIDA  
**Última Modificação**: Commit `e0ecea6` (4/4)

---

## 🛡️ ARQUIVOS PROTEGIDOS

### **1. `fallbacks.py`** (Lógica Central)
- **SHA Protegido**: `8e539cf9bd780167de313b34588202230fa59fa2`
- **Função**: Geração de categorias e descrições sem IA
- **⚠️ CRÍTICO**: Contém lógica refinada v741 com detecção múltipla
- **Limite de Categorias**: 12 (NUNCA reduzir para 8 novamente)

**Principais Funções Protegidas:**
```python
_match_all()              # Detecção múltipla de categorias
_build_categories()       # Construção com limite de 12
fallback_categories()     # Complemento de categorias da IA
fallback_description()    # Templates contextuais
```

---

### **2. `keyword_maps.py`** (Banco de Dados de Keywords)
- **SHA Protegido**: `e4065951c7f173262cbdaf3a54c0faca42866336`
- **Função**: Mapeamento de palavras-chave para categorias
- **⚠️ CRÍTICO**: Contém keywords v741 expandidas

**Novos Mapeamentos v741:**
- **FUNCTION_MAP**:
  - Book Nook → Suporte para Livros
  - Miles/Bike Tracker → Quadro de Acompanhamento
  - Growth Chart/Ruler → Régua de Crescimento
  - Tool Organizer → Organizador de Ferramentas

- **AMBIENTE_MAP**:
  - Biblioteca (library, bookshelf)
  - Garagem expandida (bike, cycling, tools)

- **THEME_MAP**:
  - Ciclismo (cycling, bike, cyclist)
  - Leitura (reading, book lover)
  - Corrida (running, runner, marathon)

- **TRANSLATION_MAP**:
  - bike, cycling, tracker, nook, reading, runner, tool

---

### **3. `text_generator.py`** (Integração com IA)
- **SHA Protegido**: `7f3eb9ee6b7257f058eed8549ee530ad4531e0cf`
- **Função**: Geração de análises usando Ollama
- **⚠️ CRÍTICO**: Linha 172 - limite de 12 categorias

**Linha Protegida:**
```python
return categories[:12], tags  # AUMENTADO DE 8 PARA 12 (v741)
```

---

## 🚫 REGRAS DE PROTEÇÃO

### **NÃO FAZER:**

❌ Reduzir limite de categorias de 12 para 8  
❌ Remover função `_match_all()` do `fallbacks.py`  
❌ Modificar lógica de `_build_categories()` sem testes  
❌ Deletar keywords adicionadas na v741  
❌ Alterar ordem de prioridade das categorias (Date → Func → Env)  
❌ Adicionar termos genéricos ("Diversos", "Data Especial")  
❌ Remover validação `_BANNED` do fallbacks  

### **PODE FAZER (com cuidado):**

✅ **Adicionar novas keywords** no `keyword_maps.py`  
✅ **Adicionar novos templates** de descrição no `fallback_description()`  
✅ **Expandir TRANSLATION_MAP** com novas traduções  
✅ **Adicionar entries no DATE_INFER_MAP**  
✅ **Criar novos mapeamentos** em FUNCTION_MAP, AMBIENTE_MAP, THEME_MAP  

---

## 📊 HISTÓRICO DE VERSÕES

### **v741** (02/03/2026) - ATUAL ✅
- Limite aumentado: 8 → 12 categorias
- Nova função `_match_all()` para detecção múltipla
- Keywords expandidas: Book Nook, Tracker, Ruler, Tool Organizer
- Novos temas: Ciclismo, Leitura, Corrida
- Novos ambientes: Biblioteca, Garagem expandida
- **Commits**: `1c06906`, `643b350`, `c99da50`, `e0ecea6`

### **v740** (anterior)
- Limite: 8 categorias
- Função `_match()` (detecção única)
- Templates de descrição refinados
- Hierarquia NOME > Visão estabelecida

---

## 🔍 CHECKLIST DE VALIDAÇÃO

Antes de modificar qualquer arquivo protegido, verifique:

- [ ] O limite de 12 categorias será mantido?
- [ ] A função `_match_all()` não será removida?
- [ ] Nenhum termo genérico será adicionado?
- [ ] A ordem de prioridade (Date → Func → Env) será mantida?
- [ ] Novos mapeamentos seguem o padrão existente?
- [ ] Há testes para validar a mudança?
- [ ] Há backup do código atual (SHA registrado)?

---

## 🛠️ PROCEDIMENTO PARA MUDANÇAS FUTURAS

### **Se PRECISAR modificar arquivos protegidos:**

1. **Criar branch de desenvolvimento**
   ```bash
   git checkout -b fix/categoria-issue-X
   ```

2. **Registrar SHA atual antes de modificar**
   ```bash
   git log --oneline -1 laserflix_v3.1/ai/fallbacks.py
   ```

3. **Fazer mudanças incrementais**
   - Um arquivo por vez
   - Commits pequenos e reversíveis
   - Mensagens descritivas

4. **Testar exaustivamente**
   - Rodar análise em produtos variados
   - Verificar que limite de 12 funciona
   - Validar que não há categorias genéricas

5. **Documentar mudanças neste arquivo**
   - Atualizar versão (v741 → v742)
   - Adicionar entry no histórico
   - Atualizar SHA protegido

6. **Merge para main apenas se testes passarem**

---

## 📞 CONTATO EM CASO DE DÚVIDAS

Se precisar modificar algo e não tiver certeza:

1. Consulte este documento primeiro
2. Revise commits da v741 para entender lógica
3. Faça perguntas específicas antes de modificar
4. **SEMPRE teste em ambiente isolado primeiro**

---

## 🎯 OBJETIVOS ALCANÇADOS NA v741

✅ Produtos com múltiplas categorias detectadas corretamente  
✅ Book Nook, Bike Tracker, Growth Chart mapeados  
✅ Limite de 12 categorias resolve bug de "poucas categorias"  
✅ Documentação clara e protegida  
✅ Sistema robusto e reversível (cada commit tem SHA)  

---

## ⚡ LEMBRETE FINAL

> "Se não está quebrado, não conserte."
> "Se PRECISAR consertar, teste 3x antes de commitar."

**Esta estrutura foi refinada através de 4 commits cuidadosos.**  
**Respeite o trabalho feito. Proteja a estabilidade.**

---

**Data de Criação**: 02/03/2026 21:59 BRT  
**Versão do Lock**: v741  
**Próxima Revisão**: Somente quando necessário
