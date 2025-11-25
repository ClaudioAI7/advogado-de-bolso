import streamlit as st
import google.generativeai as genai
import pypdf
import os

# --- Configuration ---
# Security: Read API Key from Streamlit Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Erro de Configuração: API Key não encontrada nos Secrets.")

# --- Helper Functions ---

def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return None

def analyze_contract(text):
    try:
        # Model is already configured globally
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        Você é um advogado especialista em contratos de aluguel. Analise o seguinte contrato e identifique:
        1. Cláusulas Perigosas (riscos para o inquilino).
        2. Pontos de Atenção (ambiguidades).
        3. Veredito Final (seguro ou não).
        
        Contrato:
        {text}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"""
        **Erro na Análise da IA:** {str(e)}
        
        **ANÁLISE DE FALLBACK:**
        
        **Cláusulas Perigosas:**
        *   Não foi possível detectar devido a erro de conexão.
        
        **Pontos de Atenção:**
        *   Verifique manualmente.
        
        **Veredito Final:**
        *   Consulte um advogado real.
        """

# --- Main App ---

def main():
    st.set_page_config(page_title="Advogado de Bolso", page_icon="⚖️", layout="wide")

    # --- MANUAL VISUAL CODE REPLACEMENT ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Montserrat:wght@300;400;600&display=swap');

        /* 1. FUNDO COM IMAGEM E SOBREPOSIÇÃO ESCURA (IGUAL TM ASSOCIADOS) */
        .stApp {
            background-image: linear-gradient(rgba(10, 20, 30, 0.85), rgba(10, 20, 30, 0.95)),
                              url('https://images.unsplash.com/photo-1589829085413-56de8ae18c73?q=80&w=2000&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        /* 2. TIPOGRAFIA DE LUXO */
        h1 {
            font-family: 'Playfair Display', serif !important;
            color: #ffffff !important;
            font-size: 3.8rem !important;
            text-align: center;
            font-weight: 400 !important;
            letter-spacing: 1px;
            margin-top: 50px !important;
        }

        h2 {
            font-family: 'Montserrat', sans-serif !important;
            color: #c5a059 !important; /* DOURADO TM */
            font-size: 1rem !important;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 4px;
            font-weight: 600 !important;
            margin-bottom: 60px !important;
        }

        /* 3. CARD DE LOGIN (Borda Dourada Fina) */
        div[data-testid="stVerticalBlock"] > div:has(input) {
            background: rgba(10, 20, 30, 0.6);
            border: 1px solid #c5a059;
            padding: 40px;
            border-radius: 0px; /* Quadrado elegante */
            max-width: 500px;
            margin: 0 auto;
        }

        /* 4. INPUT E BOTÃO */
        p, label {
            color: #c5a059 !important; /* Labels Dourados */
            font-family: 'Montserrat', sans-serif;
            font-size: 0.8rem;
        }

        input.st-ai {
            background-color: transparent !important;
            color: white !important;
            border: none !important;
            border-bottom: 1px solid #c5a059 !important; /* Apenas linha embaixo */
            border-radius: 0px !important;
        }

        button {
            background-color: #c5a059 !important;
            color: #0a141e !important;
            border-radius: 0px !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: none !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease;
        }
        button:hover {
            background-color: #ffffff !important;
            color: #c5a059 !important;
        }

        /* ESCONDER ELEMENTOS PADRÃO */
        header {visibility: hidden;}
        footer {visibility: hidden;}

    </style>
    """, unsafe_allow_html=True)

    # 1. Session State Logic
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # 2. View Controller
    if not st.session_state.logged_in:
        # --- LANDING PAGE VIEW ---
        
        st.markdown("<h1>Advogado de Bolso</h1>", unsafe_allow_html=True)
        st.markdown("<h2>INTELIGÊNCIA JURÍDICA PRIVADA</h2>", unsafe_allow_html=True)

        # Login Area
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            password = st.text_input("Senha", type="password", label_visibility="visible", placeholder="CÓDIGO DE ACESSO")
            
            if st.button("ENTRAR"):
                if password == "ALUGUEL2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Acesso não autorizado.")

    else:
        # --- APP INTERFACE (LOGGED IN) ---
        
        st.markdown("<h1>Portal do Cliente</h1>", unsafe_allow_html=True)
        st.markdown("<h2>ANÁLISE CONTRATUAL SEGURA</h2>", unsafe_allow_html=True)

        # Main Content
        with st.container():
            uploaded_file = st.file_uploader("Upload Document (PDF)", type="pdf")

            if uploaded_file is not None:
                with st.spinner("Analisando Documento..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success(f"Documento Carregado. ({len(text)} caracteres)")
                    
                    if st.button("EXECUTAR AUDITORIA"):
                        with st.spinner("Processando Análise Jurídica..."):
                            # 1. Análise Técnica
                            analysis = analyze_contract(text)
                            
                            st.markdown("### Parecer Técnico")
                            st.markdown(analysis)
                            
                            # 2. Gerar Mensagem de Negociação
                            st.markdown("---")
                            st.markdown("### Minuta de Negociação")
                            st.info("Texto sugerido para comunicação formal.")
                            
                            with st.spinner("Redigindo minuta..."):
                                try:
                                    model = genai.GenerativeModel('gemini-flash-latest')
                                    msg_prompt = f"""
                                    Com base na seguinte análise de contrato de aluguel, escreva uma mensagem formal, educada e firme para ser enviada ao proprietário/imobiliária.
                                    A mensagem deve solicitar a correção dos pontos críticos e cláusulas perigosas identificadas.
                                    
                                    Análise:
                                    {analysis}
                                    
                                    Escreva apenas o corpo da mensagem (E-mail/WhatsApp).
                                    """
                                    msg_response = model.generate_content(msg_prompt)
                                    negotiation_msg = msg_response.text
                                    
                                    st.text_area("Copiar Texto:", value=negotiation_msg, height=300)
                                except Exception as e:
                                    st.error(f"Erro na geração da minuta: {e}")

if __name__ == "__main__":
    main()
