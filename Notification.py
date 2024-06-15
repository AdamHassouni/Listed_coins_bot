import smtplib
import ssl
from config import credentials  # Assuming you have your email credentials stored here

EMAIL_ADDRESS = 'amerbet@gmail.com'  # Replace with your email address
EMAIL_PASSWORD = 'Hurlement030198'        # Replace with your email password

def send_notification(coin, order_type):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sent_from = EMAIL_ADDRESS
    to = ['adamhassouni111@gmail.com']
    subject = f'Order Notification: {order_type} order placed for {coin}'
    body = f'An {order_type} order has been placed for {coin}. Please check your Binance account for details.'
    message = f'Subject: {subject}\n\n{body}'

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sent_from, EMAIL_ADDRESS)
            server.sendmail(sent_from, to, message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")
