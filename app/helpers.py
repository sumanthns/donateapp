from app import mail
from config import PAYMENT_GW_SALT, ADMINS
from flask import render_template
from flask_mail import Message
import hmac
import hashlib


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_thankyou_email(user, amount):
    text_body = render_template('thank_you.txt',
                                user=user.name, amount=amount)
    html_body = render_template('thank_you.html',
                                user=user.name, amount=amount)
    recipients = [user.email]
    sender = ADMINS[0]
    subject = "Donateapp, thank you for your contribution!"
    send_email(subject, sender, recipients,
               text_body, html_body)

def verify_mac(data):
    # 'd' is the dictionary that corresponds to the POST request
    # 'salt' is the key for the HMAC algorithm

    mac_provided = data.pop('mac')

    message = '|'.join(
        str(i)
        for i in zip(
            *sorted(
                data.iteritems(),
                key=lambda s: s[0].lower()
            )

        )[1]
    ) # Message that needs the MAC.

    mac_calculated = hmac.new(
        str(PAYMENT_GW_SALT),
        message,
        hashlib.sha1,
        ).hexdigest()

    if mac_provided == mac_calculated:
        return True
    return False
