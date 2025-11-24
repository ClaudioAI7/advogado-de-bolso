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
    st.set_page_config(page_title="Advogado de Bolso", page_icon="⚖️")

    # 1. Login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Login - Advogado de Bolso")
        password = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar"):
            if password == "ALUGUEL2025":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return

    # 2. App Interface
    st.title("⚖️ Advogado de Bolso")
    st.subheader("Análise de Contratos de Aluguel com IA")

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
            st.info(f"Documento lido com sucesso! ({len(text)} caracteres)")
            
            if st.button("Analisar Contrato"):
                with st.spinner("O Advogado de Bolso está analisando..."):
                    # 1. Análise Técnica
                    analysis = analyze_contract(text)
                    st.markdown("---")
                    st.markdown(analysis)
                    
                    # 2. Gerar Mensagem de Negociação
                    st.markdown("---")
                    st.subheader("💬 Mensagem Pronta para Negociação")
                    st.info("🎁 **Bônus Exclusivo:** Sabemos que confrontar o proprietário ou imobiliária pode ser desconfortável. Para você não se estressar, nossa IA preparou o texto ideal — formal, educado e firme — baseado exatamente nos problemas encontrados acima. É só copiar e enviar!")
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
                            
                            st.text_area("Copie e envie:", value=negotiation_msg, height=300)
                        except Exception as e:
                            st.error(f"Não foi possível gerar a mensagem de negociação: {e}")

if __name__ == "__main__":
    main()
