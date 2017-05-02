
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# from django.conf import settings
# from django.core.exceptions import ImproperlyConfigured


def send_mail(subject, message, from_addr, to_addr, cc='', user=None, pwd=None):
    # user = user or hasattr(settings, 'DEFAULT_USER') and settings.DEFAULT_USER
    # pwd = pwd or hasattr(settings, 'DEFAULT_USER_PASSWORD') and settings.DEFAULT_USER_PASSWORD
    #
    # if not user or not pwd:
    #     raise ImproperlyConfigured('Either the user and password must be passed as arguments '
    #                                'or DEFAULT_USER and DEFAULT_USER_PASSWORD must be defined in the settings.')
    print message
    # msg = MIMEMultipart('alternative')
    # msg['Subject'] = subject
    # msg['From'] = from_addr
    # msg['To'] = to_addr
    # msg["Cc"] = cc
    # message = message.encode("utf8")
    # msg.attach(MIMEText(message, 'html'))
    #
    # s = smtplib.SMTP("smtp.gmail.com", 587)
    # s.ehlo()
    # s.starttls()
    # s.ehlo()
    # s.login(user, pwd)
    # s.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
    # s.quit()
