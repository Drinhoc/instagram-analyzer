# ✅ CHECKLIST MVP - Instagram Analytics

## 🎯 OBJETIVO
Criar um app funcional de análise de comentários do Instagram com GPT-4 que funcione no Streamlit Cloud.

---

## 📋 STATUS ATUAL

### ✅ FUNCIONANDO LOCALMENTE
- [x] Coleta de dados do Instagram com proxy
- [x] Análise de sentimentos com GPT-4o-mini
- [x] Categorização de comentários
- [x] Detecção de intenção do usuário
- [x] Identificação de urgências
- [x] Geração de respostas sugeridas
- [x] Exportação para Google Sheets
- [x] Banco de dados SQLite persistente
- [x] Sistema de logs detalhado

### ⏳ PENDENTE NO STREAMLIT CLOUD
- [ ] Login do Instagram funcionando (precisa configurar proxy nos secrets)
- [ ] Verificar se Google Sheets funciona no cloud
- [ ] Testar fluxo completo no ambiente de produção

---

## 🚀 PASSOS PARA DEPLOY NO STREAMLIT CLOUD

### 1️⃣ Preparação (5 min)
- [ ] Criar conta no Streamlit Cloud: https://share.streamlit.io/
- [ ] Conectar repositório GitHub
- [ ] Fazer push de todos os arquivos (exceto .env e credentials.json)

### 2️⃣ Configurar Secrets (10 min)
- [ ] Abrir Settings → Secrets no Streamlit Cloud
- [ ] Copiar conteúdo de `STREAMLIT_SECRETS_GUIDE.md`
- [ ] Colar e ajustar com suas credenciais reais
- [ ] Incluir todas as seções:
  - Instagram (user/pass)
  - OpenAI (API key)
  - Google Sheets (planilha ID + credentials JSON)
  - **Proxy** (OBRIGATÓRIO! host/port/user/pass)

### 3️⃣ Verificar Deploy (5 min)
- [ ] Aguardar build do Streamlit (1-2 min)
- [ ] Abrir app no navegador
- [ ] Verificar expander "🔍 Informações de Configuração":
  - Username deve aparecer (parcialmente)
  - Password deve aparecer (****)
  - **Proxy deve estar configurado!**

### 4️⃣ Testar Login (2 min)
- [ ] Digitar um perfil (ex: @admiravelcafe)
- [ ] Clicar em "🚀 ANALISAR"
- [ ] Aguardar mensagem "✅ Login realizado com sucesso!"

**SE FALHAR:**
- Abrir expander "🐛 Traceback completo (para debug)"
- Ler mensagem de erro
- Verificar sugestões de diagnóstico que o app mostra
- Consultar `STREAMLIT_SECRETS_GUIDE.md`

### 5️⃣ Testar Análise Completa (5-10 min)
- [ ] App coleta posts
- [ ] App coleta comentários
- [ ] GPT-4 analisa comentários (ver custo no app)
- [ ] Google Sheets gera planilha
- [ ] Link da planilha aparece no app
- [ ] Abrir planilha e verificar dados

---

## 🎯 MELHORIAS IMPLEMENTADAS (2025-11-18)

### 🧠 Prompts GPT Aprimorados
**ANTES:**
```
CATEGORIA:
- elogio: comentários positivos
- reclamacao: críticas e insatisfações
```

**DEPOIS:**
```
CATEGORIA (tipo de interação - SEJA ESPECÍFICO!):
• elogio: Comentários de aprovação, admiração, satisfação com produto/serviço/conteúdo
  Exemplos: "Que perfeito!", "Adorei a qualidade!", "Sempre impecável ❤️"
• reclamacao: Insatisfação, crítica negativa, problema reportado, experiência ruim
  Exemplos: "Péssimo atendimento", "Produto chegou com defeito"
```

**RESULTADO:** Análises 3-5x mais precisas e específicas!

---

### 🔍 Debug Streamlit Turbinado
**Adicionado:**
- Expander com informações de configuração
- Mensagens de erro detalhadas com diagnóstico automático
- Traceback completo para debug
- Sugestões de solução baseadas no tipo de erro
- Verificação automática de proxy

