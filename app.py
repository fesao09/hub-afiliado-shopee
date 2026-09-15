import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import pandas as pd
import json
import os
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Hub Omnichannel - Afiliado Shopee", page_icon="🚀", layout="wide")

# Criação do diretório para salvar as mídias locais
os.makedirs("media", exist_ok=True)

# Função para limpar os campos da tela
def limpar_campos():
    st.session_state.dados_pinterest = {}
    st.session_state.dados_insta = {}
    st.session_state.dados_tiktok = {}
    st.session_state.link_shopee_val = ""
    st.session_state.preco_val = ""
    st.session_state.detalhes_val = ""
    st.session_state.link_afiliado_val = ""

# Inicialização de variáveis de estado
if "dados_pinterest" not in st.session_state:
    st.session_state.dados_pinterest = {}
if "dados_insta" not in st.session_state:
    st.session_state.dados_insta = {}
if "dados_tiktok" not in st.session_state:
    st.session_state.dados_tiktok = {}
if "link_shopee_val" not in st.session_state:
    st.session_state.link_shopee_val = ""
if "preco_val" not in st.session_state:
    st.session_state.preco_val = ""
if "detalhes_val" not in st.session_state:
    st.session_state.detalhes_val = ""
if "link_afiliado_val" not in st.session_state:
    st.session_state.link_afiliado_val = ""

st.title("🚀 Hub Omnichannel de Afiliado - Shopee & Redes Sociais")

# --- BARRA LATERAL: CONFIGURAÇÕES E GESTÃO ---
st.sidebar.header("⚙️ Configurações & Ações")
api_key = st.sidebar.text_input("Chave API do Gemini:", type="password")

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Limpar Todos os Campos", type="secondary", on_click=limpar_campos):
    st.sidebar.success("Campos limpos com sucesso!")

# --- ÁREA COMUM DE ENTRADA DE DADOS ---
st.subheader("1. Dados Base do Produto & Mídia")

col1, col2 = st.columns(2)
with col1:
    link_shopee = st.text_input("Link do Produto (Shopee):", key="link_shopee_val")
with col2:
    preco_produto = st.text_input("Preço Promocional (Opcional):", key="preco_val")

detalhes_extras = st.text_area("Detalhes extras (nome do produto, marca, diferenciais ou mensagem da Shopee):", key="detalhes_val", height=80)

# Uploader de Mídia
arquivos_upload = st.file_uploader(
    "Faça upload dos arquivos de mídia (Máx: 1 Imagem e 1 Vídeo)", 
    type=["png", "jpg", "jpeg", "mp4", "mov"], 
    accept_multiple_files=True
)

imagens_upadas = [f for f in arquivos_upload if f.type.startswith('image')]
videos_upados = [f for f in arquivos_upload if f.type.startswith('video')]

if len(imagens_upadas) > 1 or len(videos_upados) > 1:
    st.warning("⚠️ Atenção: A estrutura aceita apenas 1 imagem e 1 vídeo. Remova os excedentes.")
    pode_gerar = False
else:
    pode_gerar = True

st.markdown("---")

# --- SISTEMA DE ABAS (TABS) PARA CADA REDE ---
aba_pinterest, aba_insta, aba_tiktok, aba_historico = st.tabs([
    "📌 Pinterest & Shopee Vídeo", 
    "📸 Instagram (Reels & Stories)", 
    "🎵 TikTok", 
    "📊 Histórico & Status de Postagem"
])

