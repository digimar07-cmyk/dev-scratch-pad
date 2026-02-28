# Laserflix

Aplicação de streaming offline para visualização de mídia local.

## Estrutura do Projeto

```
laserflix/
├── main.py                  # Ponto de entrada principal
├── Laserflix.pyw            # Entrada sem console (Windows)
├── requirements.txt         # Dependências
├── laserflix/               # Pacote principal
│   ├── app.py               # Classe principal da aplicação
│   ├── config.py            # Configurações
│   ├── state.py             # Estado global
│   ├── ui/                  # Interface do usuário
│   │   ├── main_window.py
│   │   ├── pages/           # Páginas da aplicação
│   │   └── widgets/         # Componentes reutilizáveis
│   ├── services/            # Lógica de negócio
│   ├── data/                # Persistência e modelos
│   └── utils/               # Utilitários
└── assets/                  # Recursos (ícones, imagens)
```

## Como executar

### Desenvolvimento
```bash
python main.py
```

### Windows (sem console)
```bash
pythonw Laserflix.pyw
```
ou duplo clique em `Laserflix.pyw`

## Referência
O arquivo original `laserflix_v740_Ofline_Stable.py` foi mantido como referência durante a refatoração.
