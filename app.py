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

    # --- CUSTOM CSS INJECTION (BOUTIQUE LAW FIRM STYLE) ---
    st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Montserrat:wght@300;400;600&display=swap');

            /* Global Settings */
            html, body, [class*="css"] {
                font-family: 'Montserrat', sans-serif;
                color: #e2e8f0;
            }
            
            h1, h2, h3 {
                font-family: 'Playfair Display', serif;
            }

            /* Background - Deep Petrol Blue */
            .stApp {
                background-color: #0d1b2a;
                background-image: radial-gradient(circle at 50% 0%, #1b263b 0%, #0d1b2a 70%);
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Hero Section */
            .hero-container {
                text-align: center;
                padding: 6rem 1rem 4rem 1rem;
                max-width: 800px;
                margin: 0 auto;
            }
            .hero-title {
                font-size: 3.5rem;
                font-weight: 400;
                color: #ffffff;
                margin-bottom: 1rem;
                letter-spacing: 2px;
            }
            .hero-subtitle {
                font-family: 'Montserrat', sans-serif;
                font-size: 1.1rem;
                color: #c5a059; /* Gold */
                text-transform: uppercase;
                letter-spacing: 4px;
                margin-bottom: 4rem;
            }

            /* Login Container - Minimalist */
            .login-container {
                max-width: 400px;
                margin: 0 auto;
                text-align: center;
                padding: 2rem;
            }

            /* Inputs - Minimalist Transparent */
            .stTextInput > div > div > input {
                background-color: transparent;
                border: none;
                border-bottom: 2px solid #c5a059; /* Gold Border */
                border-radius: 0;
                padding: 15px 5px;
                font-size: 18px;
                color: #ffffff;
                text-align: center;
                font-family: 'Montserrat', sans-serif;
            }
            .stTextInput > div > div > input:focus {
                box-shadow: none;
                border-bottom: 2px solid #ffffff;
            }
            /* Placeholder color hack */
            .stTextInput > div > div > input::placeholder {
                color: #64748b;
            }

            /* Buttons - Rectangular Gold */
            .stButton > button {
                background-color: #c5a059; /* Gold */
                color: #0d1b2a; /* Dark Text */
                border-radius: 0px; /* Rectangular */
                padding: 16px 40px;
                border: none;
                font-family: 'Montserrat', sans-serif;
                text-transform: uppercase;
                letter-spacing: 3px;
                font-weight: 600;
                font-size: 14px;
                width: 100%;
                margin-top: 2rem;
                transition: all 0.4s ease;
            }
            .stButton > button:hover {
                background-color: #ffffff;
                color: #0d1b2a;
                letter-spacing: 5px; /* Expand on hover */
            }

            /* Footer */
            .footer-text {
                text-align: center;
                color: #415a77;
                font-size: 0.75rem;
                margin-top: 6rem;
                font-family: 'Montserrat', sans-serif;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            
            /* Upload Area (Logged In) */
             [data-testid="stFileUploader"] {
                background-color: rgba(255,255,255,0.03);
                border: 1px solid #1b263b;
                border-radius: 0px;
                padding: 40px;
                text-align: center;
            }
            [data-testid="stFileUploader"] div {
                color: #94a3b8;
            }
            
            /* Analysis Text */
            .analysis-text {
                color: #e2e8f0;
                font-family: 'Montserrat', sans-serif;
                line-height: 1.8;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. Session State Logic
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # 2. View Controller
    if not st.session_state.logged_in:
        # --- LANDING PAGE VIEW ---
        
        # Hero Section
        st.markdown("""
            <div class="hero-container">
                <h1 class="hero-title">Advogado de Bolso</h1>
                <div class="hero-subtitle">Advocacia Digital Inteligente</div>
            </div>
        """, unsafe_allow_html=True)

        # Login Area (Minimalist)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            password = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="CHAVE DE ACESSO")
            
            if st.button("ACESSAR SISTEMA"):
                if password == "ALUGUEL2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Acesso negado.")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class="footer-text">
                © 2025 Advogado de Bolso • Private Client Services
            </div>
        """, unsafe_allow_html=True)

    else:
        # --- APP INTERFACE (LOGGED IN) ---
        
        st.markdown("""
            <div style="text-align: center; margin-bottom: 4rem; margin-top: 2rem;">
                <h2 style="font-family: 'Playfair Display', serif; color: #c5a059; font-size: 2.5rem; font-weight: 400;">Análise Contratual</h2>
                <p style="color: #94a3b8; font-size: 1rem; letter-spacing: 1px; text-transform: uppercase;">Portal do Cliente</p>
            </div>
        """, unsafe_allow_html=True)

        # Main Content
        with st.container():
            uploaded_file = st.file_uploader("Carregar Documento (PDF)", type="pdf")

            if uploaded_file is not None:
                with st.spinner("Processando..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success(f"Documento carregado. ({len(text)} caracteres)")
                    
                    if st.button("EXECUTAR ANÁLISE"):
                        with st.spinner("Realizando auditoria jurídica..."):
                            # 1. Análise Técnica
                            analysis = analyze_contract(text)
                            
                            st.markdown("### Parecer Técnico")
                            st.markdown(f'<div class="analysis-text">{analysis}</div>', unsafe_allow_html=True)
                            
                            # 2. Gerar Mensagem de Negociação
                            st.markdown("---")
                            st.markdown("### Minuta de Negociação")
                            st.info("Texto formal para comunicação com a contraparte.")
                            
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
                                    
                                    st.text_area("Copiar texto:", value=negotiation_msg, height=300)
                                except Exception as e:
                                    st.error(f"Erro na geração da minuta: {e}")

if __name__ == "__main__":
    main()