# ==========================================
# ABA 1: PINTEREST & SHOPEE VÍDEO
# ==========================================
with aba_pinterest:
    st.header("📌 Gerador para Pinterest & Shopee Vídeo")
    
    if st.button("🧠 Gerar Conteúdo para Pinterest", type="primary") and pode_gerar:
        if not api_key:
            st.warning("⚠️ Insira sua Chave API do Gemini na barra lateral.")
        elif not link_shopee and not detalhes_extras and not imagens_upadas:
            st.warning("⚠️ Forneça o link, detalhes do produto ou uma imagem.")
        else:
            with st.spinner("Gerando curadoria completa para o Pinterest..."):
                genai.configure(api_key=api_key)
                
                system_instruction = """
                Atue como especialista em curadoria de produtos e marketing de afiliados (Pinterest e Shopee).
                A descrição do Pin deve ter RIGOROSAMENTE NO MÁXIMO 800 CARACTERES.
                Retorne APENAS um JSON válido com as chaves:
                - "titulo": Título limpo e otimizado para o Pinterest.
                - "descricao": Texto envolvente da descrição (máx 800 caracteres).
                - "bloco_destaque": Parágrafo de destaque com diferencial em negrito e hashtags oficiais.
                - "pasta": Pasta sugerida.
                - "interesses": Interesses e tags recomendadas.
                - "roteiro_estatico": Sugestão de design para Pin Estático.
                - "roteiro_video": Roteiro detalhado para Vídeo Canva (9:16).
                - "texto_shop": Texto para Shop Vídeo (máx 150 caracteres).
                - "insight": Análise estratégica de afiliado.
                """
                
                model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction, generation_config={"response_mime_type": "application/json"})
                conteudo_prompt = [f"Link: {link_shopee}\nPreço: {preco_produto}\nDetalhes: {detalhes_extras}"]
                if imagens_upadas:
                    conteudo_prompt.append(Image.open(imagens_upadas[0]))
                
                try:
                    response = model.generate_content(conteudo_prompt)
                    st.session_state.dados_pinterest = json.loads(response.text)
                    st.success("Conteúdo do Pinterest gerado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # Campos editáveis Pinterest
    p_data = st.session_state.dados_pinterest
    p_titulo = st.text_input("📌 Título do Pin:", value=p_data.get("titulo", ""))
    p_desc = st.text_area("📝 Descrição do Pin (Máx 800 chars):", value=p_data.get("descricao", ""), height=100)
    p_bloco = st.text_area("✨ Bloco de Destaque & Hashtags:", value=p_data.get("bloco_destaque", ""), height=70)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p_pasta = st.text_input("📁 Pasta:", value=p_data.get("pasta", ""))
    with col_p2:
        p_tags = st.text_input("🏷️ Tags:", value=p_data.get("interesses", ""))
        
    p_estatico = st.text_area("🖼️ Roteiro Pin Estático:", value=p_data.get("roteiro_estatico", ""), height=100)
    p_video = st.text_area("🎬 Roteiro Vídeo Canva (9:16):", value=p_data.get("roteiro_video", ""), height=180)
    p_shop = st.text_area("💬 Texto Shop Vídeo:", value=p_data.get("texto_shop", ""), height=70)
    p_insight = st.text_area("🚀 Insight de Afiliado:", value=p_data.get("insight", ""), height=100)
    
    link_afiliado_p = st.text_input("🔗 Link de Afiliado Final (Pinterest):", key="afiliado_p")

    if st.button("💾 Salvar Pinterest na Fila", type="secondary"):
        if not p_titulo or not link_afiliado_p:
            st.warning("Preencha ao menos o Título e o Link de Afiliado.")
        else:
            novo_registro = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Plataforma": "Pinterest",
                "Título / Produto": p_titulo,
                "Link Afiliado": link_afiliado_p,
                "Enviado? (Sim/Não)": "Não",
                "Detalhes Extras": p_desc[:100] + "..."
            }
            df_novo = pd.DataFrame([novo_tab := novo_registro])
            # Salva na fila unificada
            arquivo_excel = "fila_omnichannel.xlsx"
            if os.path.exists(arquivo_excel):
                df_ex = pd.read_excel(arquivo_excel)
                df_final = pd.concat([df_ex, df_novo], ignore_index=True)
                df_final.to_excel(arquivo_excel, index=False)
            else:
                df_novo.to_excel(arquivo_excel, index=False)
            st.success("Salvo na fila de postagem do Pinterest!")


