# LASERFLIX - Estrutura de Diretórios

## ✅ ESTRUTURA VÁLIDA (Modular v7.4.0)

```
dev-scratch-pad/
├── laserflix/           # ✅ ESTRUTURA MODULAR (USE ESTA!)
│   ├── core/
│   ├── ollama/
│   ├── media/
│   ├── ui/
│   └── workers/
│
├── main.py             # ✅ Entry point principal
├── test_imports.py     # ✅ Validação de módulos
├── README_MODULAR.md   # ✅ Documentação
└── .gitignore          # ✅ Ignora cache/logs
```

## ❌ VERSÕES ANTIGAS (NÃO USAR)

```
dev-scratch-pad/
└── laserflix_v3/       # ❌ OLD - Versão monoarquivo antiga
```

---

## 🚀 Como Usar

### 1. Clone/Pull
```bash
git clone https://github.com/digimar07-cmyk/dev-scratch-pad.git
cd dev-scratch-pad
git checkout modularizacao
```

### 2. Validação
```bash
python test_imports.py
# Deve retornar: ✓ TODOS OS TESTES PASSARAM! (100%)
```

### 3. Execução
```bash
python main.py
# Interface Netflix-style deve abrir
```

---

## ⚠️ IMPORTANTE

- **USE APENAS** `laserflix/` (estrutura modular)
- **IGNORE** `laserflix_v3/` (versão antiga)
- **ENTRY POINT**: `main.py` na raiz
- **IMPORTS**: `from laserflix.core.app import LaserflixApp`

---

## 📝 Estrutura Modular Detalhada

Veja [README_MODULAR.md](README_MODULAR.md) para documentação completa.
