import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import pandas as pd
import json
import os
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Hub Afiliado - Shopee & Pinterest", page_icon="🚀", layout="wide")

# Criação do diretório para salvar as mídias
os.makedirs("media", exist_ok=True)

# Função para limpar o estado (Resetar para o próximo produto)
def limpar_campos():
    st.session_state.dados_ia = {
        "titulo": "", "descricao": "", "bloco_destaque": "",
        "pasta": "", "interesses": "", "roteiro_video": "",
        "texto_shop": "", "insight": ""
    }
    st.session_state.link_shopee_val = ""
    st.session_state.preco_val = ""
    st.session_state.detalhes_val = ""
    st.session_state.link_afiliado_val = ""

# Inicializa variáveis de estado se não existirem
if "dados_ia" not in st.session_state:
    st.session_state.dados_ia = {
        "titulo": "", "descricao": "", "bloco_destaque": "",
        "pasta": "", "interesses": "", "roteiro_video": "",
        "texto_shop": "", "insight": ""
    }
if "link_shopee_val" not in st.session_state:
    st.session_state.link_shopee_val = ""
if "preco_val" not in st.session_state:
    st.session_state.preco_val = ""
if "detalhes_val" not in st.session_state:
    st.session_state.detalhes_val = ""
if "link_afiliado_val" not in st.session_state:
    st.session_state.link_afiliado_val = ""

st.title("📌 Hub Gerador de Conteúdo - Afiliado Shopee")

# --- CONFIGURAÇÕES E AÇÕES NA BARRA LATERAL ---
st.sidebar.header("⚙️ Configurações & Ações")
api_key = st.sidebar.text_input("Chave API do Gemini:", type="password")

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Limpar Dados / Próximo Item", type="secondary", on_click=limpar_campos):
    st.sidebar.success("Campos limpos com sucesso!")

# Botão de Download da Planilha na Barra Lateral
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Meus Dados")

arquivo_excel = "fila_postagens_shopee.xlsx"

if os.path.exists(arquivo_excel):
    with open(arquivo_excel, "rb") as f:
        st.sidebar.download_button(
            label="📊 Baixar Planilha (Excel)",
            data=f,
            file_name="fila_postagens_shopee.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.sidebar.info("A planilha ainda não foi gerada. Salve pelo menos um produto para criá-la.")


# --- ÁREA DE ENTRADA DE DADOS ---
st.subheader("1. Dados do Produto & Mídia")

col1, col2 = st.columns(2)
with col1:
    link_shopee = st.text_input("Link do Produto (Shopee):", key="link_shopee_val")
with col2:
    preco_produto = st.text_input("Preço Promocional (Opcional):", key="preco_val")

detalhes_extras = st.text_area("Detalhes extras (mensagem de compartilhamento da Shopee com nome e preço):", key="detalhes_val", height=100)

# Uploader de Mídia
st.write("**Arquivos de Mídia (Preparação para Postagem)**")
arquivos_upload = st.file_uploader(
    "Faça upload dos arquivos (Máx: 1 Imagem e 1 Vídeo)", 
    type=["png", "jpg", "jpeg", "mp4", "mov"], 
    accept_multiple_files=True
)

# Validação da regra de 1 vídeo e 1 imagem
imagens_upadas = [f for f in arquivos_upload if f.type.startswith('image')]
videos_upados = [f for f in arquivos_upload if f.type.startswith('video')]

if len(imagens_upadas) > 1 or len(videos_upados) > 1:
    st.warning("⚠️ Atenção: A estrutura do Pin aceita apenas 1 imagem e 1 vídeo. Remova os arquivos excedentes.")
    pode_gerar = False
else:
    pode_gerar = True

# Botão de Geração
if st.button("🧠 Gerar Conteúdo com Gemini", type="primary") and pode_gerar:
    if not api_key:
        st.warning("⚠️ Insira sua Chave API do Gemini na barra lateral.")
    elif not link_shopee and not detalhes_extras and not imagens_upadas:
        st.warning("⚠️ Forneça o link, detalhes do produto ou uma imagem.")
    else:
        with st.spinner("Analisando e separando os conteúdos em campos estruturados..."):
            genai.configure(api_key=api_key)
            
            # System instruction exigindo estritamente um formato JSON estruturado por campos
            system_instruction = """
            Atue como meu assistente especialista em curadoria de produtos, estratégia de marketing de afiliados (foco Shopee e Pinterest) e estruturação de conteúdos de alta conversão.
            
            DIRETRIZ: Seja extremamente completo, rico em detalhes e aprofundado nas respostas.
            Você deve retornar APENAS um objeto JSON válido, contendo exatamente estas chaves:
            - "titulo": Título limpo, chamativo e otimizado para o Pinterest.
            - "descricao": Texto envolvente apresentando o produto, benefícios e CTA com o preço e a Shopee.
            - "bloco_destaque": Parágrafo curto reforçando o diferencial em negrito, seguido pelas hashtags e placeholder para o link.
            - "pasta": Nome da pasta sugerida para o Pinterest.
            - "interesses": Tags e interesses recomendados para o Pinterest.
            - "roteiro_video": Roteiro detalhado para Vídeo no Canva (Cena 1, Cena 2 e Cena 3 completas com visuais e textos).
            - "texto_shop": Texto curto para Shop Vídeo (máx 150 caracteres com hashtags).
            - "insight": Análise estratégica completa (Análise e Por que apostar).
            """
            
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_instruction,
                generation_config={"response_mime_type": "application/json"}
            )
            
            conteudo_prompt = [f"Link: {link_shopee}\nPreço: {preco_produto}\nDetalhes: {detalhes_extras}"]
            
            if imagens_upadas:
                img_file = imagens_upadas[0]
                img = Image.open(img_file)
                conteudo_prompt.append(img)
            
            try:
                response = model.generate_content(conteudo_prompt)
                resultado_json = json.loads(response.text)
                
                # Salva os dados estruturados no state
                st.session_state.dados_ia = resultado_json
                st.success("Conteúdo gerado e separado nos campos com sucesso!")
                
            except ResourceExhausted:
                st.error("⏳ Limite da API atingido. Aguarde cerca de 1 minuto ou ative o faturamento no Google AI Studio.")
            except Exception as e:
                st.error(f"Erro ao gerar conteúdo: {e}")

