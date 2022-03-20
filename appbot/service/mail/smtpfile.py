import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from appbot.docs.conf import from_email, password

async def send_message_to_email(to_email, message):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    msg = MIMEMultipart()
    msg.attach(MIMEText(message, 'plain'))
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

