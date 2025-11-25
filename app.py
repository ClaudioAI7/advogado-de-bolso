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

    # --- CUSTOM CSS INJECTION (LUXURY LAW FIRM STYLE) ---
    st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

            /* Global Settings */
            html, body, [class*="css"] {
                font-family: 'Lato', sans-serif;
                color: #f8fafc; /* Light text for dark background */
            }
            
            h1, h2, h3 {
                font-family: 'Playfair Display', serif;
            }

            /* Background - Midnight Blue */
            .stApp {
                background-color: #0f172a;
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Hero Section */
            .hero-container {
                text-align: center;
                padding: 4rem 1rem 3rem 1rem;
                max-width: 900px;
                margin: 0 auto;
            }
            .hero-logo {
                font-size: 4rem;
                margin-bottom: 1rem;
                display: block;
                color: #c5a059; /* Gold */
            }
            .hero-title {
                font-size: 3rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 1rem;
                letter-spacing: 1px;
            }
            .hero-subtitle {
                font-family: 'Playfair Display', serif;
                font-size: 1.5rem;
                color: #94a3b8;
                font-weight: 400;
                line-height: 1.6;
                margin-bottom: 3rem;
            }

            /* Login Card */
            .login-card {
                background-color: #ffffff;
                padding: 3rem;
                border-radius: 4px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
                max-width: 450px;
                margin: 0 auto;
                text-align: center;
            }
            .login-title {
                font-family: 'Playfair Display', serif;
                font-size: 1.5rem;
                color: #1e293b; /* Dark Blue Text */
                margin-bottom: 2rem;
                font-weight: 600;
            }

            /* Inputs */
            .stTextInput > div > div > input {
                border-radius: 2px;
                border: 1px solid #c5a059; /* Gold Border */
                padding: 12px 16px;
                font-size: 16px;
                color: #1e293b;
                background-color: #ffffff;
            }
            .stTextInput > div > div > input:focus {
                border-color: #b08d45;
                box-shadow: 0 0 0 1px #b08d45;
            }

            /* Buttons */
            .stButton > button {
                background-color: #c5a059; /* Gold Metallic */
                color: white;
                border-radius: 2px;
                padding: 14px 32px;
                border: none;
                font-family: 'Lato', sans-serif;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 700;
                font-size: 14px;
                width: 100%;
                margin-top: 1.5rem;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #b08d45; /* Darker Gold */
                color: white;
                transform: translateY(-1px);
            }

            /* Authority Section */
            .authority-section {
                margin-top: 5rem;
                padding-top: 3rem;
                border-top: 1px solid #1e293b;
            }
            .authority-item {
                text-align: center;
                padding: 1rem;
            }
            .authority-icon {
                color: #c5a059;
                font-size: 2rem;
                margin-bottom: 1rem;
                display: block;
            }
            .authority-title {
                font-family: 'Playfair Display', serif;
                color: #f8fafc;
                font-size: 1.1rem;
                margin-bottom: 0.5rem;
                font-weight: 400;
            }

            /* Footer */
            .footer-text {
                text-align: center;
                color: #64748b;
                font-size: 0.8rem;
                margin-top: 5rem;
                padding-bottom: 2rem;
                font-family: 'Lato', sans-serif;
                letter-spacing: 1px;
            }
            
            /* Upload Area (Logged In) */
             [data-testid="stFileUploader"] {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 30px;
                text-align: center;
            }
            [data-testid="stFileUploader"] div {
                color: #cbd5e1;
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
                <span class="hero-logo">⚖️</span>
                <h1 class="hero-title">Advogado de Bolso</h1>
                <h2 class="hero-subtitle">Blindagem jurídica para seu contrato de aluguel. Identifique riscos financeiros e cláusulas abusivas antes de assinar.</h2>
            </div>
        """, unsafe_allow_html=True)

        # Login Area (Card)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="login-card"><div class="login-title">Acesso ao Sistema</div>', unsafe_allow_html=True)
            
            password = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Chave de Acesso")
            
            if st.button("ENTRAR"):
                if password == "ALUGUEL2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Credencial inválida.")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Authority Section
        st.markdown('<div class="authority-section"></div>', unsafe_allow_html=True)
        
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("""
                <div class="authority-item">
                    <span class="authority-icon">⚖️</span>
                    <div class="authority-title">Compliance com a Lei do Inquilinato</div>
                </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
                <div class="authority-item">
                    <span class="authority-icon">🛡️</span>
                    <div class="authority-title">Análise de Risco Financeiro</div>
                </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
                <div class="authority-item">
                    <span class="authority-icon">📝</span>
                    <div class="authority-title">Minuta de Negociação Inclusa</div>
                </div>
            """, unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class="footer-text">
                © 2025 Advogado de Bolso • Segurança de Dados Bancária (SSL)
            </div>
        """, unsafe_allow_html=True)

    else:
        # --- APP INTERFACE (LOGGED IN) ---
        
        st.markdown("""
            <div style="text-align: center; margin-bottom: 3rem; margin-top: 2rem;">
                <h2 style="font-family: 'Playfair Display', serif; color: #ffffff; font-size: 2.5rem;">Análise Contratual</h2>
                <p style="color: #94a3b8; font-size: 1.1rem;">Submeta o documento para revisão técnica.</p>
            </div>
        """, unsafe_allow_html=True)

        # Main Content
        with st.container():
            uploaded_file = st.file_uploader("Selecione o arquivo PDF", type="pdf")

            if uploaded_file is not None:
                with st.spinner("Processando documento..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success(f"Documento processado com êxito. ({len(text)} caracteres)")
                    
                    if st.button("INICIAR ANÁLISE TÉCNICA"):
                        with st.spinner("Examinando cláusulas contratuais..."):
                            # 1. Análise Técnica
                            analysis = analyze_contract(text)
                            
                            st.markdown("### Parecer Técnico")
                            st.markdown(analysis)
                            
                            # 2. Gerar Mensagem de Negociação
                            st.markdown("---")
                            st.markdown("### Minuta de Negociação")
                            st.info("Utilize o texto abaixo para formalizar a comunicação com a parte locadora.")
                            
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
