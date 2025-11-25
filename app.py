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

    # --- CUSTOM CSS INJECTION (PREMIUM SAAS STYLE) ---
    st.markdown("""
        <style>
            /* Import Google Font */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            /* Global Settings */
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
                color: #1e293b;
            }

            /* Background */
            .stApp {
                background: linear-gradient(180deg, #f0f4f8 0%, #ffffff 100%);
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Hero Section */
            .hero-container {
                text-align: center;
                padding: 4rem 1rem 2rem 1rem;
                max-width: 900px;
                margin: 0 auto;
            }
            .hero-emoji {
                font-size: 4rem;
                margin-bottom: 1rem;
                display: block;
            }
            .hero-title {
                font-size: 3.5rem;
                font-weight: 800;
                color: #0f172a;
                line-height: 1.1;
                margin-bottom: 1rem;
                letter-spacing: -0.02em;
            }
            .hero-subtitle {
                font-size: 1.25rem;
                color: #64748b;
                font-weight: 400;
                margin-bottom: 3rem;
                line-height: 1.6;
            }

            /* Login Card */
            .login-card {
                background-color: white;
                padding: 2.5rem;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.08);
                text-align: center;
                border: 1px solid #e2e8f0;
            }
            .login-header {
                font-weight: 600;
                color: #334155;
                margin-bottom: 1.5rem;
                font-size: 1.1rem;
            }

            /* Inputs */
            .stTextInput > div > div > input {
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                padding: 12px 16px;
                font-size: 16px;
                color: #334155;
            }
            .stTextInput > div > div > input:focus {
                border-color: #0e1117;
                box-shadow: 0 0 0 2px rgba(14, 17, 23, 0.1);
            }

            /* Buttons */
            .stButton > button {
                background-color: #0e1117; /* Navy/Black */
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
                font-weight: 600;
                font-size: 16px;
                width: 100%;
                margin-top: 0.5rem;
            }
            .stButton > button:hover {
                background-color: #1a1f2b;
                transform: translateY(-1px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
                color: white;
            }

            /* Features Section */
            .features-section {
                margin-top: 4rem;
                padding-top: 2rem;
                border-top: 1px solid #e2e8f0;
            }
            .feature-item {
                text-align: center;
                padding: 1rem;
            }
            .feature-icon {
                font-size: 2rem;
                margin-bottom: 0.5rem;
                display: block;
            }
            .feature-title {
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.25rem;
            }
            .feature-text {
                color: #64748b;
                font-size: 0.9rem;
            }

            /* Footer */
            .footer-text {
                text-align: center;
                color: #94a3b8;
                font-size: 0.8rem;
                margin-top: 4rem;
                padding-bottom: 2rem;
            }
            
            /* Upload Area (Logged In) */
             [data-testid="stFileUploader"] {
                background-color: white;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02);
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
                <span class="hero-emoji">⚖️</span>
                <h1 class="hero-title">Advogado de Bolso</h1>
                <h2 class="hero-subtitle">A inteligência artificial que blinda seu contrato de aluguel contra multas e cláusulas abusivas.</h2>
            </div>
        """, unsafe_allow_html=True)

        # Login Area (Card)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="login-card"><div class="login-header">Área Restrita. Digite sua chave de acesso:</div>', unsafe_allow_html=True)
            
            password = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Sua chave de acesso")
            
            if st.button("Entrar"):
                if password == "ALUGUEL2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Chave inválida.")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Features Section
        st.markdown('<div class="features-section"></div>', unsafe_allow_html=True)
        
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("""
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    <div class="feature-title">Análise em 30s</div>
                    <div class="feature-text">Sem esperar dias por um advogado.</div>
                </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
                <div class="feature-item">
                    <span class="feature-icon">🛡️</span>
                    <div class="feature-title">Proteção Legal</div>
                    <div class="feature-text">Identifica o que a Lei do Inquilinato proíbe.</div>
                </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
                <div class="feature-item">
                    <span class="feature-icon">🎁</span>
                    <div class="feature-title">Kit Negociação</div>
                    <div class="feature-text">Receba a ferramenta exclusiva para convencer o proprietário.</div>
                </div>
            """, unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class="footer-text">
                © 2025 • Tecnologia Jurídica Avançada
            </div>
        """, unsafe_allow_html=True)

    else:
        # --- APP INTERFACE (LOGGED IN) ---
        
        # Header for App
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h1 style="font-size: 2rem; font-weight: 800; color: #0f172a;">Advogado de Bolso <span style="color: #64748b; font-weight: 400;">| Análise</span></h1>
            </div>
        """, unsafe_allow_html=True)

        # Main Content
        with st.container():
            uploaded_file = st.file_uploader("Faça upload do seu contrato (PDF)", type="pdf")

            if uploaded_file is not None:
                with st.spinner("Lendo documento..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success(f"Documento lido com sucesso! ({len(text)} caracteres)")
                    
                    if st.button("Analisar Contrato Agora"):
                        with st.spinner("Analisando cláusulas..."):
                            # 1. Análise Técnica
                            analysis = analyze_contract(text)
                            
                            st.markdown("### 📋 Resultado da Análise")
                            st.markdown(analysis)
                            
                            # 2. Gerar Mensagem de Negociação
                            st.markdown("---")
                            st.markdown("### 🎁 Bônus: Kit de Negociação")
                            st.info("Use o texto abaixo para negociar com o proprietário.")
                            
                            with st.spinner("Gerando mensagem..."):
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
                                    
                                    st.text_area("Copie o texto abaixo:", value=negotiation_msg, height=300)
                                except Exception as e:
                                    st.error(f"Erro ao gerar mensagem: {e}")

if __name__ == "__main__":
    main()
