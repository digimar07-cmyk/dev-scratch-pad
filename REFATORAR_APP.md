# Como Refatorar app.py

## Passo 1: Execute o script

```bash
cd G:\\GitHub\\dev-scratch-pad
python refactor_app_py.py
```

## O que o script faz:

1. ✅ Lê `laserflix_v740_Ofline_Stable.py`
2. ✅ Extrai a classe `LaserflixNetflix` completa
3. ✅ Extrai todos os imports necessários
4. ✅ Cria backup do `app.py` antigo (`app.py.backup`)
5. ✅ Gera novo `app.py` com a classe extraída

## Passo 2: Teste o app

```bash
cd laserflix_tkinter
python main.py
```

## Se der erro:

```bash
cd laserflix_tkinter
copy app.py.backup app.py
python main.py
```

## Próximos passos:

Depois que o app estiver funcionando com o novo `app.py`:

1. Substituir imports diretos por imports dos módulos `core/`
2. Extrair métodos grandes da classe para módulos separados
3. Modularizar UI em componentes

## Estrutura após refatoração:

```
main.py              → entry point (12 linhas)
app.py               → classe LaserflixNetflix (agora modularizada)
config.py            → constantes
core/                → lógica de negócio (já criado)
ui/                  → componentes Tkinter (próximo passo)
actions/             → ações (próximo passo)
utils/               → helpers (próximo passo)
```
