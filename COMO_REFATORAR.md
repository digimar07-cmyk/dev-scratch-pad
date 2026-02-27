# Como Refatorar o Laserflix

## Passo 1: Execute o script de refatoração

```bash
cd G:\GitHub\dev-scratch-pad
python refactor_laserflix.py
```

Isso vai:
- ✅ Criar a estrutura de pastas `laserflix_tkinter/`
- ✅ Copiar assets (ícones, logo)
- ✅ Criar `main.py` funcional
- ✅ Criar `app.py` (wrapper temporário do código original)

## Passo 2: Rode o app refatorado

```bash
cd laserflix_tkinter
python main.py
```

## Próximos passos (incremental)

A modularização será feita aos poucos:
1. Extrair funções auxiliares para `utils/`
2. Extrair componentes UI para `ui/`
3. Extrair lógica de negócio para `core/`
4. Substituir wrapper do `app.py` por código modular

## Estrutura Final

```
laserflix_tkinter/
├── main.py                  → entry point
├── app.py                   → classe principal
├── config.py                → constantes
├── core/                    → lógica de negócio
│   ├── database_manager.py
│   ├── backup_manager.py
│   ├── ollama_client.py
│   ├── ai_analyzer.py
│   └── ...
├── ui/                      → componentes de interface
│   ├── header.py
│   ├── sidebar/
│   ├── project_grid/
│   ├── modals/
│   └── ...
├── actions/                 → ações e filtros
├── utils/                   → utilitários
├── assets/                  → ícones, imagens
└── data/                    → dados em runtime
```
