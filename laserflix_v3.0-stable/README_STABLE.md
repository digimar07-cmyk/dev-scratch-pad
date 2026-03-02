# 🔒 LASERFLIX v3.0 STABLE - VERSÃO INTOCÁVEL

**Data de Congelação:** 02/03/2026  
**Commit Base:** [dbf58ae9](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/dbf58ae9)

---

## ⚠️ **REGRA FUNDAMENTAL**

**ESTA VERSÃO NÃO PODE SER MODIFICADA SEM AUTORIZAÇÃO EXPRESSA DO USUÁRIO.**

Qualquer melhoria, otimização ou nova feature deve ser implementada na **v3.1+**, mantendo esta versão intacta como referência.

---

## 🎯 **Por Que Esta Versão é Especial**

A v3.0-stable contém **3 semanas de refinamento manual** da lógica de geração de descrições por IA, migrada da v740 original. Qualquer modificação pode quebrar o comportamento refinado que foi validado com centenas de produtos reais.

### **Lógica Refinada Incluída:**

#### **1. Geração COM Ollama** (`ai/text_generator.py`)
- ✅ Raciocínio estruturado em 3 etapas (RACIOCINE antes de escrever)
- ✅ Hierarquia NOME > Visão rigorosamente aplicada
- ✅ Prompts cirúrgicos anti-genericidade
- ✅ Temperature 0.78 (criatividade controlada)
- ✅ Regras obrigatórias explícitas

#### **2. Geração SEM Ollama** (`ai/fallbacks.py`)
- ✅ Detecção inteligente por keywords (cabide, espelho, calendário, etc)
- ✅ Templates específicos para 15+ tipos de peças
- ✅ Cascata: palavra-chave > data > ambiente > função > genérico
- ✅ NUNCA frase padrão igual para todos

#### **3. Análise de Qualidade de Imagem** (`ai/image_analyzer.py`)
- ✅ Filtro de qualidade (brilho, saturação, fundo branco)
- ✅ Moondream com prompt cirúrgico
- ✅ Logs informativos de rejeicão

---

## 📚 **Estrutura da Versão**

```
laserflix_v3.0-stable/
├── ai/                    # Módulos de IA (INTOCÁVEIS)
│   ├── text_generator.py   # Geração COM Ollama (raciocínio estruturado)
│   ├── fallbacks.py        # Geração SEM Ollama (keywords inteligentes)
│   ├── image_analyzer.py   # Filtro de qualidade + moondream
│   ├── ollama_client.py    # Cliente HTTP Ollama
│   └── keyword_maps.py     # Mapas de categorização
├── config/                # Configurações
├── core/                  # Lógica de negócios
├── ui/                    # Interface Tkinter
├── utils/                 # Utilitários
└── main.py                # Entry point
```

---

## 🔧 **Commits Críticos (NÃO REVERTER)**

| Commit | Data | Descrição |
|--------|------|-------------|
| [08809aa1](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/08809aa1) | 02/03/2026 | Restaurar lógica refinada text_generator (COM Ollama) |
| [dbf58ae9](https://github.com/digimar07-cmyk/dev-scratch-pad/commit/dbf58ae9) | 02/03/2026 | Restaurar lógica refinada fallbacks (SEM Ollama) |

---

## 🚧 **Desenvolvimento Futuro**

Para novas features, melhorias ou experimentos:

1. ✅ **Use a v3.1+** (pasta separada)
2. ❌ **NUNCA modifique esta v3.0-stable**
3. ✅ **Copie desta versão** se precisar da lógica de IA
4. ✅ **Mantenha esta versão** como referência eterna

---

## 📝 **Quando Modificar Esta Versão**

**APENAS** com autorização expressa do usuário para:
- Corrigir bugs críticos de segurança
- Atualizar dependências com vulnerabilidades
- Refinar a lógica de IA (com validação prévia)

**TODOS OS OUTROS CASOS:** desenvolver na v3.1+

---

## ✅ **Status de Validação**

- ✅ Lógica de geração COM Ollama testada
- ✅ Lógica de geração SEM Ollama testada
- ✅ Filtro de qualidade de imagem validado
- ✅ Templates contextuais por tipo de peça validados
- ✅ Sistema de cascata de detecção validado

---

**Última Atualização:** 02/03/2026, 15:15 -03  
**Mantenedor:** digimar07-cmyk  
**IA Responsável:** Claude Sonnet 4.5
