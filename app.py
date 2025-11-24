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
    st.set_page_config(page_title="Advogado de Bolso", page_icon="⚖️", layout="centered")

    # --- CUSTOM CSS INJECTION ---
    st.markdown("""
        <style>
            /* Import Google Font */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

            /* Global Settings */
            html, body, [class*="css"] {
                font-family: 'Inter', 'Helvetica Neue', sans-serif;
                color: #333;
            }

            /* Background */
            .stApp {
                background-color: #f8f9fa;
            }

            /* Main Container (The "Card" Look) */
            .block-container {
                background-color: white;
                padding: 3rem !important;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                margin-top: 2rem;
                max-width: 800px;
            }

            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Buttons */
            .stButton > button {
                background-color: #001f3f; /* Navy Blue */
                color: white;
                border-radius: 12px;
                padding: 12px 24px;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                font-weight: 600;
                font-size: 16px;
                width: 100%;
            }
            .stButton > button:hover {
                background-color: #003366;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
                transform: translateY(-2px);
                color: white;
            }

            /* Upload Area */
            [data-testid="stFileUploader"] {
                background-color: #f8f9fa;
                border: 1px dashed #ced4da;
                border-radius: 15px;
                padding: 20px;
            }
            
            /* Inputs */
            .stTextInput > div > div > input {
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 10px 15px;
            }
            
            /* Custom Header Styling */
            .custom-header h1 {
                color: #1e293b;
                font-weight: 800;
                letter-spacing: -1px;
            }
            .custom-header p {
                color: #64748b;
            }
        </style>
    """, unsafe_allow_html=True)

    # 1. Login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("""
            <div class="custom-header">
                <h1>🔐 Acesso Restrito</h1>
                <p>Digite sua credencial para acessar o Advogado de Bolso.</p>
            </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar"):
            if password == "ALUGUEL2025":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return

    # 2. App Interface (Custom Header)
    st.markdown("""
        <div class="custom-header">
            <h1>⚖️ Advogado de Bolso</h1>
            <p>Sua inteligência jurídica pessoal. Análise de contratos rápida, segura e sem juridiquês.</p>
        </div>
    """, unsafe_allow_html=True)

    # 3. Disclaimer
    disclaimer = st.checkbox("Declaro que sei que esta ferramenta NÃO substitui um advogado real.")
    
    if not disclaimer:
        st.warning("Você precisa aceitar o termo acima para continuar.")
        return

    # 4. Upload
    query_params = st.query_params
    test_mode = query_params.get("test_mode") == "true"

    if test_mode:
        st.warning("⚠️ MODO DE TESTE ATIVADO")
        file_path = st.text_input("Caminho do arquivo PDF (Teste)")
        uploaded_file = None
        if file_path and os.path.exists(file_path):
            uploaded_file = open(file_path, "rb")
    else:
        uploaded_file = st.file_uploader("Faça upload do seu contrato (PDF)", type="pdf")

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
