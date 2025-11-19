# 🔐 GUIA COMPLETO - Streamlit Secrets

## ⚡ CONFIGURAÇÃO STREAMLIT CLOUD

Para fazer o app funcionar no Streamlit Cloud, você PRECISA configurar os secrets corretamente.

### 1️⃣ Acessar Streamlit Cloud

1. Vá em: https://share.streamlit.io/
2. Abra seu app
3. Clique em **"⚙️ Settings"** (canto superior direito)
4. Clique em **"Secrets"**

---

### 2️⃣ Configurar Secrets (formato TOML)

Cole isso no editor de secrets (substitua pelos seus valores reais):

```toml
# ============================================================================
# CREDENCIAIS INSTAGRAM
# ============================================================================
INSTAGRAM_USER = "seu_email@gmail.com"
INSTAGRAM_PASS = "sua_senha_aqui"

# ============================================================================
# OPENAI (GPT-4)
# ============================================================================
OPENAI_KEY = "sk-proj-SUA_CHAVE_OPENAI_AQUI"

# ============================================================================
# GOOGLE SHEETS
# ============================================================================
PLANILHA_ID = "1Ho_Pj_6jP4XkA9L6eflOo9VMJ6IQ99LNaH4lsh4Q2_4"

# ============================================================================
# PROXY RESIDENCIAL (OBRIGATÓRIO NO STREAMLIT CLOUD!)
# ============================================================================
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "7030"
PROXY_USER = "xddyewxz"
PROXY_PASS = "flmpw9zuxfkn"

# ============================================================================
# GOOGLE CREDENTIALS (JSON do Service Account)
# ============================================================================
[google_credentials]
type = "service_account"
project_id = "analise-de-comentarios-478622"
private_key_id = "SEU_PRIVATE_KEY_ID_AQUI"
private_key = "-----BEGIN PRIVATE KEY-----\nSUA_CHAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n"
client_email = "analise@analise-de-comentarios-478622.iam.gserviceaccount.com"
client_id = "SEU_CLIENT_ID_AQUI"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/analise%40analise-de-comentarios-478622.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

---

### 3️⃣ Como pegar as Google Credentials

1. Abra o arquivo `credentials.json` (local)
2. Copie TODO o conteúdo
3. Cole no formato acima (dentro de `[google_credentials]`)

**⚠️ IMPORTANTE:**
- A `private_key` deve ter `\n` para quebras de linha
- Exemplo: `"-----BEGIN PRIVATE KEY-----\nMIIEvAI...\n-----END PRIVATE KEY-----\n"`

---

### 4️⃣ PROXY - Por que é OBRIGATÓRIO no Streamlit Cloud?

❌ **SEM proxy:**
- Streamlit Cloud usa IPs compartilhados
- Instagram detecta e BLOQUEIA esses IPs
- Login SEMPRE falhará

✅ **COM proxy residencial:**
- Você usa um IP residencial "limpo"
- Instagram aceita o login
- Tudo funciona perfeitamente

**Seu proxy atual (Webshare.io):**
- Host: `p.webshare.io`
- Port: `7030`
- User: `xddyewxz`
- Pass: `flmpw9zuxfkn`

---

### 5️⃣ Verificar se está funcionando

Depois de salvar os secrets:

1. O app vai **reiniciar automaticamente**
2. Abra o app e clique em **"🔍 Informações de Configuração"** (expander)
3. Você deve ver:
   - ✅ Username: papo...r.com (24 chars)
   - ✅ Password: ********** (15 chars)
   - ✅ Proxy: p.webshare.io:7030

4. Se aparecer tudo OK mas o login falhar, veja os erros detalhados que o app mostra

---

## 🚨 PROBLEMAS COMUNS

### ❌ "Credenciais Instagram vazias"
**Solução:** Verifique se INSTAGRAM_USER e INSTAGRAM_PASS estão nos secrets (sem espaços extras)

### ❌ "Proxy não configurado"
**Solução:** Adicione PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS nos secrets

### ❌ "IP bloqueado pelo Instagram"
**Solução:** Configure o proxy residencial (obrigatório no cloud!)

### ❌ "Conta com checkpoint/verificação"
**Solução:**
1. Acesse instagram.com pelo navegador
2. Faça login com as mesmas credenciais
3. Resolva qualquer verificação de segurança

### ❌ "Autenticação de 2 fatores ativada"
**Solução:** Desative o 2FA temporariamente na conta do Instagram

---

## 📝 CHECKLIST FINAL

Antes de fazer deploy, confirme:

- [ ] INSTAGRAM_USER configurado no Streamlit Secrets
- [ ] INSTAGRAM_PASS configurado no Streamlit Secrets
- [ ] OPENAI_KEY configurado no Streamlit Secrets
- [ ] PLANILHA_ID configurado no Streamlit Secrets
- [ ] PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS configurados
- [ ] google_credentials configurado (JSON completo do service account)
- [ ] Planilha compartilhada com o service account email
- [ ] Conta Instagram SEM 2FA ativado
- [ ] Conta Instagram SEM checkpoint/verificação pendente

---

## 🎉 TESTANDO O MVP

Quando tudo estiver configurado:

1. Abra o app no Streamlit Cloud
2. Digite um perfil (ex: @admiravelcafe)
3. Clique em "🚀 ANALISAR"
4. Aguarde (pode levar 1-2 minutos)
5. ✅ Planilha gerada com análises GPT!

---

## 💡 DICAS PRO

1. **Logs no Streamlit:**
   - Vá em Settings → Logs
   - Você pode ver prints e erros em tempo real

2. **Restartar app:**
   - Se algo estranho acontecer, clique em "⋮" → "Reboot app"

3. **Custo GPT-4:**
   - GPT-4o-mini é MUITO barato
   - ~100 comentários = $0.01 (1 centavo)
   - Não se preocupe com custo!

4. **Proxy Webshare.io:**
   - Você tem 10 proxies grátis
   - Se precisar de mais, upgrade é barato (~$2.99/mês)

---

**Criado com ❤️ por Claude (Sonnet 4.5)**
**Data:** 2025-11-18
