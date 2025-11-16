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
            prompt = f"""Analise este comentário do Instagram:

COMENTÁRIO: "{texto_comentario}"

SENTIMENTO:
- positivo: elogios, emojis felizes (❤️😍🥰), "amei", "adorei", "perfeito", "top"
- negativo: reclamações, "ruim", "péssimo", "caro", críticas
- neutro: APENAS perguntas sem emoção tipo "qual o preço?"

CATEGORIA:
- elogio: comentários positivos
- reclamacao: críticas e insatisfações
- duvida: perguntas
- sugestao: ideias
- spam: links ou inútil
- outro: nenhuma acima

URGÊNCIA: "sim" se precisa resposta rápida, "nao" se não

INTENÇÃO:
- compra: quer comprar/saber preço
- informacao: quer saber mais
- feedback: dando opinião
- reclamacao: reclamando
- outro: nenhuma

Retorne APENAS JSON:
{{
    "sentimento": "positivo/neutro/negativo",
    "categoria": "elogio/reclamacao/duvida/sugestao/spam/outro",
    "topico": "tema em 2-3 palavras",
    "urgencia": "sim/nao",
    "intent": "compra/informacao/feedback/reclamacao/outro",
    "resposta_sugerida": "resposta curta ou null"
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