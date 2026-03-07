# 🔐 Sistema de Backup Local - Laserflix v3.1

## 🎯 Objetivo

Resolver o problema de **commits múltiplos que quebram o app** sem dependência do GitHub, mantendo até **10 versões anteriores** para restauração instantânea.

---

## 🚀 Uso Rápido

### Criar Backup Antes de Mudanças

```bash
python backup_manager.py create "Antes de adicionar feature X"
```

### Listar Backups Disponíveis

```bash
python backup_manager.py list
```

### Restaurar Backup

```bash
# Restaurar o mais recente (backup #0)
python backup_manager.py restore 0

# Restaurar backup #3
python backup_manager.py restore 3
```

### Ver Info de um Backup

```bash
python backup_manager.py info 0
```

---

## 📚 Guia Completo

### 1️⃣ Estrutura de Backups

```
laserflix_v3.1/
├── .backups/                    # Pasta de backups (criada automaticamente)
│   ├── backup_20260302_210530_a3e48/
│   ├── backup_20260302_183421_dbf58/
│   ├── backup_20260302_154512_08809/
│   ├── ...
│   └── backup_metadata.json          # Metadados de todos os backups
├── backup_manager.py              # Sistema de backup
├── main.py
├── ai/
└── ...
```

**⚠️ Importante**: A pasta `.backups` é **automaticamente excluída** dos próprios backups para evitar recursividade.

---

### 2️⃣ Comandos Disponíveis

#### `create` - Criar Novo Backup

```bash
# Sem descrição
python backup_manager.py create

# Com descrição
python backup_manager.py create "Antes de refatorar UI"
```

**Comportamento**:
- Copia TODO o projeto (exceto `.backups`, `__pycache__`, `.git`)
- Calcula hash SHA256 do estado atual
- **Não cria backup duplicado** se nada mudou
- Remove backups antigos automaticamente (mantém só 10)

#### `list` - Listar Backups

```bash
python backup_manager.py list
```

**Saída**:
```
📦 Backups disponíveis (10/10):

[0] 2026-03-02T21:05:30
    📝 Antes de adicionar feature X
    💾 12.3 MB
    🔑 Hash: a3e4863ff8995

[1] 2026-03-02T18:34:21
    📝 Restauração da lógica de IA
    💾 12.1 MB
    🔑 Hash: dbf58ae9f943b
```

**Índice 0 = backup mais recente**

#### `restore` - Restaurar Backup

```bash
# Restaurar o mais recente
python backup_manager.py restore 0

# Restaurar backup #5
python backup_manager.py restore 5
```

**Comportamento**:
1. Mostra informações do backup
2. **Cria backup de segurança do estado atual**
3. Pede confirmação (`SIM`)
4. Remove conteúdo atual (exceto `.backups`)
5. Restaura backup selecionado

**⚠️ Segurança**: Sempre cria backup antes de restaurar!

#### `info` - Ver Detalhes

```bash
python backup_manager.py info 0
```

**Saída**:
```
📦 Backup #0:
📅 Data: 2026-03-02T21:05:30
📝 Descrição: Antes de adicionar feature X
💾 Tamanho: 12.3 MB
🔑 Hash: a3e4863ff8995
📂 Nome: backup_20260302_210530_a3e48
```

#### `delete` - Remover Backup

```bash
python backup_manager.py delete 5
```

**Uso**: Liberar espaço removendo backups desnecessários.

---

### 3️⃣ Uso Programático (Python)

```python
from backup_manager import BackupManager

# Inicializar
manager = BackupManager()

# Criar backup
backup_info = manager.create_backup("Antes de mudança arriscada")
print(f"Backup criado: {backup_info['name']}")

# Listar backups
backups = manager.list_backups()
for i, backup in enumerate(backups):
    print(f"[{i}] {backup['datetime']} - {backup['description']}")

# Restaurar backup
manager.restore_backup(backup_index=0)
```

#### Decorator para Backup Automático

```python
from backup_manager import BackupManager

manager = BackupManager()

@manager.auto_backup_wrapper
def funcao_que_pode_quebrar_tudo():
    # Código arriscado aqui
    pass

# Ao executar, cria backup automaticamente ANTES de rodar
funcao_que_quebrar_tudo()
```

---

### 4️⃣ Arquivos/Pastas Excluídos

**Nunca entram nos backups**:
- `.backups/` (os próprios backups)
- `__pycache__/`, `.pytest_cache/`
- `.git/`
- `*.pyc`, `*.pyo`
- `.DS_Store`
- `*.log`

**Por quê?** Reduzir tamanho e evitar conflitos.

---

## 🚨 Workflow Recomendado

### Antes de Desenvolvimento

```bash
# 1. Criar backup
python backup_manager.py create "Antes de adicionar feature X"

# 2. Desenvolver...
# (você ou a IA fazem mudanças)

# 3. Testar
python main.py

# 4. Se quebrou:
python backup_manager.py restore 0
```

