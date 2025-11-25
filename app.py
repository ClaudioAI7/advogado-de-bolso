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

    # --- LUXURY FRONTEND CSS INJECTION ---
    st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

            /* Global Reset & Settings */
            html, body, [class*="css"] {
                font-family: 'Montserrat', sans-serif;
                color: #e2e8f0;
                background-color: #0b1120; /* Deep Navy Blue */
            }
            
            h1, h2, h3 {
                font-family: 'Playfair Display', serif;
            }

            /* Background Animation - Subtle Gradient Pulse */
            .stApp {
                background: linear-gradient(-45deg, #0b1120, #1a2332, #0f172a, #0b1120);
                background-size: 400% 400%;
                animation: gradientBG 15s ease infinite;
            }
            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* --- HERO SECTION (HTML INJECTION) --- */
            .hero-wrapper {
                text-align: center;
                padding: 15vh 1rem 2rem 1rem;
                max-width: 1000px;
                margin: 0 auto;
                animation: fadeIn 1.5s ease-out;
            }
            .hero-logo {
                font-size: 4rem;
                display: block;
                margin-bottom: 1rem;
                color: #c5a059;
                text-shadow: 0 0 20px rgba(197, 160, 89, 0.3);
            }
            .hero-title {
                font-family: 'Playfair Display', serif;
                font-size: 4rem;
                font-weight: 400;
                color: #ffffff;
                margin-bottom: 1rem;
                letter-spacing: 1px;
            }
            .hero-subtitle {
                font-family: 'Montserrat', sans-serif;
                font-size: 1.1rem;
                color: #c5a059; /* Gold */
                text-transform: uppercase;
                letter-spacing: 4px;
                margin-bottom: 4rem;
                font-weight: 500;
                border-top: 1px solid rgba(197, 160, 89, 0.3);
                border-bottom: 1px solid rgba(197, 160, 89, 0.3);
                display: inline-block;
                padding: 10px 20px;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            /* --- LOGIN CARD (GLASSMORPHISM) --- */
            .login-card-wrapper {
                background: rgba(11, 17, 32, 0.7);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(197, 160, 89, 0.3); /* Gold Border */
                padding: 3rem;
                border-radius: 2px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                max-width: 400px;
                margin: 0 auto;
                text-align: center;
            }
            
            /* --- WIDGET STYLING (MASKING STREAMLIT) --- */
            
            /* Inputs */
            .stTextInput > div > div > input {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 0;
                padding: 15px;
                font-size: 16px;
                color: #ffffff;
                text-align: center;
                font-family: 'Montserrat', sans-serif;
                transition: all 0.3s ease;
            }
            .stTextInput > div > div > input:focus {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: #c5a059; /* Gold Focus */
                box-shadow: 0 0 15px rgba(197, 160, 89, 0.2);
            }
            .stTextInput > div > div > input::placeholder {
                color: #64748b;
                letter-spacing: 1px;
            }

            /* Buttons */
            .stButton > button {
                background: linear-gradient(45deg, #c5a059, #d4af37);
                color: #0b1120;
                border-radius: 0px;
                padding: 16px 40px;
                border: none;
                font-family: 'Montserrat', sans-serif;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 600;
                font-size: 14px;
                width: 100%;
                margin-top: 1rem;
                transition: all 0.4s ease;
                box-shadow: 0 4px 15px rgba(197, 160, 89, 0.3);
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(197, 160, 89, 0.5);
                letter-spacing: 3px;
                color: #ffffff;
            }

            /* Footer */
            .custom-footer {
                text-align: center;
                color: #475569;
                font-size: 0.7rem;
                margin-top: 6rem;
                font-family: 'Montserrat', sans-serif;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            
            /* --- APP INTERFACE (LOGGED IN) --- */
            .app-header {
                text-align: center;
                margin-bottom: 3rem;
                padding-top: 2rem;
                border-bottom: 1px solid rgba(197, 160, 89, 0.2);
                padding-bottom: 2rem;
            }
            
            /* Upload Area */
             [data-testid="stFileUploader"] {
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px dashed rgba(197, 160, 89, 0.3);
                border-radius: 0px;
                padding: 50px;
                text-align: center;
                transition: border-color 0.3s;
            }
            [data-testid="stFileUploader"]:hover {
                border-color: #c5a059;
            }
            [data-testid="stFileUploader"] div {
                color: #94a3b8;
            }
            
            /* Analysis Text Box */
            .analysis-box {
                background-color: rgba(11, 17, 32, 0.8);
                border-left: 3px solid #c5a059;
                padding: 2rem;
                margin-top: 1rem;
                font-weight: 300;
                line-height: 1.8;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. Session State Logic
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # 2. View Controller
    if not st.session_state.logged_in:
        # --- LANDING PAGE VIEW ---
        
        # Hero HTML Injection
        st.markdown("""
            <div class="hero-wrapper">
                <span class="hero-logo">⚖️</span>
                <h1 class="hero-title">Advogado de Bolso</h1>
                <div class="hero-subtitle">Private Legal Intelligence</div>
            </div>
        """, unsafe_allow_html=True)

        # Login Area (Wrapped in Columns for Centering)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="login-card-wrapper">', unsafe_allow_html=True)
            
            # Streamlit Widgets (Styled by CSS above)
            password = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="ACCESS KEY")
            
            if st.button("ENTER SYSTEM"):
                if password == "ALUGUEL2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Access Denied.")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class="custom-footer">
                © 2025 Advogado de Bolso • Exclusive Member Access Only
            </div>
        """, unsafe_allow_html=True)

    else:
        # --- APP INTERFACE (LOGGED IN) ---
        
        st.markdown("""
            <div class="app-header">
                <h2 style="font-family: 'Playfair Display', serif; color: #ffffff; font-size: 2.5rem; margin: 0;">Client Portal</h2>
                <p style="color: #c5a059; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; margin-top: 0.5rem;">Contract Analysis Suite</p>
            </div>
        """, unsafe_allow_html=True)

        # Main Content
        with st.container():
            uploaded_file = st.file_uploader("Upload Document (PDF)", type="pdf")

            if uploaded_file is not None:
                with st.spinner("Analyzing Document Structure..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success(f"Document Loaded Successfully. ({len(text)} chars)")
                    
                    if st.button("EXECUTE LEGAL AUDIT"):
                        with st.spinner("Processing Legal Analysis..."):
                            # 1. Análise Técnica
                            analysis = analyze_contract(text)
                            
                            st.markdown("### Technical Opinion")
                            st.markdown(f'<div class="analysis-box">{analysis}</div>', unsafe_allow_html=True)
                            
                            # 2. Gerar Mensagem de Negociação
                            st.markdown("---")
                            st.markdown("### Negotiation Draft")
                            st.info("Formal communication draft generated below.")
                            
                            with st.spinner("Drafting Correspondence..."):
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
                                    
                                    st.text_area("Copy Text:", value=negotiation_msg, height=300)
                                except Exception as e:
                                    st.error(f"Error generating draft: {e}")

if __name__ == "__main__":
    main()
