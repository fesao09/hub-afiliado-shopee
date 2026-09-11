import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Hub Afiliado - Shopee & Pinterest", page_icon="🚀", layout="wide")

# Criação do diretório para salvar as mídias
os.makedirs("media", exist_ok=True)

# Função para limpar o estado (Resetar para o próximo produto)
def limpar_campos():
    st.session_state.texto_gerado = ""
    st.session_state.link_shopee_val = ""
    st.session_state.preco_val = ""
    st.session_state.detalhes_val = ""
    st.session_state.link_afiliado_val = ""

# Inicializa variáveis de estado se não existirem
if "texto_gerado" not in st.session_state:
    st.session_state.texto_gerado = ""
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
        with st.spinner("Analisando e estruturando o conteúdo completo..."):
            genai.configure(api_key=api_key)
            
            system_instruction = """
            Atue como meu assistente especialista em curadoria de produtos, estratégia de marketing de afiliados (foco Shopee e Pinterest) e estruturação de conteúdos de alta conversão.
            
            DIRETRIZ DE CONTEÚDO: Seja extremamente completo, rico em detalhes, profissional e aprofundado, exatamente no mesmo nível de densidade de um curador sênior.

            Sempre que receber os dados do produto, retorne o texto estruturado EXATAMENTE com este formato, títulos e emoticons (utilize Markdown):

            📌 **Título do Pin:**
            [Título limpo, chamativo e otimizado para o Pinterest, focando na marca, quantidade e tamanho exatos]

            📝 **Descrição do Pin:**
            [Texto envolvente e rico apresentando o produto, destacando benefícios, dores e utilidade. Termine com a chamada para ação informando o preço exato e a Shopee]

            [Bloco de destaque: Parágrafo curto reforçando o grande diferencial do produto em negrito, seguido pelas hashtags oficiais do nicho e o link de afiliado]

            💡 **Configuração rápida:**
            - **Pasta:** [Pasta sugerida alinhada com o nicho]
            - **Interesses / Tags no Pinterest:** [Lista rica de interesses focados em atributos, terminando no próprio produto]
            - **Link de Destino:** [Link fornecido]

            🎬 **Roteiro para Vídeo no Canva (Formato Pinterest 9:16 - 15 a 20 segundos):**
            - **Cena 1 (0s - 03s) - Gancho visual:**
              - *Visual no Canva:* [Descrição rica e detalhada do cenário, cores e elementos visuais]
              - *Áudio/Ritmo:* [Descrição da trilha sonora e ritmo]
            - **Cena 2 (03s - 11s) - Apresentação do produto:**
              - *Visual no Canva:* [Descrição detalhada do foco, close-ups e animações na tela]
              - *Texto na tela:* [Texto exato que aparecerá]
              - *Legenda rápida:* [Legenda de apoio]
            - **Cena 3 (11s - 18s) - Chamada para Ação:**
              - *Visual no Canva:* [Descrição detalhada da tela final, setas e elementos de conversão]
              - *Texto na tela:* [Texto exato de CTA]
              - *Legenda final:* [Legenda de fechamento]

            💬 **Texto para a descrição do Shop Vídeo (150 caracteres com hashtags):**
            [Texto curto, magnético e direto com limite aproximado de 150 caracteres, já incluindo hashtags estratégicas]

            🚀 **Insight de Afiliado:** [TÍTULO DA ANÁLISE EM CAIXA ALTA]
            - **Análise:** [Análise de mercado aprofundada, explicando o comportamento do público-alvo e a urgência da necessidade]
            - **Por que apostar:** [Tópicos detalhados destrinchando os gatilhos mentais aplicados, o apelo da marca, o custo-benefício e o potencial de conversão rápida]
            """
            
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_instruction
            )
            
            conteudo_prompt = [f"Link: {link_shopee}\nPreço: {preco_produto}\nDetalhes: {detalhes_extras}"]
            
            if imagens_upadas:
                img_file = imagens_upadas[0]
                img = Image.open(img_file)
                conteudo_prompt.append(img)
            
            try:
                response = model.generate_content(conteudo_prompt)
                st.session_state.texto_gerado = response.text
                st.success("Conteúdo gerado com sucesso!")
                
            except ResourceExhausted:
                st.error("⏳ Limite da API atingido. Aguarde cerca de 1 minuto ou ative o faturamento no Google AI Studio.")
            except Exception as e:
                st.error(f"Erro ao gerar conteúdo: {e}")

# --- ÁREA DE REVISÃO, EDIÇÃO E CÓPIA RÁPIDA ---
if st.session_state.texto_gerado:
    st.subheader("2. Revisão, Edição e Cópia Rápida")
    st.info("💡 **Dica para o Tablet:** Você pode editar o texto completo abaixo ou usar os blocos para copiar e colar nas redes.")

    # Caixa única de edição geral
    texto_editado = st.text_area(
        "Editor Geral de Conteúdo:", 
        value=st.session_state.texto_gerado, 
        height=450
    )

    meu_link_afiliado = st.text_input("Cole aqui o seu Link de Afiliado final:", key="link_afiliado_val")

    # --- ARMAZENAMENTO EM LOTE ---
    st.subheader("3. Salvar para Postagem")

    if st.button("💾 Salvar na Fila (Excel)", type="secondary"):
        if not texto_editado or not meu_link_afiliado:
            st.warning("Preencha o seu Link de Afiliado antes de salvar.")
        else:
            caminhos_salvos = []
            for arquivo in arquivos_upload:
                caminho_arquivo = os.path.join("media", arquivo.name)
                with open(caminho_arquivo, "wb") as f:
                    f.write(arquivo.getbuffer())
                caminhos_salvos.append(caminho_arquivo)
                
            caminhos_str = " | ".join(caminhos_salvos)

            novo_dado = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Conteúdo Completo": texto_editado,
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
                    
                st.success("Salvo com sucesso na planilha de fila!")
                
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")
