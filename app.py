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

    # --- CUSTOM CSS INJECTION (LANDING PAGE STYLE) ---
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
                background-color: #f8f9fa;
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Header */
            .header-container {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem 0;
                margin-bottom: 2rem;
            }
            .header-logo {
                font-size: 2rem;
                margin-right: 0.5rem;
            }
            .header-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #0f172a;
            }

            /* Hero Section */
            .hero-container {
                text-align: center;
                padding: 2rem 1rem;
                max-width: 800px;
                margin: 0 auto;
            }
            .hero-title {
                font-size: 3rem;
                font-weight: 800;
                color: #0f172a;
                line-height: 1.2;
                margin-bottom: 1rem;
            }
            .hero-subtitle {
                font-size: 1.25rem;
                color: #64748b;
                font-weight: 400;
                margin-bottom: 2rem;
            }

            /* Login Box / Main Card */
            .login-container {
                background-color: white;
                padding: 3rem;
                border-radius: 24px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.08);
                max-width: 500px;
                margin: 0 auto 4rem auto;
                text-align: center;
            }
            
            /* Inputs */
            .stTextInput > div > div > input {
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 12px 16px;
                font-size: 16px;
                text-align: center;
            }
            .stTextInput > div > div > input:focus {
                border-color: #2563EB;
                box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
            }

            /* Buttons */
            .stButton > button {
                background-color: #2563EB; /* Royal Blue */
                color: white;
                border-radius: 12px;
                padding: 14px 32px;
                border: none;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
                transition: all 0.2s ease;
                font-weight: 600;
                font-size: 16px;
                width: 100%;
                margin-top: 1rem;
            }
            .stButton > button:hover {
                background-color: #1d4ed8;
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);
                color: white;
            }

            /* Features Section */
            .features-container {
                padding: 4rem 0;
                border-top: 1px solid #e2e8f0;
            }
            .feature-card {
                background: white;
                padding: 2rem;
                border-radius: 16px;
                text-align: center;
                height: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02);
                transition: transform 0.2s;
            }
            .feature-card:hover {
                transform: translateY(-5px);
            }
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                display: block;
            }
            .feature-title {
                font-weight: 700;
                font-size: 1.1rem;
                margin-bottom: 0.5rem;
                color: #0f172a;
            }
            .feature-desc {
                color: #64748b;
                font-size: 0.95rem;
                line-height: 1.5;
            }

            /* Footer */
            .footer-text {
                text-align: center;
                color: #94a3b8;
                font-size: 0.875rem;
                margin-top: 3rem;
                padding-bottom: 2rem;
            }
            
            /* Upload Area */
             [data-testid="stFileUploader"] {
                background-color: #f8f9fa;
                border: 2px dashed #cbd5e1;
                border-radius: 16px;
                padding: 30px;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. Header (Always Visible)
    st.markdown("""
        <div class="header-container">
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
                <h1 class="hero-title">Advogado de Bolso</h1>
                <p class="hero-subtitle">Não assine seu contrato de aluguel no escuro. Nossa IA encontra as pegadinhas e te protege de multas abusivas em segundos.</p>
            </div>
        """, unsafe_allow_html=True)

        # Login Area (The "Vault")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div class="login-container">
                    <p style="font-weight: 500; color: #334155; margin-bottom: 15px;">Já tem sua chave de acesso? Digite abaixo para liberar a análise.</p>
                    
    """, unsafe_allow_html=True)
            
            password = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Digite sua chave de acesso")
            
            if st.button("Entrar"):
                if password == "ALUGUEL2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Chave de acesso inválida.")
            
            st.markdown("""
                </div>
                <div style="text-align: center; margin-top: 15px;">
                    <a href="#" style="color: #64748b; text-decoration: none; font-size: 0.9rem;">Não tem acesso? Adquira sua chave aqui</a>
                </div>
            """, unsafe_allow_html=True)

        # Features Section (Below the fold)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.divider()
        
        f_col1, f_col2, f_col3 = st.columns(3)
        
        with f_col1:
            st.markdown("""
                <div class="feature-card">
                    <span class="feature-icon">🚀</span>
                    <div class="feature-title">Rápido</div>
                    <div class="feature-desc">Análise completa em menos de 30 segundos.</div>
                </div>
            """, unsafe_allow_html=True)
            
        with f_col2:
            st.markdown("""
                <div class="feature-card">
                    <span class="feature-icon">🛡️</span>
                    <div class="feature-title">Seguro</div>
                    <div class="feature-desc">Identificamos cláusulas abusivas proibidas por Lei.</div>
                </div>
            """, unsafe_allow_html=True)
            
        with f_col3:
            st.markdown("""
                <div class="feature-card">
                    <span class="feature-icon">💬</span>
                    <div class="feature-title">Negociável</div>
                    <div class="feature-desc">Geramos o texto pronto para você enviar ao proprietário.</div>
                </div>
            """, unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class="footer-text">
                © 2025 Advogado de Bolso • Tecnologia Google Gemini 3 • Seus dados são processados de forma criptografada e não são armazenados.
            </div>
        """, unsafe_allow_html=True)

    else:
        # --- APP INTERFACE (LOGGED IN) ---
        
        # Simple Welcome / Context
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: #0f172a;">Área de Análise Segura</h2>
                <p style="color: #64748b;">Faça o upload do seu contrato para iniciar.</p>
            </div>
        """, unsafe_allow_html=True)

        # Main Card Container
        with st.container():
            # Upload
            uploaded_file = st.file_uploader("Arraste seu PDF aqui", type="pdf")

            if uploaded_file is not None:
                with st.spinner("Lendo documento..."):
                    text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success(f"Documento lido com sucesso! ({len(text)} caracteres)")
                    
                    if st.button("Analisar Contrato Agora"):
                        with st.spinner("O Advogado de Bolso está analisando cada cláusula..."):
                            # 1. Análise Técnica
                            analysis = analyze_contract(text)
                            
                            st.markdown("### 📋 Resultado da Análise")
                            st.markdown(analysis)
                            
                            # 2. Gerar Mensagem de Negociação
                            st.markdown("---")
                            st.markdown("""
                                <div style="background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 20px;">
                                    <h3 style="margin-top: 0;">💬 Mensagem de Negociação</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.info("🎁 **Bônus Exclusivo:** Sabemos que confrontar o proprietário ou imobiliária pode ser desconfortável. Para você não se estressar, nosso aplicativo preparou o texto ideal — formal, educado e firme — baseado exatamente nos problemas encontrados acima. É só copiar e enviar!")
                            
                            with st.spinner("Escrevendo mensagem de negociação..."):
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
                                    st.error(f"Não foi possível gerar a mensagem de negociação: {e}")

if __name__ == "__main__":
    main()
