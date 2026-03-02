# 🔐 Sistema de Backup Local - Laserflix v3.1

## 🎯 Por que existe?

**PROBLEMA RESOLVIDO:**
- Commits em lote quebram o app
- Reversões via Git são lentas
- Falta snapshots rápidos antes de mudanças

**SOLUÇÃO:**
Backups locais comprimidos, independentes do Git, com restore em 5 segundos.

---

## 📦 O que é backupado?

✅ **Incluído:**
- Todas as pastas de código (`ai/`, `ui/`, `core/`, `config/`, `utils/`)
- Arquivos principais (`main.py`, `requirements.txt`)
- Documentação (`*.md`)

❌ **Excluído:**
- Cache Python (`__pycache__/`, `*.pyc`)
- Ambientes virtuais (`venv/`)
- Bancos de dados (`*.db`)
- Logs (`*.log`)
- A própria pasta de backups (`.backups/`)

---

## 🚀 Comandos Básicos

### 1️⃣ Criar Backup

**Antes de QUALQUER modificação importante:**

```bash
python backup_manager.py create "antes de fix do modal"
```

**Backup rápido sem descrição:**

```bash
python backup_manager.py create
```

**O que acontece:**
- Cria arquivo `.backups/backup_XXX_YYYY-MM-DD_HH-MM-SS.zip`
- Comprime ~70% do tamanho original
- Atualiza metadata JSON
- Remove backups excedentes (mantém últimos 10)

---

### 2️⃣ Listar Backups

```bash
python backup_manager.py list
```

**Exemplo de saída:**
```
📦 Backups disponíveis (10/10):

  #010 | 2026-03-02_22-30-15 | 2.3 MB - antes de refatorar UI
  #009 | 2026-03-02_21-45-08 | 2.2 MB - fix modal de imagens
  #008 | 2026-03-02_20-12-33 | 2.1 MB - AUTO: antes de restaurar #5
  ...

💡 Restaurar: python backup_manager.py restore <número>
```

---

### 3️⃣ Restaurar Backup

**CUIDADO:** Isso substitui os arquivos atuais!

```bash
python backup_manager.py restore 5
```

**O que acontece:**
1. Sistema pede confirmação
2. Cria backup de segurança automático (antes de restaurar)
3. Extrai o backup escolhido
4. Substitui arquivos atuais

**Exemplo de execução:**
```
⚠️  ATENÇÃO: Isso vai SUBSTITUIR os arquivos atuais!
📦 Restaurando backup #5 (2026-03-02_19-30-12)

🤔 Confirma? (sim/não): sim

🔄 Criando backup de segurança antes...
✅ Backup criado: backup_011_2026-03-02_22-35-01.zip

📂 Extraindo backup_005_2026-03-02_19-30-12.zip...
✅ Backup #5 restaurado com sucesso!
💾 Backup de segurança criado: backup_011_2026-03-02_22-35-01.zip
```

---

### 4️⃣ Limpar Backups Antigos

**Manter apenas últimos 5:**

```bash
python backup_manager.py clean 5
```

**Padrão (últimos 10):**

```bash
python backup_manager.py clean
```

---

## 🔥 Workflow Recomendado (Filosofia Akita)

### Antes de QUALQUER mudança:

```bash
# 1. Criar backup
python backup_manager.py create "antes de [descrição da mudança]"

# 2. Fazer as modificações
vim laserflix_v3.1/ui/main_window.py

# 3. Testar
python laserflix_v3.1/main.py

# 4a. Se funcionou: commit no Git
git add .
git commit -m "✅ [descrição]"

# 4b. Se quebrou: restaurar backup
python backup_manager.py restore 10  # último backup
```

---

## 🎯 Casos de Uso

### ✅ Caso 1: Refatoração Grande

```bash
# Antes de começar
python backup_manager.py create "antes de refatorar sistema de IA"

# Depois de cada etapa funcional
python backup_manager.py create "etapa 1: text_generator OK"
python backup_manager.py create "etapa 2: fallbacks OK"
```

### ✅ Caso 2: Bug Urgente