# ==========================================
# ABA 2: INSTAGRAM (REELS & STORIES)
# ==========================================
with aba_insta:
    st.header("📸 Gerador para Instagram (Reels & Stories)")
    
    if st.button("🧠 Gerar Pacote para Instagram", type="primary") and pode_gerar:
        if not api_key:
            st.warning("⚠️ Insira sua Chave API do Gemini na barra lateral.")
        else:
            with st.spinner("Criando estratégia magnética para o Instagram..."):
                genai.configure(api_key=api_key)
                
                system_instruction = """
                Atue como especialista em Marketing de Afiliados e Copywriting para e-commerce (foco Instagram Reels e Stories).
                Estruture a resposta EXATAMENTE com as seções em JSON válido contendo as chaves:
                - "textos_tela": 3 momentos curtos para a tela do vídeo (Início, Meio, Fim).
                - "legenda_reels": Legenda persuasiva com quebras de linha dinâmicas, CTA para comentar "QUERO" e hashtags estratégicas.
                - "story_1": Roteiro para Story 1 (Abertura / Gancho de curiosidade).
                - "story_2": Roteiro para Story 2 (Detalhe / Desejo e utilidade com chamada).
                - "story_3": Roteiro para Story 3 (Fechamento / Urgência e preço).
                """
                
                model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction, generation_config={"response_mime_type": "application/json"})
                conteudo_prompt = [f"Link: {link_shopee}\nPreço: {preco_produto}\nDetalhes: {detalhes_extras}"]
                if imagens_upadas:
                    conteudo_prompt.append(Image.open(imagens_upadas[0]))
                
                try:
                    response = model.generate_content(conteudo_prompt)
                    st.session_state.dados_insta = json.loads(response.text)
                    st.success("Pacote do Instagram gerado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    i_data = st.session_state.dados_insta
    i_tela = st.text_area("1️⃣ Textos Rápidos para Tela do Vídeo:", value=i_data.get("textos_tela", ""), height=100)
    i_legenda = st.text_area("2️⃣ Legenda para Reels (Estratégia 'Comente QUERO'):", value=i_data.get("legenda_reels", ""), height=180)
    i_s1 = st.text_area("📱 Story 1 (Gancho / Curiosidade):", value=i_data.get("story_1", ""), height=90)
    i_s2 = st.text_area("📱 Story 2 (Detalhe / Desejo):", value=i_data.get("story_2", ""), height=90)
    i_s3 = st.text_area("📱 Story 3 (Fechamento / Urgência):", value=i_data.get("story_3", ""), height=90)
    
    link_afiliado_i = st.text_input("🔗 Link de Afiliado Final (Instagram):", key="afiliado_i")

    if st.button("💾 Salvar Instagram na Fila", type="secondary"):
        if not i_legenda or not link_afiliado_i:
            st.warning("Preencha ao menos a Legenda e o Link de Afiliado.")
        else:
            novo_registro = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Plataforma": "Instagram",
                "Título / Produto": detalhes_extras[:40] or "Produto Instagram",
                "Link Afiliado": link_afiliado_i,
                "Enviado? (Sim/Não)": "Não",
                "Detalhes Extras": i_legenda[:100] + "..."
            }
            df_novo = pd.DataFrame([novo_registro])
            arquivo_excel = "fila_omnichannel.xlsx"
            if os.path.exists(arquivo_excel):
                df_ex = pd.read_excel(arquivo_excel)
                df_final = pd.concat([df_ex, df_novo], ignore_index=True)
                df_final.to_excel(arquivo_excel, index=False)
            else:
                df_novo.to_excel(arquivo_excel, index=False)
            st.success("Salvo na fila de postagem do Instagram!")


