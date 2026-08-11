import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_gmail_service():
    creds = None

    # Token OAuth previamente obtenido
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Renovar token si ha expirado
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Primera autorización
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES
        )

        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_verification(name, token, mail):
    service = get_gmail_service()

    verification_url = (
        f"https://base-de-noviercas.onrender.com/verify/{token}"
    )

    body = f"""Hola {name}.

Verifica tu cuenta mediante este enlace:

{verification_url}

Si no has creado esta cuenta, puedes ignorar este correo.
"""

    message = MIMEText(body, "plain", "utf-8")

    message["To"] = mail
    message["Subject"] = "Verifica tu usuario"

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()

    print("Correo enviado correctamente.")
    print(result)

    return result