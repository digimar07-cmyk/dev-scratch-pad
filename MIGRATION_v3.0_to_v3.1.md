# 🔄 GUIA DE MIGRAÇÃO: v3.0 → v3.0-stable + v3.1

**Data:** 02/03/2026  
**Razão:** Congelar versão com lógica refinada de IA e criar nova versão para desenvolvimento

---

## 🎯 **Objetivo**

1. 🔒 **v3.0-stable**: Versão intocável com lógica de IA refinada
2. 🚀 **v3.1**: Nova versão para continuar desenvolvimento

---

## 🛠️ **Passos de Migração**

### **Passo 1: Criar v3.0-stable (cópia exata da v3.0)**

```bash
# Clone o repositório
cd dev-scratch-pad

# Copie toda a pasta v3.0 para v3.0-stable
cp -r laserflix_v3.0 laserflix_v3.0-stable

# Commit
git add laserflix_v3.0-stable/
git commit -m "🔒 Criar v3.0-stable - Versão intocável congelada"
git push origin main
```

### **Passo 2: Criar v3.1 (cópia da v3.0 para desenvolvimento)**

```bash
# Copie toda a pasta v3.0 para v3.1
cp -r laserflix_v3.0 laserflix_v3.1

# Atualize versão no README
sed -i 's/v3.0/v3.1/g' laserflix_v3.1/README.md

# Commit
git add laserflix_v3.1/
git commit -m "🚀 Criar v3.1 - Nova versão para desenvolvimento"
git push origin main
```

### **Passo 3: Adicionar avisos na v3.0 original**

```bash
# Criar aviso no README da v3.0
cat > laserflix_v3.0/DEPRECATION_NOTICE.md << 'EOF'
# ⚠️ AVISO DE DEPRECAÇÃO

Esta pasta (laserflix_v3.0) foi duplicada para:

- **laserflix_v3.0-stable**: Versão intocável (referência)
- **laserflix_v3.1**: Versão ativa para desenvolvimento

**NÃO desenvolva mais nesta pasta.** Use a v3.1+.
EOF

git add laserflix_v3.0/DEPRECATION_NOTICE.md
git commit -m "⚠️ Adicionar aviso de deprecação na v3.0 original"
git push origin main
```

---

## 📚 **Estrutura Final Esperada**

```
dev-scratch-pad/
├── laserflix_v3.0/              # ⚠️ ORIGINAL (deprecated)
│   └── DEPRECATION_NOTICE.md  # Aviso para usar v3.1
├── laserflix_v3.0-stable/      # 🔒 INTOCÁVEL (referência)
│   ├── README_STABLE.md       # Documentação de congelação
│   ├── ai/                     # Lógica refinada congelada
│   └── ...
└── laserflix_v3.1/             # 🚀 ATIVA (desenvolvimento)
    ├── README.md              # Atualizado para v3.1
    ├── ai/                     # Cópia da v3.0-stable
    └── ...
```

---

## ✅ **Checklist de Validação**

- [ ] v3.0-stable criada (cópia exata da v3.0)
- [ ] v3.0-stable/README_STABLE.md existe
- [ ] v3.1 criada (cópia da v3.0 para desenvolvimento)
- [ ] v3.1/README.md atualizado com versão 3.1
- [ ] v3.0/DEPRECATION_NOTICE.md adicionado
- [ ] Testar v3.1 roda normalmente
- [ ] Confirmar que v3.0-stable não será mais modificada

---

## 📝 **Notas Importantes**

1. **v3.0-stable**: Nunca deve ser modificada sem autorização expressa
2. **v3.1**: Versão ativa - todas as novas features vão aqui
3. **v3.0 original**: Pode ser removida após validação da v3.1

---

## 🚀 **Próximos Passos Após Migração**

1. Validar que v3.1 roda corretamente
2. Fazer backup local da v3.0-stable
3. Continuar desenvolvimento APENAS na v3.1
4. Usar v3.0-stable como referência quando precisar da lógica de IA

---

**Executar em:** Terminal local  
**Tempo estimado:** 5 minutos  
**Riscos:** Nenhum (apenas cópias)
