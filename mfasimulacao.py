import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.markdown(
    "<h1 style='text-align: center; color: navy;'>Simulação de Autenticação Multifator</h1>",
    unsafe_allow_html=True,
)

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}  

if "estado" not in st.session_state:
    st.session_state.estado = "CRIAR_CONTA"  # criação de conta

if "codigo_mfa" not in st.session_state:
    st.session_state.codigo_mfa = None

if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None


                                        # enviar e-mail com o código MFA
def enviar_email_codigo(email, codigo):
    remetente = "mfacodigo@gmail.com"
    senha_remetente = "ilre jrto xudf opxf"
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remetente, senha_remetente)

        mensagem = MIMEMultipart()
        mensagem["From"] = remetente
        mensagem["To"] = email
        mensagem["Subject"] = "Seu Código MFA"

        corpo = f"Seu código de autenticação é: {codigo}"
        mensagem.attach(MIMEText(corpo, "plain"))

        servidor.sendmail(remetente, email, mensagem.as_string())
        servidor.quit()
        st.success(f"Código MFA enviado para: {email}")
    except Exception as e:
        st.error(f"Erro ao enviar código MFA: {str(e)}")


                                                                   # botões
if st.session_state.estado in ["CRIAR_CONTA", "INSERIR_CREDENCIAIS"]:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Criar Conta", key="botao_criar_tela"):
            st.session_state.estado = "CRIAR_CONTA"
    with col2:
        if st.button("Já tenho uma conta", key="botao_login_tela"):
            st.session_state.estado = "INSERIR_CREDENCIAIS"

                                                                   # tela conta
if st.session_state.estado == "CRIAR_CONTA":
    st.title("Criar Conta")
    nome_usuario = st.text_input("Nome do Usuário", key="criar_usuario")
    senha = st.text_input("Senha", type="password", key="criar_senha")
    email = st.text_input("E-mail", key="criar_email")
    if st.button("Criar", key="botao_criar_conta"):
        if nome_usuario in st.session_state.usuarios:
            st.error("Nome de usuário já existe. Escolha outro.")
        elif not nome_usuario or not senha or not email:
            st.error("Todos os campos são obrigatórios!")
        else:
                                                                  # armazenar usuário
            st.session_state.usuarios[nome_usuario] = {
                "senha": senha,
                "email": email,
                "tentativas": 0,
                "bloqueado": False,
            }
            st.success("Conta criada com sucesso! Agora faça login.")
            st.session_state.estado = "INSERIR_CREDENCIAIS"

                                                                   # tela de login
if st.session_state.estado == "INSERIR_CREDENCIAIS":
    st.title("Login")
    usuario = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Autenticar", key="botao_autenticar"):
        if usuario in st.session_state.usuarios:
            user_data = st.session_state.usuarios[usuario]
            if user_data["bloqueado"]:
                st.error("Conta bloqueada devido a múltiplas tentativas falhas.")
            elif user_data["senha"] == senha:
                st.session_state.codigo_mfa = random.randint(100000, 999999)
                enviar_email_codigo(user_data["email"], st.session_state.codigo_mfa)
                st.session_state.usuario_atual = usuario
                st.session_state.estado = "INSERIR_CODIGO_MFA"
                user_data["tentativas"] = 0  
            else:
                user_data["tentativas"] += 1
                if user_data["tentativas"] >= 3:
                    user_data["bloqueado"] = True
                    st.error("Conta bloqueada devido a múltiplas tentativas falhas.")
                else:
                    st.error(
                        f"Senha incorreta. Tentativas restantes: {3 - user_data['tentativas']}"
                    )
        else:
            st.error("Usuário não encontrado.")

                                                                          # tela código MFA
if st.session_state.estado == "INSERIR_CODIGO_MFA":
    st.title("Verificação MFA")
    codigo_inserido = st.text_input("Insira o código enviado ao seu e-mail", type="password", key="codigo_mfa_input")
    if st.button("Verificar Código", key="botao_verificar_codigo"):
        if str(st.session_state.codigo_mfa) == codigo_inserido:
            st.success(f"Autenticação bem-sucedida! Bem-vindo, {st.session_state.usuario_atual}!")
            st.balloons()  
            st.session_state.estado = "SUCESSO"
        else:
            st.error("Código MFA inválido. Tente novamente.")


if st.session_state.estado == "SUCESSO":
    st.title("Bem-vindo!")
    st.write(f"Você está autenticado como {st.session_state.usuario_atual}.")

                                                            # logout
if st.button("Logout", key="botao_logout"):
    st.session_state.estado = "CRIAR_CONTA"
    st.session_state.pop("usuario_atual", None)