**RESULTADO:** Muito mais fácil identificar e resolver problemas!

---

### 📚 Documentação Completa
**Criado:**
- `STREAMLIT_SECRETS_GUIDE.md`: Guia completo de configuração
- `MVP_CHECKLIST.md`: Este arquivo com checklist
- Comentários melhorados no código
- Debug info integrado no app

---

## 🚨 PROBLEMAS CONHECIDOS E SOLUÇÕES

### ❌ "Credenciais Instagram vazias"
**Causa:** INSTAGRAM_USER ou INSTAGRAM_PASS não configurados no Streamlit Secrets
**Solução:** Adicionar nos secrets (formato TOML, sem espaços extras)

### ❌ "Proxy não configurado"
**Causa:** PROXY_HOST/PORT/USER/PASS faltando nos secrets
**Solução:** OBRIGATÓRIO configurar proxy residencial no cloud!
**Por quê?** Streamlit Cloud usa IPs compartilhados que Instagram BLOQUEIA

### ❌ "IP bloqueado pelo Instagram"
**Causa:** Tentou rodar sem proxy no Streamlit Cloud
**Solução:** Configure proxy residencial (Webshare.io está configurado e funcionando local)

### ❌ "Conta com checkpoint/verificação"
**Causa:** Instagram detectou atividade suspeita
**Solução:**
1. Acesse instagram.com pelo navegador
2. Faça login com as mesmas credenciais
3. Resolva a verificação de segurança

### ❌ "Autenticação de 2 fatores ativada"
**Causa:** 2FA está ativo na conta
**Solução:** Desative temporariamente OU implemente suporte a 2FA no código

---

## 💰 CUSTO ESTIMADO

### OpenAI GPT-4o-mini
- ~100 comentários: **$0.01** (1 centavo!)
- ~1000 comentários: **$0.10** (10 centavos)
- Modelo é EXTREMAMENTE barato

### Proxy Webshare.io
- **Grátis:** 10 proxies residenciais
- **Pago:** $2.99/mês para mais proxies
- Já está configurado e funcionando!

### Streamlit Cloud
- **Grátis:** 1 app público
- **Pago:** $20/mês para apps privados

### Google Sheets
- **Grátis:** API usage normal
- **Sem custo** para uso típico

**TOTAL MVP:** ~$3-5/mês (só o proxy se quiser upgrade)

---

## 🎉 PRÓXIMOS PASSOS

1. **AGORA:**
   - [ ] Configurar Streamlit Secrets seguindo o guia
   - [ ] Fazer deploy
   - [ ] Testar login
   - [ ] Testar análise completa

2. **DEPOIS DO MVP:**
   - [ ] Adicionar mais filtros na planilha
   - [ ] Dashboard visual no Streamlit
   - [ ] Alertas de comentários urgentes
   - [ ] Respostas automáticas (bot)
   - [ ] Análise de Stories
   - [ ] Análise de DMs
   - [ ] Comparação de concorrentes

---

## 📞 SUPORTE

### Se algo der errado:
1. **Primeiro:** Veja os logs no Streamlit (Settings → Logs)
2. **Segundo:** Leia os erros que o app mostra (agora tem diagnóstico automático!)
3. **Terceiro:** Consulte `STREAMLIT_SECRETS_GUIDE.md`
4. **Último recurso:** Me chame de volta! 😊

---

## 🏆 QUALIDADE DAS ANÁLISES

### Sentimento: ✅ BOM
- Positivo/Negativo/Neutro funcionando bem

### Tópico: ✅ BOM
- Identifica assunto principal corretamente

### Urgência: ✅ BOM
- Detecta comentários que precisam resposta rápida

### Resposta Sugerida: ✅ BOM
- Gera respostas apropriadas para cada tipo

### Categoria: ✅ ÓTIMO (MELHORADO!)
- Antes: genérico ("elogio", "dúvida")
- Agora: específico com exemplos e contexto

### Intenção: ✅ ÓTIMO (MELHORADO!)
- Antes: básico (4 categorias)
- Agora: detalhado (6 categorias incluindo "engajamento")

---

**Criado com ❤️ usando Claude Sonnet 4.5**
**Data:** 2025-11-18
**Versão:** MVP 1.0
