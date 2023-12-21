from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP
import os


class NoEnvironmentVariableError(Exception):
    pass


def send_email(from_: str, to: str, subject: str, body: str) -> None:
    """メール送信

    Args:
        from_ (str): 送信元メールアドレス
        to (str): 送信先メールアドレス
        subject (str): 件名
        body (str): 本文
    """
    mail_host = os.environ.get("MAIL_HOST")
    mail_port = os.environ.get("MAIL_PORT")
    mail_password = os.environ.get("MAIL_PASSWORD")
    if not mail_host or not mail_port or not mail_password:
        raise NoEnvironmentVariableError(
            "環境変数が設定されていません。.envファイルにMAIL_HOST, MAIL_PORT, MAIL_PASSWORDを設定してください。"
        )
    connection = SMTP("smtp.gmail.com", mail_port)
    connection.set_debuglevel(True)
    connection.starttls()
    connection.login(from_, mail_password)
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = from_
    msg["To"] = to
    connection.sendmail(from_, [to], msg.as_string())
    connection.quit()
