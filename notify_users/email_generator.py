

def get_email_text(stage, username, password, is_reminder=False):

    url = 'prosody.delafuentealvarez.com/{}'.format(stage)

    if stage == 'Session_1':

        subject = 'Italian Prosody Study Part 1{}'

        message = "Ciao!\n\n"\
                "Thanks for signing up for our study!" \
                " You’ll try out a web app for Italian intonation practice." \
                " The study has three sessions, one week apart. " \
                "The first two are training sessions that should take" \
                " about half an hour, and the last one is a follow up that" \
                " should take 15 minutes or less. Completing each session" \
                " gets you an entry in our drawing, plus an additional entry" \
                " for completing the whole study.\n\n"\
                "To start the first session, click on the ling below. Sign in as follows:\n\n"\
                "username: {}\n"\
                "password: {}\n"\
                "url: {}\n\n"\
                "We hope you enjoy!" \
                " If you run into any issues," \
                " contact Antón de la Fuente at antondlf@mac.com\n\n"\
                "Grazie mille!\n"\
                "Catherine Scanlon and Antón de la Fuente".format(username, password, url)

        reminder = "Hi again!\n\n"\
                "Just checking in to see if you’re" \
                    " still interested in participating" \
                    " in our study and practicing your Italian intonation."\
                "To start the first session, click on the link below and sign in with the credentials we provided in the first email"\
                "url: {}\n\n" \
                    " The study has three sessions, one week apart. " \
                    "The first two are training sessions that should take" \
                    " about half an hour, and the last one is a follow up that" \
                    " should take 15 minutes or less. Completing each session" \
                    " gets you an entry in our drawing, plus an additional entry" \
                    " for completing the whole study.\n\n" \
                    "We hope you enjoy!" \
                " If you run into any issues," \
                " contact Antón de la Fuente at antondlf@mac.com\n\n"\
                "Grazie mille!\n"\
                "Catherine Scanlon and Antón de la Fuente".format(url)

    elif stage == "Session_2":
        subject = 'Italian Prosody Study Part 2{}'
        message = "Ciao!\n\n"\
                    "Time for another Italian prosody session!" \
                  " Please complete Session 2 within the next day." \
                  " It’s very similar to Session 1 and should take no " \
                  "more than 30 minutes. Please sign in with the username" \
                  "and password from the last email at this link: {}\n\n"\
            "Have fun!" \
                " If you run into any issues," \
                " contact Antón de la Fuente at antondlf@mac.com\n\n"\
                "Grazie mille!\n"\
                "Catherine Scanlon and Antón de la Fuente".format(url)

        reminder = "Hi!\n\n" \
                   "Just a reminder about Session 2 of the Italian prosody study," \
                   " which should take no more than 30 minutes." \
                   " Please complete it today if you can, by clicking the following link" \
                   "and signing in with the username and password provided to you" \
                   "in the introductory email\n\nSession 2 link: {}" \
                   "\n\nEnjoy!" \
                " If you run into any issues," \
                " contact Antón de la Fuente at antondlf@mac.com\n\n"\
                "Grazie mille!\n"\
                "Catherine Scanlon and Antón de la Fuente".format(url)

    elif stage == "Session_3":

        subject = 'Italian Prosody Study Final Followup{}'

        message = "Ciao!\n\n"\
                    "Time for the final session" \
                  " of the Italian prosody study." \
                  " This is a short follow-up that should " \
                  "take no more than 15 minutes." \
                  " Please sign in with the username" \
                  "and password from the first email at this link: {}\n\n"\
                " If you run into any issues," \
                " contact Antón de la Fuente at antondlf@mac.com\n\n" \
                  "Thanks for your participation!" \
                  " The drawing will take place by" \
                  " the end of the year, after data " \
                  "collection is complete. The winner will" \
                  " be notified by email.\n\n"\
                "Grazie mille!\n"\
                "Catherine Scanlon and Antón de la Fuente".format(url)

        reminder = "Ciao!\n\n"\
                    "Just a reminder about the final sesion" \
                   " of the Italian prosody study, which" \
                   " should take no more than 15 minutes." \
                   " Please complete it today if you can." \
                  " Please sign in with the username" \
                  "and password from the first email at this link: {}\n\n"\
                " If you run into any issues," \
                " contact Antón de la Fuente at antondlf@mac.com\n\n" \
                  "Thanks for your participation!" \
                  " The drawing will take place by" \
                  " the end of the year, after data " \
                  "collection is complete. The winner will" \
                  " be notified by email.\n\n"\
                "Grazie mille!\n"\
                "Catherine Scanlon and Antón de la Fuente".format(url)

    if is_reminder:
        return subject.format(' reminder'), reminder

    else:
        return subject.format(''), message

