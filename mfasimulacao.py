import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


credenciais = {"usuario": "admin", "senha": "1234"}
tentativas_max = 3
tentativas = st.session_state.get('tentativas', 0)
codigo_mfa = st.session_state.get('codigo_mfa', None)
email_usuario = "larymarquesp@gmail.com"


                                                # enviar e-mail com o código MFA
def enviar_email_codigo(email, codigo):
    remetente = "mfacodigo@gmail.com"
    senha_remetente = ""
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


st.title("Sistema de Autenticação Multifator")


if "estado" not in st.session_state:
    st.session_state.estado = "INSERIR_CREDENCIAIS"


if st.session_state.estado == "INSERIR_CREDENCIAIS":
    st.subheader("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Autenticar"):
        if usuario == credenciais["usuario"] and senha == credenciais["senha"]:
            st.session_state.codigo_mfa = random.randint(100000, 999999)
            enviar_email_codigo(email_usuario, st.session_state.codigo_mfa)
            st.session_state.estado = "INSERIR_CODIGO_MFA"
        else:
            tentativas += 1
            st.session_state.tentativas = tentativas
            if tentativas >= tentativas_max:
                st.session_state.estado = "BLOQUEADO"
            else:
                st.error(f"Credenciais inválidas. Tentativas restantes: {tentativas_max - tentativas}")

if st.session_state.estado == "INSERIR_CODIGO_MFA":
    st.subheader("Verificação MFA")
    codigo_inserido = st.text_input("Insira o código enviado ao seu e-mail", type="password")
    if st.button("Verificar Código"):
        if str(st.session_state.codigo_mfa) == codigo_inserido:
            st.success("Autenticação bem-sucedida! Bem-vindo!")
            st.session_state.estado = "SUCESSO"
        else:
            st.error("Código MFA inválido. Tente novamente.")


if st.session_state.estado == "BLOQUEADO":
    st.error("Conta bloqueada devido a múltiplas tentativas falhas. Tente novamente mais tarde.")


if st.session_state.estado == "SUCESSO":
    st.balloons()
    st.write("Você está autenticado!")