```bash
# Backup rápido antes do fix
python backup_manager.py create "antes de fix urgente"

# Se o fix quebrar algo:
python backup_manager.py restore 10
```

### ✅ Caso 3: IA Fez Commits em Lote

```bash
# Listar backups
python backup_manager.py list

# Voltar para versão antes da IA
python backup_manager.py restore 8
```

---

## 📊 Informações Técnicas

### Estrutura de Arquivos

```
laserflix_v3.1/
├── .backups/                          # Pasta de backups (não vai pro Git)
│   ├── backup_001_2026-03-02_19-28-15.zip
│   ├── backup_002_2026-03-02_20-15-43.zip
│   ├── ...
│   ├── backup_010_2026-03-02_22-30-01.zip
│   └── backup_metadata.json           # Rastreamento de versões
├── backup_manager.py                  # Script de backup/restore
└── ...
```

### Metadata JSON (exemplo)

```json
[
  {
    "number": 10,
    "filename": "backup_010_2026-03-02_22-30-01.zip",
    "timestamp": "2026-03-02_22-30-01",
    "description": "antes de refatorar UI",
    "file_count": 45,
    "size_mb": 2.3
  }
]
```

### Rotação Automática

- **Máximo:** 10 backups
- **Quando cria o 11º:** Remove o mais antigo automaticamente
- **Ordem:** Sempre do mais novo (#10) para o mais antigo (#1)

---

## 🐛 Troubleshooting

### Erro: "Backup não encontrado"

```bash
# Listar backups disponíveis
python backup_manager.py list

# Usar número correto
python backup_manager.py restore 5
```

### Erro: "Arquivo de backup corrompido"

```bash
# Tentar backup anterior
python backup_manager.py restore 9
```

### Pasta `.backups/` muito grande

```bash
# Limpar backups antigos (manter últimos 5)
python backup_manager.py clean 5
```

### Restauração cancelada acidentalmente

```bash
# Tentar novamente
python backup_manager.py restore 8

# Confirmar com "sim" quando perguntado
```

---

## ⚡ Dicas Rápidas

1. **Crie backup ANTES de testar código novo da IA**
2. **Use descrições curtas mas úteis** ("antes de fix modal" é melhor que "backup1")
3. **Não delete a pasta `.backups/` manualmente** (use `clean` se precisar)
4. **Backups são locais** - não vão pro GitHub (já está no `.gitignore`)
5. **Rotação é automática** - não precisa limpar manualmente

---

## 🚨 Regras de Ouro

1. ✅ **SEMPRE criar backup antes de mudanças grandes**
2. ✅ **Testar DEPOIS de restaurar** (não assumir que está OK)
3. ✅ **Usar Git + Backups juntos** (backups locais ≠ substituem Git)
4. ✅ **Descrever backups** (você vai esquecer o que era daqui 1 hora)
5. ❌ **NUNCA deletar `.backups/` inteira** (use o comando `clean`)

---

## 💬 Perguntas Frequentes

### P: Backups vão pro GitHub?
**R:** Não! A pasta `.backups/` está no `.gitignore`.

### P: Quanto espaço ocupam?
**R:** ~2-3 MB por backup (comprimido). 10 backups = ~25 MB.

### P: Posso mudar o limite de 10 backups?
**R:** Sim! Edite `MAX_BACKUPS` no `backup_manager.py`.

### P: E se eu quiser backup de 1 arquivo só?
**R:** Use Git: `git checkout HEAD -- arquivo.py`

### P: Backup automático antes de commits?
**R:** Em desenvolvimento! Por enquanto, rode manualmente.

---

## 🎓 Filosofia Akita Aplicada

> **"Software vivo itera. Backups protegem suas iterações."**

- ✅ **Small Releases**: Backup após cada etapa funcional
- ✅ **Velocidade COM disciplina**: Restore em 5s quando algo quebra
- ✅ **Refactoring Contínuo**: Sem medo de quebrar (backup te protege)
- ✅ **IA é ferramenta**: Backup antes de aceitar código da IA
- ✅ **Iteração real**: Testa, quebra, restaura, aprende

---

**🔥 BORA CODAR COM SEGURANÇA!**
