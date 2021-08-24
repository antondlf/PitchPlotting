import smtplib
from notify_users.email_generator import get_email_text
from future.backports.email.mime.multipart import MIMEMultipart
from future.backports.email.mime.text import MIMEText

# Part of this code based on https://towardsdatascience.com/automate-email-with-python-1e755d9c6276
# and https://realpython.com/python-send-email/

#def session_text(session, reminder):
def contains_non_ascii_characters(str):
    return not all(ord(c) < 128 for c in str)


def generate_email(stage, username=None, password=None, is_reminder=False):

    subject, text = get_email_text(stage, username, password, is_reminder=is_reminder)



    if (contains_non_ascii_characters(text)):
        plain_text = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    else:
        plain_text = MIMEText(text, 'plain')

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg.attach(plain_text)

    return msg
    

def send_email(msg, server, sender, receiver_list):
    """Sends message object msg to some email server."""

    if type(receiver_list) == list:
        for receiver in receiver_list:
            server.sendmail(sender,
                          receiver,
                          msg.as_string())
    elif type(receiver_list) == str:
        server.sendmail(sender,
                      receiver_list,
                      msg.as_string())

    else:
        print('Error: email supplied is invalid.')


def notify(session, receiver_list, username=None, password=None, is_reminder=False):

    # initialize connection to our email server, we will use Outlook here
    with smtplib.SMTP('smtp.gmail.com', port='587') as smtp:

        smtp.ehlo()  # send the extended hello to our server
        smtp.starttls()  # tell server we want to communicate with TLS encryption

        # TODO: solve Password issue
        smtp.login('testdummyprosody@gmail.com', input('Password:'))  # login to our email server

        msg = generate_email(session, username=username, password=password, is_reminder=is_reminder)
        send_email(msg, smtp, 'testdummyprosody@gmail.com', receiver_list)


# def main():
#
#     with smtplib.SMTP('smtp.gmail.com', port='587') as smtp:
#
#         smtp.ehlo()  # send the extended hello to our server
#         smtp.starttls()  # tell server we want to communicate with TLS encryption
#
#         # TODO: solve Password issue
#         smtp.login('testdummyprosody@gmail.com', input('Password:'))  # login to our email server
#         receiver = input('Who will receive this email?\n')
#         for sesh in ['Session_1', 'Session_2', 'Session_3']:
#             for remind in [True, False]:
#                 msg = generate_email(sesh, is_reminder=remind, username="test", password="Testpassword")
#                 smtp.sendmail('testdummyprosody@gmail.com',
#                               receiver,
#                               msg.as_string())
                #send_email(msg, 'testdummyprosody@gmail.com', receiver)

# if __name__ == '__main__':
#     main()
