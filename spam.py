import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import json

weburl = 'http://base-de-noviercas.onrender.com'

def send_verification(name,token,mail):
    # Configuración
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_usuario = "base.noviercas@gmail.com"
    email_password = "qzzv wvbv smfo ggmf"

    # Crear el mensaje
    mensaje = MIMEMultipart()
    mensaje["Subject"] = "Verifica tu usuario"
    mensaje["From"] = email_usuario
    mensaje["To"] = mail

    html = '''\
                <meta charset="utf-8">
      <html>
      <body style="display:flex;align-items: center;align-content: center;text-align: center;font-family: sans-serif;color:black;">
        <div id='body' style="position: relative; border: solid darkcyan 2px;border-radius: 10px;padding: 10px;display: inline-block;margin: auto;box-shadow: rgba(0, 0, 0, 0.2) 0px 4px 12px;text-align:left;">
          <h1 style="color:darkcyan">Estimad@ '''+name+'''</h1>
          <hr>
          <p>Según nuestros registros, usted ha intentado iniciar sesión en su cuenta de La Base de Noviercas. Si es así, le enviamos el siguiente enlace temporal.</p>

          <a style="color:darkcyan !important" href="http://mikequez12.github.io/base-de-noviercas/account#'''+token+'''">Iniciar sesión</a>
          <p style="color: gray;font-size: 12px;">Este enlace durará aproximadamente 5 minutos, si necesita más tiempo, considere volver a intentar iniciar sesión para recibir otro enlace.</p>

          Por favor, nunca comparta este enlace. Nuestro sistema trata de ser seguro, pero como cualquier otro, tiene vulnerabilidades. Si comparte este código, contáctenos de inmediato.
<br>
          <h4>¡Gracias!</h4>

          <footer style="position: absolute;
          color:white;
        left: 0;
        bottom: 0;
        width: calc(100% - 20px);
        background: linear-gradient(to right, darkcyan, transparent);
        padding: 10px;
        border-radius: 5px;">
            Base de Noviercas
          </footer>
        </div>
      </body>
      </html>
      '''

    mensaje.attach(MIMEText(f'''\
    {html}
    ''', "html"))

    # Enviar el correo
    try:
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()
        servidor.login(email_usuario, email_password)
        servidor.sendmail(email_usuario, [mail], mensaje.as_string())
        servidor.quit()
        return "Correo enviado correctamente."
    except Exception as e:
        return f"Error al enviar el correo: {e}"


    # Contraseña de aplicación: qzzv wvbv smfo ggmf