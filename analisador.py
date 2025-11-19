"""
ANALISADOR COM GPT-4 - SUPER PRECISO
"""

import openai
import json
from config import CONFIG


class AnalisadorGPT:
    """Análise com GPT-4"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=CONFIG["OPENAI_KEY"])
        self.modelo = CONFIG["MODELO_GPT"]
        self.max_tokens = CONFIG["MAX_TOKENS"]
        self.total_analisado = 0
        self.custo_estimado = 0.0

    def analisar_comentario(self, texto_comentario):
        """Analisa comentário com GPT-4"""
        try:
            prompt = f"""Você é um analista expert em redes sociais. Analise este comentário do Instagram com PRECISÃO:

COMENTÁRIO: "{texto_comentario}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SENTIMENTO (tom emocional geral):
• positivo: Elogios ("amei!", "perfeito!", "top demais"), emojis felizes (❤️😍🥰🔥), entusiasmo, gratidão
• negativo: Críticas ("ruim", "péssimo", "decepcionante"), raiva, frustração, insatisfação clara
• neutro: Perguntas objetivas SEM emoção ("qual o preço?", "tem em azul?"), informações factuais

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 CATEGORIA (tipo de interação - SEJA ESPECÍFICO!):
• elogio: Comentários de aprovação, admiração, satisfação com produto/serviço/conteúdo
  Exemplos: "Que perfeito!", "Adorei a qualidade!", "Sempre impecável ❤️"

• reclamacao: Insatisfação, crítica negativa, problema reportado, experiência ruim
  Exemplos: "Péssimo atendimento", "Produto chegou com defeito", "Muito caro pelo que oferece"

• duvida: Perguntas sobre produto, serviço, disponibilidade, funcionamento, detalhes técnicos
  Exemplos: "Tem na cor vermelha?", "Qual o horário de funcionamento?", "Serve para pele oleosa?"

• sugestao: Ideias de melhoria, feedback construtivo, pedido de novo produto/funcionalidade
  Exemplos: "Deviam fazer em tamanho maior", "Que tal adicionar versão sem açúcar?"

• spam: Links suspeitos, propaganda não relacionada, textos aleatórios/sem sentido, bots
  Exemplos: "Ganhe seguidores bit.ly/xyz", "aaaaaaa", caracteres aleatórios

• outro: Não se encaixa em nenhuma categoria acima (marcações de pessoas, apenas emojis, etc)
  Exemplos: "@maria olha isso", "🔥🔥🔥", "primeira!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ URGÊNCIA (precisa resposta rápida?):
• "sim": Reclamações graves, dúvidas urgentes ("preciso HOJE"), problemas que afetam cliente AGORA
  Exemplos: "Meu pedido não chegou!", "Produto com defeito, como troco?", "Preciso pra amanhã, tem?"

• "nao": Elogios, perguntas gerais sem pressa, feedbacks, curiosidades
  Exemplos: "Amei ❤️", "Vcs entregam em SP?", "Esse produto é vegano?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 INTENÇÃO (objetivo do usuário - O QUE ELE QUER?):
• compra: Interesse direto em comprar, perguntas sobre preço/pagamento/disponibilidade/entrega
  Exemplos: "Quanto custa?", "Tem pronta entrega?", "Aceita cartão?", "Quero 2!", "Link da loja?"

• informacao: Busca detalhes técnicos, esclarecimentos, conhecimento sobre produto/marca/uso
  Exemplos: "Quais os ingredientes?", "Esse modelo serve pra X?", "Como usar?", "É importado?"

• feedback: Compartilhar experiência (positiva/negativa), dar opinião, deixar testemunho
  Exemplos: "Usei e AMEI!", "Não gostei da textura", "Melhor produto que já comprei", "Qualidade caiu"

• engajamento: Apenas interagir socialmente, marcar amigos, expressar emoção sem objetivo comercial
  Exemplos: "@maria vem ver", "❤️❤️❤️", "Maravilhoso!", "Quero muito!", emojis, reações

• reclamacao: Reportar problema, expressar insatisfação, pedir resolução/compensação
  Exemplos: "Produto chegou errado", "Atendimento horrível", "Cobraram 2x no cartão!", "Quero reembolso"

• outro: Spam, mensagens sem sentido, ou não se encaixa nas categorias acima

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 TÓPICO: Identifique o assunto principal em 2-4 palavras específicas
Exemplos: "preço do produto", "qualidade do café", "tempo de entrega", "atendimento ao cliente"

💬 RESPOSTA SUGERIDA:
• Se for elogio: Agradecimento caloroso e emoji
• Se for dúvida: Resposta direta e objetiva (use informações comuns do tipo de negócio)
• Se for reclamação: Pedido de desculpas + oferta de solução
• Se for spam/outro: null

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Retorne APENAS JSON válido:
{{
    "sentimento": "positivo/neutro/negativo",
    "categoria": "elogio/reclamacao/duvida/sugestao/spam/outro",
    "topico": "tema específico em 2-4 palavras",
    "urgencia": "sim/nao",
    "intent": "compra/informacao/feedback/engajamento/reclamacao/outro",
    "resposta_sugerida": "resposta personalizada e amigável OU null"
}}"""

            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": "Você é expert em análise de sentimentos. Seja preciso."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            analise = json.loads(response.choices[0].message.content.strip())

            self.total_analisado += 1
            self._atualizar_custo(response.usage)

            return analise

        except Exception as e:
            print(f"⚠️ Erro: {e}")
            return {
                "sentimento": "neutro",
                "categoria": "outro",
                "topico": "erro",
                "urgencia": "nao",
                "intent": "outro",
                "resposta_sugerida": None
            }

    def _atualizar_custo(self, usage):
        """Calcula custo GPT-4"""
        # GPT-4o-mini: input $0.00015, output $0.0006 por 1K tokens
        custo = (usage.prompt_tokens / 1000 * 0.00015 +
                usage.completion_tokens / 1000 * 0.0006)
        self.custo_estimado += custo