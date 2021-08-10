import smtplib, ssl
from future.backports.email.mime.multipart import MIMEMultipart
from future.backports.email.mime.text import MIMEText

# Part of this code based on https://towardsdatascience.com/automate-email-with-python-1e755d9c6276
# and https://realpython.com/python-send-email/

#def session_text(session, reminder):
def contains_non_ascii_characters(str):
    return not all(ord(c) < 128 for c in str)


def generate_email(stage, is_reminder=False, is_reminder_2=False):

    if is_reminder:
        reminder = ' reminder'
        text = "Hello!\n\n"\
                        "This is an automated email\n\n"\
                        "This is a reminder that you still have not completed" + stage + "for the Italian prosody learning course\n"\
                        "Please complete the course at your earliest convenience,"\
                        "You will receive one more reminder in case you can't complete this in the next two days.\n"\
                        "If cannot complete the rest of the study or would rather unenroll, let either of the contact emails know.\n\n"\
                        "Thank you for your contribution to our study,\n\n"\
                        "Regards,\n\n"\
                        "Antón de la Fuente and Catherine Scanlon"
    elif is_reminder_2:
        reminder = ' last reminder'
        text = "Hello!\n\n"\
                        "This is an automated email\n\n"\
                        "This is a reminder that you still have not completed " + stage + " for the Italian prosody learning course\n"\
                        "Please complete the course at your earliest convenience."\
                        "You will not receive any more reminders for this stage, but if you do not intend to finish the course please\n"\
                        "notify us at either of the contact emails.\n\n"\
                        "Thank you for your contribution to our study,\n\n"\
                         "Regards,\n\n"\
                         "Antón de la Fuente and Catherine Scanlon"
    else:
        reminder = ''
        if stage == 'Session 1':

            # TODO: get session specific urls
            url = 'prosody.delafuentealvarez.com/' + stage

            text = "Hello! \n\n" \
                   "This is an example automated email:\n"\
                    "Welcome to Italian Prosody Training.\n" \
                   "Here you will learn how Native Italian Speakers use their intonation, and you will have a chance to compare it to yours." \
                   "To get started, go to the following url: "+  url + \
                   " We hope you enjoy our training module. \n\n" \
                   "If you run into any issues, contact ...\n\n\n" \
                   "Regards \n\n\n" \
                   "Antón de la Fuente and Catherine Scanlon"

    #text = MIMEText(message)


    if (contains_non_ascii_characters(text)):
        plain_text = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    else:
        plain_text = MIMEText(text, 'plain')

    msg = MIMEMultipart()
    msg['Subject'] = 'Italian Prosody Project ' + stage + reminder
    msg.attach(plain_text)
    return msg
    

def send_email(msg, sender, receiver_list):
    """Sends message object msg to some email server."""

    # initialize connection to our email server, we will use Outlook here
    with smtplib.SMTP('smtp.gmail.com', port='587') as smtp:

        smtp.ehlo()  # send the extended hello to our server
        smtp.starttls()  # tell server we want to communicate with TLS encryption

        # TODO: solve Password issue
        smtp.login(sender, input('Password:'))  # login to our email server


        for receiver in receiver_list:
            smtp.sendmail(sender,
                          receiver,
                          msg.as_string())

def notify(session, receiver_list, is_reminder=False):

    msg = generate_email(session, is_reminder)
    send_email(msg, 'testdummyprosody@gmail.com', receiver_list)


def main():
    msg = generate_email('Session 1')
    send_email(msg, 'testdummyprosody@gmail.com', input('Who will receive this email?\n'))

if __name__ == '__main__':
    main()
