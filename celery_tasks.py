import os
import smtplib
from celery import Celery
from sqlalchemy import select
from database import init_db, db_session
from model import Contract, Item

app = Celery('tasks', broker=f'pyamqp://guest@{os.environ.get("RABBITMQ_HOST", "localhost")}//')

@app.task
def add(x, y):
    print(x + y)


@app.task
def send_email(contract_id):
    import smtplib

    # Import the email modules we'll need
    from email.message import EmailMessage

    init_db()
    contract = db_session.execute(select(Contract).filter_by(id=contract_id)).scalar()
    item = db_session.execute(select(Item).filter_by(id=contract.item)).scalar()


    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login("sender_email_id", "sender_email_id_password")
    # message to be sent
    message = "Message_you_need_to_send"
    # sending the mail
    s.sendmail("appemail@exmple.com", "user1@example.com", message)
    s.sendmail("appemail@exmple.com", "user1@example.com", message)
    # terminating the session
    s.quit()