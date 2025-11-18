# 🌐 GUIA COMPLETO: Proxy Residencial para Streamlit

## Por que proxy residencial?
- ✅ IPs de casas REAIS (não de datacenter)
- ✅ Instagram raramente bloqueia
- ✅ 95% de taxa de sucesso
- ✅ Funciona 24/7 no Streamlit Cloud
- 💰 Custo: R$ 25-50/mês

---

## 💰 OPÇÕES DE PROXY (DO MELHOR PRO MAIS BARATO)

### 🥇 **OPÇÃO 1: Webshare Residential (RECOMENDADO)**

**Por quê?**
- ✅ Mais barato ($4.99/10GB)
- ✅ Fácil de configurar
- ✅ Suporte bom
- ✅ Aceita cartão brasileiro

**Link:** https://www.webshare.io/

**Plano recomendado:**
- **Residential Proxy**: $4.99/10GB
- 10GB dura ~1-2 meses de uso moderado

---

### 🥈 **OPÇÃO 2: Smartproxy**

**Por quê?**
- ✅ Muito confiável
- ✅ IPs de 195 países
- ✅ Dashboard bacana
- 💰 Um pouco mais caro ($7/GB)

**Link:** https://smartproxy.com/

**Plano recomendado:**
- **Residential Proxies**: $7/GB (mínimo 8GB = $56)

---

### 🥉 **OPÇÃO 3: Bright Data (ex-Luminati)**

**Por quê?**
- ✅ Mais confiável de todos
- ✅ Usado por empresas grandes
- ✅ Melhor qualidade
- 💰 Mais caro ($10/GB)

**Link:** https://brightdata.com/

**Plano recomendado:**
- **Residential Proxies**: Pay as you go

---

## 🚀 PASSO A PASSO: WEBSHARE (RECOMENDADO)

### 1️⃣ Criar conta

1. Acessa: https://www.webshare.io/
2. Clica em **Sign Up**
3. Preenche email/senha
4. Confirma email

### 2️⃣ Comprar proxy residencial

1. Vai em **Dashboard** → **Residential Proxies**
2. Clica em **Purchase**
3. Escolhe: **10GB por $4.99** (suficiente!)
4. Adiciona cartão
5. Finaliza compra

### 3️⃣ Pegar credenciais

1. Vai em **Proxies** → **Residential**
2. Clica em **Download**
3. Escolhe formato: **Username:Password@Host:Port**
4. Copia a linha que aparecer, exemplo:
   ```
   youruser-rotate:yourpass@p.webshare.io:80
   ```

Vai parecer algo assim:
```
xddyewxz-country-br-rotate:flmpw9zuxfkn@p.webshare.io:80
```

### 4️⃣ Separar as partes

Da linha acima, extrai:
```
PROXY_USER = xddyewxz-country-br-rotate
PROXY_PASS = flmpw9zuxfkn
PROXY_HOST = p.webshare.io
PROXY_PORT = 80
```

### 5️⃣ Adicionar nos Secrets do Streamlit

1. Vai no seu app Streamlit
2. **Settings** → **Secrets**
3. Edita as linhas do proxy:

```toml
# Mantém igual:
INSTAGRAM_USER = "seu_usuario"
INSTAGRAM_PASS = "sua_senha"
OPENAI_KEY = "sk-..."
PLANILHA_ID = "..."

# MUDA APENAS ESSAS 4 LINHAS:
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"
PROXY_USER = "xddyewxz-country-br-rotate"
PROXY_PASS = "flmpw9zuxfkn"

# Google credentials mantém igual:
[google_credentials]
...
```

4. **Save**
5. Aguarda redeploy (1-2 min)

### 6️⃣ TESTA!

1. Abre a URL do Streamlit
2. Deve aparecer:
   ```
   🌐 Usando proxy: p.webshare.io:80
   ✅ Login realizado com sucesso!
   ```
3. **SUCESSO!** 🎉

---

## 🎯 DICAS IMPORTANTES

### Opções extras ao criar usuário:

**Sticky Sessions (recomendado):**
```
username-session-123abc
```
- Usa o mesmo IP por um tempo
- Mais "natural" pro Instagram

**Rotação automática:**
```
username-rotate
```
- Muda IP a cada request
- Mais anônimo

**País específico (MELHOR!):**
```
username-country-br-rotate
```
- Usa IPs do Brasil
- Instagram prefere login do mesmo país

**Recomendação final:**
```
PROXY_USER = "seuuser-country-br-session-abc123"
```

---

## 📊 CONSUMO ESTIMADO

**Com 10GB você consegue:**
- ~2.000-5.000 posts analisados
- ~50.000-100.000 comentários coletados
- ~2-3 meses de uso moderado

**Se acabar:**
- Compra mais 10GB ($4.99)
- Ou espera renovar mensalmente

---

## ⚠️ TROUBLESHOOTING

### "Proxy não funciona"

**Testa primeiro:**
```bash
# Local, com o proxy novo:
python testar_proxy.py
```

Deve mostrar:
```
✅ IPs diferentes! Proxy está ativo!
   Sem proxy: 123.456.789.0
   Com proxy: 200.100.50.25 (BR)
```

### "Ainda dá erro de login"

1. Confirma que copiou credenciais certinho
2. Tenta com `session` no username
3. Aguarda 5-10 min e tenta de novo
4. Contata suporte do Webshare

### "Erro de autenticação do proxy"

- Username/password errados
- Verifica no dashboard do Webshare
- Copia/cola de novo (sem espaços!)

---

## 🔄 OUTROS PROVEDORES

### Smartproxy

**Credenciais ficam assim:**
```
PROXY_HOST = "gate.smartproxy.com"
PROXY_PORT = "7000"
PROXY_USER = "user-USERNAME"
PROXY_PASS = "PASSWORD"
```

### Bright Data

**Credenciais ficam assim:**
```
PROXY_HOST = "zproxy.lum-superproxy.io"
PROXY_PORT = "22225"
PROXY_USER = "lum-customer-CUSTOMER-zone-ZONE"
PROXY_PASS = "PASSWORD"
```

---

## 💡 RESUMO RÁPIDO

1. ✅ Compra Webshare Residential (10GB = $4.99)
2. ✅ Pega credenciais no dashboard
3. ✅ Adiciona nos Secrets do Streamlit
4. ✅ Aguarda redeploy
5. ✅ FUNCIONA! 🎉

**Tempo total: ~10 minutos**

---

## 🆘 PRECISA DE AJUDA?

Me manda:
1. Qual provedor escolheu
2. Qual erro aparece
3. Print das credenciais (pode censurar a senha)

Te ajudo a configurar! 😊

---

**Com proxy residencial, seu app vai funcionar perfeitamente no Streamlit Cloud 24/7!** 🚀
