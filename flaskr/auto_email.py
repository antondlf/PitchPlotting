import smtplib, ssl
from future.backports.email.mime.multipart import MIMEMultipart
from future.backports.email.mime.text import MIMEText

# Part of this code based on https://towardsdatascience.com/automate-email-with-python-1e755d9c6276
# and https://realpython.com/python-send-email/


def generate_email(stage):
    if stage == 'Session 1':
        text = MIMEText("Hello! \n\n" \
               "This is an example automated email:"
                        "Welcome to Italian Prosody Training!\n" \
               "Here you will learn how Native Italian Speakers use their intonation, and you will have a chance to compare it to yours." \
               "To get started, go to the following url..." \
               "We hope you enjoy our training!\n\n" \
               "If you run into any issues, contact ...\n\n\n" \
               "Regards \n\n\n" \
               "Antón de la Fuente and Catherine Scanlon")
        msg = MIMEMultipart()
        msg['Subject'] = 'Italian Prosody Project Part 1'
        msg.attach(text)
        return msg
    

def send_email(msg, sender, receiver):
    """Sends message object msg to some email server."""

    # initialize connection to our email server, we will use Outlook here
    with smtplib.SMTP('smtp.gmail.com', port='587') as smtp:

        smtp.ehlo()  # send the extended hello to our server
        smtp.starttls()  # tell server we want to communicate with TLS encryption

        # Password issue
        smtp.login(sender, input('Password:'))  # login to our email server

        # send our email message 'msg' to our boss
        smtp.sendmail(sender,
                      receiver,
                      msg.as_string())

def main():
    msg = generate_email('Session 1')
    send_email(msg, 'testdummyprosody@gmail.com', input('Who will receive this email?\n'))

if __name__ == '__main__':
    main()
