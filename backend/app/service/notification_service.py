from flask_mail import Message
from app.extension import mail
from app.model.user import User
import threading
from flask import current_app

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_status_update_email(user: User, status: str, start_date: str, end_date: str):
    subject = f"Leave Request Status Updated: {status}"
    
    body = (
        f"Hello {user.first_name} {user.last_name},\n\n"
        f"We would like to inform you that the status of your leave request "
        f"from {start_date} to {end_date} has been updated.\n\n"
        f"Current Status: {status}\n\n"
        f"Best regards,\n"
        f"Leave Management System"
    )
    
    sender_name = current_app.config.get('MAIL_DEFAULT_SENDER', 'notification@leave.system.pl')
    full_sender = f"Leave Management System <{sender_name}>"
    full_recipient = f"{user.first_name} {user.last_name} <{user.email}>"
    
    msg = Message(
        subject=subject, 
        recipients=[full_recipient], 
        body=body,
        sender=full_sender
    )
    
    app = current_app._get_current_object()
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()