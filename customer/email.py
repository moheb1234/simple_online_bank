from django.core.mail import EmailMessage

from customer.models import Customer


def send_email(subject, body, to):
    email = EmailMessage(subject, body, to=[to])
    return email.send(True)


def send_verifying_code(customer: Customer):
    subject = 'verifying email'
    body = 'your verifying code is: \n' + customer.verify_code
    to = customer.email
    if send_email(subject, body, to) == 1:
        return True
    return False
