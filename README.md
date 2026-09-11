# 📌 Hub Afiliado - Shopee & Pinterest AI

Aplicação web desenvolvida em **Streamlit** e integrada com a **API do Gemini (Google Generative AI)** para automatizar a curadoria de produtos, criação de copies de alta conversão para Pins, roteiros detalhados para vídeos (Canva 9:16) e análises estratégicas de mercado para marketing de afiliados.

## 🚀 Funcionalidades
- **Geração Inteligente via IA:** Analisa o link do produto, preço, detalhes e imagens/vídeos enviados.
- **Estrutura Completa:** Retorna Título otimizado, Descrição comercial, Bloco de destaque com hashtags, Configuração de pastas/tags do Pinterest, Roteiro cena a cena para vídeos, Texto para Shop Vídeo e Insights de Afiliado.
- **Otimizado para Dispositivos Móveis (Tablet/Celular):** Interface limpa com editores e botões de cópia rápida para agilizar a postagem.
- **Gerenciamento de Fila:** Salva automaticamente o lote de produtos estruturados em uma planilha Excel (`.xlsx`) com o registro das mídias locais.
- **Botão de Limpeza Rápida:** Reseta o estado da tela instantaneamente para o próximo item.

## 🛠️ Tecnologias Utilizadas
- **Python**
- **Streamlit** (Interface Web)
- **Google Generative AI (`gemini-2.5-flash`)**
- **Pandas & OpenPyXL** (Manipulação e salvamento de dados)
- **Pillow (PIL)** (Processamento de imagens)

## ⚙️ Como Executar Localmente

1. Clone o repositório ou baixe os arquivos.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt