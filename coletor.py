"""
Módulo de coleta de dados do Instagram
Versão 2.0 com PROXY RESIDENCIAL
"""

import instagrapi
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import time
import json
from datetime import datetime
from config import CONFIG, get_proxy_dict


class ColetorInstagram:
    """Coleta dados do Instagram usando proxy residencial"""
    
    def __init__(self):
        """Inicializa cliente com proxy se disponível"""
        self.client = Client()
        self.client.delay_range = [2, 5]  # Delay entre requests (mais seguro)
        
        # Configura proxy se disponível
        proxy_dict = get_proxy_dict()
        if proxy_dict:
            # Instagrapi usa requests internamente, então setamos proxies
            self.client.set_proxy(proxy_dict["https"])
            print(f"✅ Proxy configurado: {CONFIG['PROXY_HOST']}")
        else:
            print("⚠️ Rodando SEM proxy (pode dar bloqueio!)")
    
    def fazer_login(self, username=None, password=None):
        """Faz login no Instagram com tratamento de erros"""
        username = username or CONFIG["INSTAGRAM_USER"]
        password = password or CONFIG["INSTAGRAM_PASS"]
        
        try:
            print(f"🔐 Fazendo login como {username}...")
            
            # Tenta carregar sessão salva (se existir)
            try:
                self.client.load_settings("session.json")
                self.client.login(username, password)
                print("✅ Login realizado com sessão salva!")
            except:
                # Login fresh
                self.client.login(username, password)
                # Salva sessão
                self.client.dump_settings("session.json")
                print("✅ Login realizado! Sessão salva.")
            
            return True
            
        except ChallengeRequired as e:
            print(f"⚠️ Instagram pediu verificação: {e}")
            print("💡 Entre no Instagram pelo app/navegador e confirme que é você!")
            return False
            
        except LoginRequired as e:
            print(f"❌ Erro de login: {e}")
            print("💡 Verifique suas credenciais!")
            return False
            
        except Exception as e:
            erro_msg = str(e).lower()
            
            if "checkpoint" in erro_msg or "challenge" in erro_msg:
                print(f"⚠️ Conta com checkpoint/verificação!")
                print("💡 Resolva no app do Instagram primeiro!")
            elif "ip" in erro_msg or "blacklist" in erro_msg:
                print(f"⚠️ IP bloqueado!")
                if get_proxy_dict():
                    print("💡 Mesmo com proxy, tente mudar de proxy ou aguardar!")
                else:
                    print("💡 CONFIGURE UM PROXY RESIDENCIAL!")
            else:
                print(f"❌ Erro desconhecido: {e}")
            
            return False
    
    def buscar_perfil(self, username):
        """Busca informações do perfil"""
        username = username.replace("@", "")
        
        try:
            print(f"🔍 Buscando perfil @{username}...")
            user_info = self.client.user_info_by_username(username)
            
            perfil = {
                'username': user_info.username,
                'full_name': user_info.full_name,
                'bio': user_info.biography,
                'seguidores': user_info.follower_count,
                'seguindo': user_info.following_count,
                'total_posts': user_info.media_count,
                'foto_perfil': user_info.profile_pic_url.unicode_string() if user_info.profile_pic_url else None,
                'verificado': user_info.is_verified,
                'privado': user_info.is_private,
            }
            
            print(f"✅ Perfil encontrado: {perfil['seguidores']} seguidores")
            return perfil
            
        except Exception as e:
            print(f"❌ Erro ao buscar perfil: {e}")
            raise
    
    def coletar_posts(self, username, quantidade=5):
        """Coleta posts recentes do perfil"""
        username = username.replace("@", "")
        
        try:
            print(f"📸 Coletando {quantidade} posts de @{username}...")
            
            user_id = self.client.user_id_from_username(username)
            medias = self.client.user_medias(user_id, amount=quantidade)
            
            posts = []
            for media in medias:
                post = {
                    'codigo': media.code,
                    'url': f"https://www.instagram.com/p/{media.code}/",
                    'tipo': media.media_type.name if hasattr(media.media_type, 'name') else str(media.media_type),
                    'caption': media.caption_text if media.caption_text else "",
                    'likes': media.like_count,
                    'comentarios_count': media.comment_count,
                    'data_post': media.taken_at.isoformat() if media.taken_at else None,
                    'comentarios': []
                }
                posts.append(post)
            
            print(f"✅ {len(posts)} posts coletados!")
            return posts
            
        except Exception as e:
            print(f"❌ Erro ao coletar posts: {e}")
            raise
    
    def coletar_comentarios(self, codigo_post, max_comentarios=100):
        """Coleta comentários de um post"""
        try:
            print(f"💬 Coletando comentários do post {codigo_post}...")
            
            media_id = self.client.media_pk_from_code(codigo_post)
            comentarios_raw = self.client.media_comments(media_id, amount=max_comentarios)
            
            comentarios = []
            for c in comentarios_raw:
                comentario = {
                    'id': str(c.pk),
                    'texto': c.text,
                    'autor': c.user.username,
                    'likes': c.like_count,
                    'data': c.created_at_utc.isoformat() if c.created_at_utc else None,
                }
                comentarios.append(comentario)
            
            print(f"✅ {len(comentarios)} comentários coletados!")
            return comentarios
            
        except Exception as e:
            print(f"⚠️ Erro ao coletar comentários: {e}")
            return []
    
    def coletar_tudo(self, username, num_posts=5):
        """Coleta perfil + posts + comentários"""
        print(f"\n{'='*60}")
        print(f"🎯 COLETANDO DADOS DE @{username}")
        print(f"{'='*60}\n")
        
        # Busca perfil
        perfil = self.buscar_perfil(username)
        
        # Coleta posts
        posts = self.coletar_posts(username, num_posts)
        
        # Coleta comentários de cada post
        for post in posts:
            comentarios = self.coletar_comentarios(post['codigo'], CONFIG["MAX_COMENTARIOS_POR_POST"])
            post['comentarios'] = comentarios
            time.sleep(2)  # Pausa entre posts (segurança)
        
        resultado = {
            'perfil': perfil,
            'posts': posts
        }
        
        print(f"\n{'='*60}")
        print(f"✅ COLETA FINALIZADA!")
        print(f"📊 {len(posts)} posts, {sum(len(p['comentarios']) for p in posts)} comentários")
        print(f"{'='*60}\n")
        
        return resultado


# Teste rápido
if __name__ == "__main__":
    coletor = ColetorInstagram()
    
    if coletor.fazer_login():
        dados = coletor.coletar_tudo("instagram", num_posts=2)
        print(json.dumps(dados, indent=2, ensure_ascii=False))
