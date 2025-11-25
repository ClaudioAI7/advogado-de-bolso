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

    # --- CUSTOM CSS INJECTION (CLASSIC LAW FIRM STYLE) ---
    st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

            /* Global Settings */
            html, body, [class*="css"] {
                font-family: 'Lato', sans-serif;
                color: #334155;
            }
            
            h1, h2, h3 {
                font-family: 'Playfair Display', serif;
            }

            /* Background */
            .stApp {
                background-color: #f8fafc;
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Header Section */
            .header-bar {
                background-color: #1e293b; /* Navy Blue */
                padding: 1.5rem 0;
                text-align: center;
                margin-bottom: 3rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .header-logo {
                font-size: 2.5rem;
                margin-right: 10px;
                vertical-align: middle;
            }
            .header-title {
                font-family: 'Playfair Display', serif;
                font-size: 2rem;
                color: #ffffff;
                font-weight: 600;
                letter-spacing: 1px;
                vertical-align: middle;
            }

            /* Hero / Promise */
            .hero-container {
                text-align: center;
                max-width: 800px;
                margin: 0 auto 3rem auto;
                padding: 0 1rem;
            }
            .hero-subtitle {
                font-family: 'Playfair Display', serif;
                font-size: 1.8rem;
                color: #1e293b;
                line-height: 1.4;
                font-weight: 400;
            }

            /* Login Card */
            .login-card {
                background-color: white;
                padding: 3rem;
                border: 1px solid #e2e8f0;
                border-top: 4px solid #c29d59; /* Gold Accent */
                max-width: 450px;
                margin: 0 auto;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            }
            .login-label {
                text-align: center;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #64748b;
                margin-bottom: 1.5rem;
            }

            /* Inputs */
            .stTextInput > div > div > input {
                border-radius: 2px;
                border: 1px solid #cbd5e1;
                padding: 10px 15px;
                font-family: 'Lato', sans-serif;
            }
            .stTextInput > div > div > input:focus {
                border-color: #c29d59;
                box-shadow: 0 0 0 1px #c29d59;
            }

            /* Buttons */
            .stButton > button {
                background-color: #c29d59; /* Gold */
                color: white;
                border-radius: 4px;
                padding: 10px 30px;
                border: none;
                font-family: 'Lato', sans-serif;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 700;
                font-size: 14px;
                width: 100%;
                margin-top: 1rem;
                transition: background-color 0.3s;
            }
            .stButton > button:hover {
                background-color: #a38246;
                color: white;
            }

            /* Footer Icons */
            .footer-section {
                margin-top: 5rem;
                border-top: 1px solid #e2e8f0;
                padding-top: 3rem;
            }
            .footer-item {
                text-align: center;
            }
            .footer-icon {
                color: #c29d59;
                font-size: 2rem;
                margin-bottom: 1rem;
                display: block;
            }
            .footer-title {
                font-family: 'Playfair Display', serif;
                color: #1e293b;
                font-size: 1.1rem;
                margin-bottom: 0.5rem;
            }
            
            /* Upload Area */
             [data-testid="stFileUploader"] {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. Header (Always Visible)
    st.markdown("""
        <div class="header-bar">
            <span class="header-logo">⚖️</span>
            <span class="header-title">Advogado de Bolso</span>
        </div>
    """, unsafe_allow_html=True)

    # 2. Session State Logic
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # 3. View Controller
    if not st.session_state.logged_in:
        # --- LANDING PAGE VIEW ---
        
        # Hero Section
        st.markdown("""
            <div class="hero-container">
                <div class="hero-subtitle">A plataforma que blinda seu contrato de aluguel contra multas e cláusulas abusivas.</div>
            </div>
        """, unsafe_allow_html=True)

        # Login Area (Card)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="login-card"><div class="login-label">Acesso Restrito</div>', unsafe_allow_html=True)
            
            password = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Chave de Acesso")
            
            if st.button("Entrar"):
                if password == "ALUGUEL2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Credencial inválida.")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Footer Section
        st.markdown('<div class="footer-section"></div>', unsafe_allow_html=True)
        
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("""
                <div class="footer-item">
                    <span class="footer-icon">⚖️</span>
                    <div class="footer-title">Análise Técnica</div>
                </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
                <div class="footer-item">
                    <span class="footer-icon">🛡️</span>
                    <div class="footer-title">Segurança Jurídica</div>
                </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
                <div class="footer-item">
                    <span class="footer-icon">🤝</span>
                    <div class="footer-title">Negociação Pronta</div>
                </div>
            """, unsafe_allow_html=True)

    else:
        # --- APP INTERFACE (LOGGED IN) ---
        
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="font-family: 'Playfair Display', serif; color: #1e293b;">Análise Contratual</h2>
                <p style="color: #64748b;">Submeta o documento para revisão jurídica automatizada.</p>
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
                    
                    if st.button("Iniciar Análise Jurídica"):
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
