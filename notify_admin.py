import config
from twilio.rest import Client
import smtplib
from email.message import EmailMessage

# email
def send_email(plate, image_url, record_id):
    msg = EmailMessage()
    msg['Subject'] = f"SmartGate access request: {plate}"
    msg['From'] = config.EMAIL_ADDR
    msg['To'] = config.ADMIN_EMAIL
    approve = f"{config.BACKEND_PUBLIC_URL}/public/approve.html?id={record_id}"
    deny = f"{config.BACKEND_PUBLIC_URL}/public/deny.html?id={record_id}"
    msg.set_content(f"Plate: {plate}\nApprove: {approve}\nDeny: {deny}")
    msg.add_alternative(f"<p>Plate: <b>{plate}</b></p><p><img src=\"{image_url}\" width=600></p><p><a href=\"{approve}\">Approve</a> | <a href=\"{deny}\">Deny</a></p>", subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(config.EMAIL_ADDR, config.EMAIL_PASS)
        smtp.send_message(msg)

# SMS/Whatsapp
def send_sms(plate, record_id):
    if not config.TWILIO_ACCOUNT_SID:
        return
    client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    approve = f"{config.BACKEND_PUBLIC_URL}/public/approve.html?id={record_id}"
    deny = f"{config.BACKEND_PUBLIC_URL}/public/deny.html?id={record_id}"
    body = f"SmartGate: Plate {plate}. Approve: {approve} | Deny: {deny}"
    client.messages.create(from_=config.TWILIO_FROM, to=config.ADMIN_PHONE, body=body)
