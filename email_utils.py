import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


SMTP_SERVER = os.getenv('SMTP_SERVER', 'localhost')
SMTP_PORT = int(os.getenv('SMTP_PORT', '25'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() in ('1', 'true', 'yes')
SMTP_FROM = os.getenv('SMTP_FROM', 'no-reply@example.com')
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Receitas App')


def send_email(subject: str, body: str, to_address: str) -> bool:
    """Send a plain-text email using smtplib. Returns True on success."""
    message = MIMEText(body, 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = formataddr((SMTP_FROM_NAME, SMTP_FROM))
    message['To'] = to_address

    try:
        if SMTP_USE_TLS:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.ehlo()
                try:
                    server.starttls()
                    server.ehlo()
                except Exception:
                    pass
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [to_address], message.as_string())
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [to_address], message.as_string())
        return True
    except Exception as exc:
        print(f"[email] Failed to send to {to_address}: {exc}")
        return False
