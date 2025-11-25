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

    # --- CUSTOM CSS INJECTION (VISUAL CORRECTION) ---
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

            /* Background Image with Overlay */
            .stApp {
                background-image: linear-gradient(rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.9)), url('https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1920&auto=format&fit=crop');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Hero Section */
            .hero-container {
                text-align: center;
                padding: 10vh 1rem 4rem 1rem;
                max-width: 900px;
                margin: 0 auto;
            }
            .hero-title {
                font-family: 'Playfair Display', serif;
                font-size: 3.5rem;
                font-weight: 700;
                color: #ffffff !important;
                margin-bottom: 1rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .hero-subtitle {
                font-family: 'Montserrat', sans-serif;
                font-size: 1.2rem;
                color: #c5a059 !important; /* Gold */
                text-transform: uppercase;
                letter-spacing: 3px;
                margin-bottom: 3rem;
                font-weight: 600;
            }

            /* Login Container - Glassmorphism */
            .login-container {
                max-width: 400px;
                margin: 0 auto;
                text-align: center;
                padding: 3rem;
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid #c5a059;
                border-radius: 4px;
                backdrop-filter: blur(5px);
            }

            /* Inputs - Minimalist Transparent */
            .stTextInput > div > div > input {
                background-color: transparent;
                border: none;
                border-bottom: 1px solid #c5a059; /* Gold Border */
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
                color: #94a3b8;
            }

            /* Buttons - Gold Solid */
            .stButton > button {
                background-color: #c5a059; /* Gold */
                color: #0f172a; /* Dark Text */
                border-radius: 2px;
                padding: 16px 40px;
                border: none;
                font-family: 'Montserrat', sans-serif;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 700;
                font-size: 14px;
                width: 100%;
                margin-top: 2rem;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #ffffff;
                color: #0f172a;
                transform: translateY(-2px);
            }

            /* Footer */
            .footer-text {
                text-align: center;
                color: #64748b;
                font-size: 0.8rem;
                margin-top: 6rem;
                font-family: 'Montserrat', sans-serif;
            }
            
            /* Upload Area (Logged In) */
             [data-testid="stFileUploader"] {
                background-color: rgba(15, 23, 42, 0.8);
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 40px;
                text-align: center;
            }
            [data-testid="stFileUploader"] div {
                color: #cbd5e1;
            }
            
            /* Analysis Text */
            .analysis-text {
                color: #e2e8f0;
                font-family: 'Montserrat', sans-serif;
                line-height: 1.8;
                background-color: rgba(15, 23, 42, 0.6);
                padding: 2rem;
                border-radius: 4px;
                border-left: 4px solid #c5a059;
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

        # Login Area (Glass Card)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            password = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="CHAVE DE ACESSO")
            
            if st.button("ENTRAR"):
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
                <h2 style="font-family: 'Playfair Display', serif; color: #ffffff; font-size: 2.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">Portal do Cliente</h2>
                <p style="color: #c5a059; font-size: 1rem; letter-spacing: 2px; text-transform: uppercase;">Análise Contratual Segura</p>
            </div>
        """, unsafe_allow_html=True)

        # Main Content
        with st.container():
            uploaded_file = st.file_uploader("Carregar Documento (PDF)", type="pdf")

            if uploaded_file is not None:
                with st.spinner("Processando documento..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success(f"Documento recebido. ({len(text)} caracteres)")
                    
                    if st.button("INICIAR AUDITORIA"):
                        with st.spinner("Realizando análise jurídica..."):
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
