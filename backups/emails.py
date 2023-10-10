import os
import ssl
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


class Mailer:
    def __init__(self, my_email="", my_password="", smtp_server="", port=465):
        self.my_email = my_email
        self.my_password = my_password

        self.smtp_server = smtp_server
        self.port = port

        # connect and login
        self.context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(self.smtp_server, self.port, context=self.context)
        self.server.login(self.my_email, self.my_password)

    def __add_attachments(self, message: MIMEMultipart, attachments: str | list):
        # if attachments is not a list, convert it to a list
        if isinstance(attachments, str):
            attachments = [attachments]

        # add each attachment to the email message
        for attachment_path in attachments:
            if len(attachment_path) > 0:
                attachment = open(attachment_path, "rb")

                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

                encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {str(os.path.basename(attachment_path))}",
                )

                message.attach(part)
        return message

    def sendPlainTextEmail(self, to_email: str | list, subject: str, content: str, attachments: str | list = ""):
        """
        Method to send an email with plain text content, and optional attachments.
        :param to_email: recipient's email (single email as a string, or multiple emails as a list)
        :param subject: email subject
        :param content: the plain text content of the email (not html)
        :param attachments: a single attachment file path as a string, or multiple file paths as a list
        :return:
        """
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = self.my_email
        # message["To"] = to_email

        message.attach(MIMEText(content, "plain"))

        message = self.__add_attachments(message, attachments)

        self.server.sendmail(self.my_email, to_email, message.as_string())


    def sendHtmlEmail(self, to_email: str | list, subject: str, html_content: str, attachments: str | list = ""):
        """
        Method to send an email with html content, and optional attachments.
        :param to_email: recipient's email (single email as a string, or multiple emails as a list)
        :param subject: email subject
        :param html_content: the html content of the email
        :param attachments: a single attachment file path as a string, or multiple file paths as a list
        :return:
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.my_email
        # message["To"] = to_email

        message.attach(MIMEText(html_content, "html"))

        message = self.__add_attachments(message, attachments)

        self.server.sendmail(self.my_email, to_email, message.as_string())


    def close_connection(self):
        self.server.quit()


if __name__ == '__main__':

    # mailMan = Mailer(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST, EMAIL_PORT)
    # mailMan.sendPlainTextEmail(to_email="mushunjek@gmail.com", subject="Test Email", content="This is a test email")
    # mailMan.close_connection()
    import os
    import django
    from django.core.mail import send_mail

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SoftriteAPI.settings")
    django.setup()

    send_mail(
        'Test Subject',
        'This should fail',
        os.environ.get('SMTP_USERNAME'),  # From email address
        ['mushunjek@gmail.com'],  # List of recipient email addresses
        fail_silently=False,
    )

