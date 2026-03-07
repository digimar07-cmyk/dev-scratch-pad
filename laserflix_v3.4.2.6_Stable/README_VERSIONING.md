# 🔢 Sistema de Versionamento Automático - Laserflix

## 🎯 Objetivo

Gerenciar versões automaticamente e documentar cada modificação do projeto.

**Benefícios:**
- ✅ Auto-incremento de versão
- ✅ CHANGELOG.md sempre atualizado
- ✅ Histórico completo de mudanças
- ✅ Rastreamento fácil de versões
- ✅ Integrado com refatoração Fase 7

---

## 📊 Esquema de Versionamento

### Formato: `MAJOR.MINOR.PATCH.BUILD`

```
3.4.2.5
│ │ │ └─ BUILD:  Mudanças pequenas, bug fixes, ajustes
│ │ └─── PATCH:  Features menores, melhorias
│ └───── MINOR:  Features grandes, refatorações
└─────── MAJOR:  Breaking changes, mudanças de arquitetura
```

### Exemplos:

| Tipo | Quando usar | Exemplo |
|------|-------------|----------|
| **BUILD** | Bug fixes, ajustes pequenos | 3.4.2.4 → 3.4.2.5 |
| **PATCH** | Nova feature menor | 3.4.2.5 → 3.4.3.0 |
| **MINOR** | Refatoração, feature grande | 3.4.3.0 → 3.5.0.0 |
| **MAJOR** | Breaking change | 3.5.0.0 → 4.0.0.0 |

---

## 🔧 Uso

### **1. Ver versão atual**

```bash
python version_manager.py current
```

**Saída:**
```
Versão atual: 3.4.2.5
```

---

### **2. Incrementar versão**

#### **BUILD** (mudanças pequenas)
```bash
python version_manager.py bump build "Corrigido bug no filtro de categorias"
```

#### **PATCH** (feature menor)
```bash
python version_manager.py bump patch "Adicionado filtro por data"
```

#### **MINOR** (feature grande)
```bash
python version_manager.py bump minor "Fase 7C: SelectionController implementado"
```

#### **MAJOR** (breaking change)
```bash
python version_manager.py bump major "Nova arquitetura MVC"
```

---

### **3. Incrementar com detalhes**

```bash
python version_manager.py bump build "Fase 7C aplicada" \
  --changes "SelectionController extraído" \
            "CollectionController extraído" \
            "ProjectManagementController extraído" \
            "14 métodos removidos do main_window"
```

**Resultado no CHANGELOG.md:**
```markdown
## [3.4.2.6] - 2026-03-07 10:00:00

### Fase 7C aplicada

**Mudanças:**
- SelectionController extraído
- CollectionController extraído
- ProjectManagementController extraído
- 14 métodos removidos do main_window
```

---

## 📝 Arquivos Gerenciados

### **1. `VERSION`**
Arquivo único com versão atual:
```
3.4.2.5
```

### **2. `config/settings.py`**
Atualizado automaticamente:
```python
VERSION = "3.4.2.5"
```

### **3. `CHANGELOG.md`**
Histórico completo de mudanças:
```markdown
## [3.4.2.5] - 2026-03-07 09:13:00
### Sistema de versionamento implementado
**Mudanças:**
- Criado version_manager.py
- ...
```

---

## 🔄 Integração com Fase 7

O `apply_fase7_refactor.py` foi modificado para auto-incrementar versão:

```bash
# Aplicar Fase 7C (auto-incrementa versão)
python apply_fase7_refactor.py --phase 7c

# Resultado:
# - Versão: 3.4.2.5 → 3.4.2.6
# - CHANGELOG.md atualizado
# - config/settings.py atualizado
```

---

## 📅 Roadmap de Versões (Fase 7)

| Versão | Fase | Descrição | Linhas |
|---------|------|-------------|--------|
| **3.4.2.4** | - | Estado atual (FASE 2+3) | 859 |
| **3.4.2.5** | - | Sistema de versionamento | 859 |
| **3.4.2.6** | 7C | SelectionController + 2 | 659 |
| **3.4.2.7** | 7D | ChipsBar + 2 components | 409 |
| **3.4.2.8** | 7E | Simplificações | 309 |
| **3.4.2.9** | 7F | ModalManager + 2 | 189 |
| **3.4.3.0** | - | RELEASE FINAL | 189 |

---

## ❓ FAQ

### **P: Preciso rodar version_manager.py manualmente?**
**R:** Não! O `apply_fase7_refactor.py` já faz isso automaticamente.

### **P: Como ver histórico completo?**
**R:** Abra `CHANGELOG.md`

### **P: Posso reverter uma versão?**
**R:** Sim, use `git revert` ou restaure o backup.

### **P: O que acontece se eu editar VERSION manualmente?**
**R:** Funciona, mas não é recomendado. Use sempre o script.

---

## 🎉 Exemplo Completo

```bash
# 1. Ver versão atual
python version_manager.py current
# Versão atual: 3.4.2.5

# 2. Aplicar Fase 7C (auto-incrementa)
python apply_fase7_refactor.py --phase 7c
# 🔼 VERSÃO: 3.4.2.5 → 3.4.2.6
# 📝 DESCRIÇÃO: Fase 7C: SelectionController + CollectionController + ProjectManagementController
# ✅ VERSION atualizado: 3.4.2.6
# ✅ config/settings.py atualizado
# ✅ CHANGELOG.md atualizado

# 3. Verificar mudanças
cat CHANGELOG.md
# [3.4.2.6] - 2026-03-07 10:00:00
# Fase 7C aplicada...

# 4. Testar
python main.py

# 5. Commit
git add VERSION config/settings.py CHANGELOG.md ui/
git commit -m "feat(v3.4.2.6): Fase 7C aplicada"
git push
```

---

## 🛠️ Troubleshooting

### **Problema: "VERSION file not found"**
**Solução:**
```bash
echo "3.4.2.5" > VERSION
```

### **Problema: config/settings.py não atualizado**
**Solução:**
Verifique se o arquivo existe:
```bash
ls -l config/settings.py
```

---

## 👨‍💻 Autor

**Claude Sonnet 4.5**  
Data: 07/03/2026  
Versão: 1.0

---

## ✅ Conclusão

**Sistema de versionamento ativo!**

Agora toda modificação é:
- ✅ Versionada automaticamente
- ✅ Documentada no CHANGELOG
- ✅ Rastreada no git
- ✅ Fácil de auditar

**Próximo passo:** Aplicar Fase 7C!
```bash
python apply_fase7_refactor.py --phase 7c
```