# ==========================================
# ABA 3: TIKTOK
# ==========================================
aba_tiktok_view, _ = aba_tiktok, None # Ajuste de escopo visual
with aba_tiktok:
    st.header("🎵 Gerador para TikTok")
    
    if st.button("🧠 Gerar Pacote para TikTok", type="primary") and pode_gerar:
        if not api_key:
            st.warning("⚠️ Insira sua Chave API do Gemini na barra lateral.")
        else:
            with st.spinner("Criando conteúdo viral para o TikTok..."):
                genai.configure(api_key=api_key)
                
                system_instruction = """
                Atue como especialista em Marketing de Afiliados e Copywriting para TikTok.
                Estruture a resposta EXATAMENTE em JSON válido contendo as chaves:
                - "textos_tela": 3 momentos curtos para a tela do vídeo (Gancho, Benefício, CTA).
                - "legenda_tiktok": Legenda direta, focada em curiosidade e desejo, com CTA para Link na Bio ou comentar "QUERO" e hashtags em alta.
                """
                
                model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction, generation_config={"response_mime_type": "application/json"})
                conteudo_prompt = [f"Link: {link_shopee}\nPreço: {preco_produto}\nDetalhes: {detalhes_extras}"]
                if imagens_upadas:
                    conteudo_prompt.append(Image.open(imagens_upadas[0]))
                
                try:
                    response = model.generate_content(conteudo_prompt)
                    st.session_state.dados_tiktok = json.loads(response.text)
                    st.success("Pacote do TikTok gerado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    t_data = st.session_state.dados_tiktok
    t_tela = st.text_area("1️⃣ Textos para Tela do Vídeo (TikTok):", value=t_data.get("textos_tela", ""), height=100)
    t_legenda = st.text_area("2️⃣ Legenda para TikTok (Curiosidade & Desejo):", value=t_data.get("legenda_tiktok", ""), height=150)
    
    link_afiliado_t = st.text_input("🔗 Link de Afiliado Final (TikTok):", key="afiliado_t")

    if st.button("💾 Salvar TikTok na Fila", type="secondary"):
        if not t_legenda or not link_afiliado_t:
            st.warning("Preencha a Legenda e o Link de Afiliado.")
        else:
            novo_registro = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Plataforma": "TikTok",
                "Título / Produto": detalhes_extras[:40] or "Produto TikTok",
                "Link Afiliado": link_afiliado_t,
                "Enviado? (Sim/Não)": "Não",
                "Detalhes Extras": t_legenda[:100] + "..."
            }
            df_novo = pd.DataFrame([novo_registro])
            arquivo_excel = "fila_omnichannel.xlsx"
            if os.path.exists(arquivo_excel):
                df_ex = pd.read_excel(arquivo_excel)
                df_final = pd.concat([df_ex, df_novo], ignore_index=True)
                df_final.to_excel(arquivo_excel, index=False)
            else:
                df_novo.to_excel(arquivo_excel, index=False)
            st.success("Salvo na fila de postagem do TikTok!")


# ==========================================
# ABA 4: HISTÓRICO & STATUS DE POSTAGEM (CRM)
# ==========================================
with aba_historico:
    st.header("📊 Gestão de Fila e Status de Envio")
    st.info("Aqui você acompanha tudo o que já foi gerado e pode atualizar o status de postagem para cada rede social.")

    arquivo_excel = "fila_omnichannel.xlsx"
    
    if os.path.exists(arquivo_excel):
        df_historico = pd.read_excel(arquivo_excel)
        
        # Exibe a tabela interativa onde o usuário pode alterar colunas (como o status de enviado)
        st.write("**Sua Fila de Produtos e Redes:**")
        
        # Editor de dados interativo do Streamlit (Permite alterar o status "Enviado?" direto na tela)
        df_editado = st.data_editor(
            df_historico, 
            num_rows="dynamic",
            key="editor_tabela"
        )
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            if st.button("💾 Salvar Alterações de Status"):
                df_editado.to_excel(arquivo_excel, index=False)
                st.success("Status atualizados com sucesso!")
        with col_h2:
            with open(arquivo_excel, "rb") as f:
                st.download_button(
                    label="📊 Baixar Planilha Atualizada (.xlsx)",
                    data=f,
                    file_name="fila_omnichannel_afiliado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("Nenhum produto salvo na fila omnichannel ainda. Gere e salve conteúdos nas abas anteriores!")