### Após IA Fazer Vários Commits

```bash
# Se a IA fez 5 commits e quebrou tudo:

# 1. Ver backups disponíveis
python backup_manager.py list

# 2. Restaurar versão antes dos commits
python backup_manager.py restore 1  # Pular backup #0 (quebrado)
```

### Antes de Refatoração Grande

```bash
# Backup descritivo
python backup_manager.py create "V3.1 estável antes de modularizar UI"

# Agora pode refatorar com segurança
```

---

## 🛡️ Seguranças Implementadas

✅ **Backup de segurança antes de restaurar**: Sempre cria backup do estado atual

✅ **Confirmação obrigatória**: Pede `SIM` para restaurar/deletar

✅ **Detecção de duplicatas**: Não cria backup se nada mudou (hash)

✅ **Limite automático**: Remove backups antigos (mantém 10)

✅ **Metadados JSON**: Rastreamento completo de data, descrição, tamanho

✅ **Exceções tratadas**: Não quebra se arquivo estiver em uso

---

## 📊 Espaço em Disco

### Tamanho Típico

- **1 backup**: ~12 MB
- **10 backups**: ~120 MB

### Gerenciar Espaço

```bash
# Ver tamanho de cada backup
python backup_manager.py list

# Remover backups antigos manualmente
python backup_manager.py delete 9  # Remove o mais antigo
python backup_manager.py delete 8
```

**Automático**: Sistema remove backups excedentes automaticamente.

---

## ❓ FAQ

### Por que não usar Git?

✅ **Backups locais são instantâneos**: Sem push/pull

✅ **Não poluem histórico**: Git fica limpo

✅ **Mais simples**: Comandos diretos

✅ **Segurança dupla**: Git + backups locais

### O que acontece se deletar `.backups`?

⚠️ **Perde todos os backups**, mas o sistema recria a pasta vazia automaticamente.

### Backups funcionam com v3.0?

✅ **Sim**, mas **não é necessário**: v3.0 está **protegida e intocável**.

Backups são para **v3.1 (versão ativa)**.

### Posso commitar backups no Git?

❌ **Não recomendado**: `.backups` deve estar no `.gitignore`.

Backups são **locais**, não remotos.

### Como integrar com CI/CD?

```python
# No script de deploy
from backup_manager import BackupManager

manager = BackupManager()
manager.create_backup("Deploy v3.1.5")

# Deploy...
```

---

## 🔧 Troubleshooting

### Erro: "Nenhum backup disponível"

**Solução**: Criar primeiro backup:
```bash
python backup_manager.py create "Primeiro backup"
```

### Erro: "Backup corrompido"

**Causa**: Pasta de backup foi deletada manualmente.

**Solução**: Deletar metadados:
```bash
python backup_manager.py delete [indice_corrompido]
```

### Restauração não funciona

**Verificações**:
1. Backup existe? `python backup_manager.py list`
2. Permissões de escrita no diretório?
3. Espaço em disco suficiente?

---

## 🎓 Exemplos Práticos

### Caso 1: IA Quebrou Tudo com 7 Commits

```bash
# Situação: Última conversa fez 7 commits, app não roda mais

# Ver backups
python backup_manager.py list

# Restaurar backup antes dos commits (backup #1 ou #2)
python backup_manager.py restore 1

# Confirmar com "SIM"
# ✅ App volta a funcionar!
```

### Caso 2: Testar Mudança Arriscada

```bash
# Antes de pedir para IA refatorar
python backup_manager.py create "Antes de refatorar lógica de IA"

# IA faz refatoração...

# Testar
python main.py

# Se deu ruim:
python backup_manager.py restore 0

# Se deu certo: continuar desenvolvendo
```

### Caso 3: Manter Milestones

```bash
# Criar backups de versões estáveis
python backup_manager.py create "V3.1 - UI Netflix funcionando"
# ... desenvolver ...
python backup_manager.py create "V3.1 - Filtros implementados"
# ... desenvolver ...
python backup_manager.py create "V3.1 - IA refinada"

# Sempre ter milestones para voltar
```

---

## ✅ Checklist de Uso Diário

- [ ] **Início do dia**: Criar backup do estado estável
- [ ] **Antes de mudanças grandes**: Criar backup descritivo
- [ ] **Após IA fazer vários commits**: Testar + criar backup se OK
- [ ] **Se algo quebrar**: Restaurar último backup funcional
- [ ] **Fim do dia**: Criar backup se versão está estável

---

## 🚀 Próximos Passos

✅ **Sistema implementado e funcional**

🔸 **Uso recomendado**: Começar criando primeiro backup agora

```bash
python backup_manager.py create "V3.1 - Estado inicial com lógica de IA refinada"
```

🔸 **Adicionar ao `.gitignore`**:
```bash
echo ".backups/" >> .gitignore
```

---

**🔐 Agora você tem controle total sobre versões locais, sem depender do GitHub para restaurações rápidas!**
