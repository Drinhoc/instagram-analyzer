"""
COLETOR DE DADOS DO INSTAGRAM
Usa Instagrapi para coletar posts e comentários
Suporta contas normais e verificadas
"""

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, PleaseWaitFewMinutes
import time
import json
from datetime import datetime
from config import CONFIG


class ColetorInstagram:
    """Classe para coletar dados do Instagram"""
    
    def __init__(self):
        self.client = None
        self.username = CONFIG["INSTAGRAM_USER"]
        self.password = CONFIG["INSTAGRAM_PASS"]
        self.eh_conta_verificada = False
        
    def login(self):
        """Faz login no Instagram"""
        print("🔐 Fazendo login no Instagram...")
        
        try:
            self.client = Client()
            self.client.delay_range = [1, 3]
            
            # Tenta fazer login
            self.client.login(self.username, self.password)
            
            # Verifica se é conta comercial/verificada
            if CONFIG["COLETAR_METRICAS_VERIFICADA"]:
                self._verificar_tipo_conta()
            
            print(f"✅ Login realizado! (@{self.username})")
            return True
            
        except ChallengeRequired:
            print("\n⚠️  Instagram pediu verificação de segurança.")
            print("    Solução:")
            print("    1. Abra o app do Instagram no celular")
            print("    2. Faça login normalmente")
            print("    3. Tente rodar o script novamente")
            return False
            
        except LoginRequired:
            print("❌ Erro de login. Verifique usuário e senha no config.py")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao fazer login: {e}")
            return False
    
    def _verificar_tipo_conta(self):
        """Verifica se a conta logada tem acesso a métricas extras"""
        try:
            user_id = self.client.user_id_from_username(self.username)
            info = self.client.user_info(user_id)
            
            if info.is_business:
                self.eh_conta_verificada = True
                print("    ✨ Conta comercial detectada - métricas extras disponíveis!")
            else:
                print("    ℹ️  Conta pessoal - métricas básicas apenas")
                
        except:
            pass
    
    def buscar_perfil_info(self, username):
        """Busca informações do perfil"""
        try:
            username = username.replace("@", "")
            
            user_id = self.client.user_id_from_username(username)
            info = self.client.user_info(user_id)
            
            perfil_data = {
                "username": info.username,
                "nome_completo": info.full_name,
                "biografia": info.biography,
                "seguidores": info.follower_count,
                "seguindo": info.following_count,
                "total_posts": info.media_count,
                "eh_comercial": info.is_business,
                "eh_verificado": info.is_verified,
            }
            
            return perfil_data
            
        except Exception as e:
            print(f"⚠️  Erro ao buscar perfil {username}: {e}")
            return None
    
    def coletar_posts_recentes(self, username, quantidade=10):
        """Coleta os últimos N posts de um perfil"""
        print(f"\n📸 Coletando últimos {quantidade} posts de @{username}...")
        
        try:
            username = username.replace("@", "")
            user_id = self.client.user_id_from_username(username)
            
            # Busca posts
            medias = self.client.user_medias(user_id, amount=quantidade)
            
            posts_dados = []
            
            for i, media in enumerate(medias, 1):
                print(f"  📄 Post {i}/{len(medias)}: {media.code}")
                
                post_info = {
                    "id": media.id,
                    "codigo": media.code,
                    "url": f"https://www.instagram.com/p/{media.code}/",
                    "tipo": self._tipo_post_nome(media.media_type),
                    "caption": media.caption_text if media.caption_text else "",
                    "data": media.taken_at.isoformat(),
                    "likes": media.like_count,
                    "comentarios_count": media.comment_count,
                    "visualizacoes": media.play_count if hasattr(media, 'play_count') else 0,
                }
                
                # Métricas extras se for conta verificada
                if self.eh_conta_verificada and CONFIG["COLETAR_METRICAS_VERIFICADA"]:
                    try:
                        insights = self.client.insights_media(media.id)
                        post_info.update({
                            "alcance": insights.get('reach', 0),
                            "impressoes": insights.get('impressions', 0),
                            "salvamentos": insights.get('saved', 0),
                        })
                    except:
                        pass  # Se falhar, ignora
                
                posts_dados.append(post_info)
                
                # Delay entre posts
                if i < len(medias):
                    time.sleep(CONFIG["DELAY_ENTRE_POSTS"])
            
            print(f"✅ {len(posts_dados)} posts coletados!")
            return posts_dados
            
        except Exception as e:
            print(f"❌ Erro ao coletar posts: {e}")
            return []
    
    def coletar_comentarios_post(self, media_id):
        """Coleta TODOS os comentários de um post"""
        try:
            print(f"    💬 Coletando comentários...")
            
            # Busca comentários (amount=0 = todos)
            comentarios = self.client.media_comments(media_id, amount=0)
            
            comentarios_dados = []
            
            for comment in comentarios:
                comentario_info = {
                    "id": comment.pk,
                    "usuario": comment.user.username,
                    "nome_completo": comment.user.full_name,
                    "texto": comment.text,
                    "data": comment.created_at_utc.isoformat(),
                    "likes": comment.like_count,
                }
                
                comentarios_dados.append(comentario_info)
            
            print(f"    ✅ {len(comentarios_dados)} comentários coletados")
            return comentarios_dados
            
        except PleaseWaitFewMinutes:
            print("    ⚠️  Instagram pediu para aguardar. Esperando 2 minutos...")
            time.sleep(120)
            return self.coletar_comentarios_post(media_id)
            
        except Exception as e:
            print(f"    ❌ Erro ao coletar comentários: {e}")
            return []
    
    def coletar_tudo(self, username, num_posts=10):
        """
        Função principal: coleta posts + comentários
        """
        dados_completos = {
            "perfil": None,
            "data_coleta": datetime.now().isoformat(),
            "conta_verificada_metricas": self.eh_conta_verificada,
            "posts": []
        }
        
        # 1. Informações do perfil
        print(f"\n{'='*60}")
        print(f"🎯 ANÁLISE DO PERFIL: @{username}")
        print(f"{'='*60}")
        
        perfil_info = self.buscar_perfil_info(username)
        dados_completos["perfil"] = perfil_info
        
        if perfil_info:
            print(f"\n📊 Seguidores: {perfil_info['seguidores']:,}")
            print(f"📊 Posts totais: {perfil_info['total_posts']:,}")
            if perfil_info['eh_verificado']:
                print(f"✅ Conta verificada")
        
        # 2. Posts recentes
        posts = self.coletar_posts_recentes(username, num_posts)
        
        # 3. Comentários de cada post
        print(f"\n{'='*60}")
        print(f"💬 COLETANDO COMENTÁRIOS")
        print(f"{'='*60}")
        
        for i, post in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}] Post: {post['url']}")
            print(f"    ❤️  {post['likes']:,} likes | 💬 {post['comentarios_count']} comentários")
            
            # Coleta comentários
            comentarios = self.coletar_comentarios_post(post['id'])
            post['comentarios'] = comentarios
            
            dados_completos["posts"].append(post)
            
            # Delay entre posts
            if i < len(posts):
                print(f"    ⏱️  Aguardando {CONFIG['DELAY_ENTRE_POSTS']}s...")
                time.sleep(CONFIG["DELAY_ENTRE_POSTS"])
        
        # Salva JSON backup se configurado
        if CONFIG["SALVAR_JSON_BACKUP"]:
            self._salvar_json_backup(dados_completos, username)
        
        return dados_completos
    
    def _salvar_json_backup(self, dados, username):
        """Salva backup dos dados em JSON"""
        import os
        
        dir_json = f"{CONFIG['DIR_OUTPUT']}/backup_json"
        os.makedirs(dir_json, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dir_json}/{username}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Backup JSON salvo: {filename}")
    
    def _tipo_post_nome(self, tipo_num):
        """Converte número do tipo para nome"""
        tipos = {
            1: "Foto",
            2: "Vídeo",
            8: "Carrossel"
        }
        return tipos.get(tipo_num, "Outro")


# ========================================
# TESTE
# ========================================

if __name__ == "__main__":
    print("🧪 Teste do módulo coletor...")
    
    coletor = ColetorInstagram()
    
    if coletor.login():
        print("\n✅ Login OK! Módulo funcionando.")
    else:
        print("\n❌ Erro no login. Verifique config.py")
