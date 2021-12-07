import smtplib
from email_generator import get_email_text
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# This script provides functions for automatic emailing.
# Contains email generator, server login, and notification.

# Part of this code based on https://towardsdatascience.com/automate-email-with-python-1e755d9c6276
# and https://realpython.com/python-send-email/

#def session_text(session, reminder):


# This avoids mime encoding issues
def contains_non_ascii_characters(str):
    return not all(ord(c) < 128 for c in str)


def server_login(password):
    """Login to email server"""
    smtp = smtplib.SMTP('smtp.gmail.com', port='587')
    smtp.ehlo()  # send the extended hello to our server
    smtp.starttls()  # tell server we want to communicate with TLS encryption

    if password:
        smtp.login('italianprosody.reminders@gmail.com', password)
    else:
        smtp.login('italianprosody.reminders@gmail.com', input('Password:'))
    print('Logged in successfully')

    return smtp


def server_logout(server):
    """Logout from server"""
    server.quit()


def generate_email(stage, username=None, password=None, is_reminder=False):
    """generate email reminder for a given session and mime encode it."""

    subject, text = get_email_text(stage, username, is_reminder=is_reminder)

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


def notify(session, receiver_list, server=None, username=None, is_reminder=False):
    """This function sends the email notifications."""

    if server:
        print(is_reminder)
        msg = generate_email(session, username=username, is_reminder=is_reminder)
        send_email(msg, server, 'italianprosody.reminders@gmail.com', receiver_list)

    else:
        # initialize connection to our email server, we will use Outlook here
        with smtplib.SMTP('smtp.gmail.com', port='587') as smtp:

            smtp.ehlo()  # send the extended hello to our server
            smtp.starttls()  # tell server we want to communicate with TLS encryption

            # TODO: solve Password issue
            smtp.login('italianprosody.reminders@gmail.com', input('Password:'))  # login to our email server

            msg = generate_email(session, username=username, is_reminder=is_reminder)
            send_email(msg, smtp, 'italianprosody.reminders@gmail.com', receiver_list)


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