# --- ÁREA DE REVISÃO E EDIÇÃO EM CAMPOS SEPARADOS ---
if st.session_state.dados_ia["titulo"] or st.session_state.dados_ia["descricao"]:
    st.subheader("2. Revisão e Edição por Campos Individuais")
    st.info("💡 Cada informação está em seu respectivo campo. Você pode ajustar qualquer detalhe antes de salvar na planilha.")

    titulo_edit = st.text_input("📌 Título do Pin:", value=st.session_state.dados_ia.get("titulo", ""))
    descricao_edit = st.text_area("📝 Descrição do Pin:", value=st.session_state.dados_ia.get("descricao", ""), height=120)
    destaque_edit = st.text_area("✨ Bloco de Destaque & Hashtags:", value=st.session_state.dados_ia.get("bloco_destaque", ""), height=80)
    
    col_a, col_b = st.columns(2)
    with col_a:
        pasta_edit = st.text_input("📁 Pasta Sugerida:", value=st.session_state.dados_ia.get("pasta", ""))
    with col_b:
        interesses_edit = st.text_input("🏷️ Interesses / Tags Pinterest:", value=st.session_state.dados_ia.get("interesses", ""))

    roteiro_edit = st.text_area("🎬 Roteiro para Vídeo (Canva 9:16):", value=st.session_state.dados_ia.get("roteiro_video", ""), height=220)
    shop_edit = st.text_area("💬 Texto para Shop Vídeo:", value=st.session_state.dados_ia.get("texto_shop", ""), height=80)
    insight_edit = st.text_area("🚀 Insight de Afiliado:", value=st.session_state.dados_ia.get("insight", ""), height=150)

    meu_link_afiliado = st.text_input("🔗 Cole aqui o seu Link de Afiliado final:", key="link_afiliado_val")

    # --- ARMAZENAMENTO EM LOTE COM COLUNAS EXCLUSIVAS ---
    st.subheader("3. Salvar para Postagem")

    if st.button("💾 Salvar na Fila (Excel)", type="secondary"):
        if not titulo_edit or not meu_link_afiliado:
            st.warning("Preencha ao menos o Título e o Link de Afiliado antes de salvar.")
        else:
            caminhos_salvos = []
            for arquivo in arquivos_upload:
                caminho_arquivo = os.path.join("media", arquivo.name)
                with open(caminho_arquivo, "wb") as f:
                    f.write(arquivo.getbuffer())
                caminhos_salvos.append(caminho_arquivo)
                
            caminhos_str = " | ".join(caminhos_salvos)

            # Cada dado vai perfeitamente para a sua coluna dedicada
            novo_dado = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Título do Pin": titulo_edit,
                "Descrição do Pin": descricao_edit,
                "Bloco Destaque e Tags": destaque_edit,
                "Pasta Sugerida": pasta_edit,
                "Interesses Pinterest": interesses_edit,
                "Roteiro Vídeo Canva": roteiro_edit,
                "Texto Shop Vídeo": shop_edit,
                "Insight de Afiliado": insight_edit,
                "Link Afiliado": meu_link_afiliado,
                "Caminho Arquivos (Mídia)": caminhos_str
            }
            
            df_novo = pd.DataFrame([novo_dado])
            arquivo_excel = "fila_postagens_shopee.xlsx"
            
            try:
                if os.path.exists(arquivo_excel):
                    with pd.ExcelWriter(arquivo_excel, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                        df_existente = pd.read_excel(arquivo_excel)
                        startrow = len(df_existente) + 1
                        df_novo.to_excel(writer, index=False, header=False, startrow=startrow)
                else:
                    df_novo.to_excel(arquivo_excel, index=False, engine='openpyxl')
                    
                st.success("Salvo com sucesso! Cada informação foi para a sua coluna exclusiva na planilha.")
                
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")
            
