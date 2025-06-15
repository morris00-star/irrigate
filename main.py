'''from mailersend import emails
mailer = emails.NewEmail("mlsn.a11059ca06e6a901783c1edd40b89e7652036735406960d58f712b25112a50bb")
print(mailer.test_api())  # Should return "PONG!"'''

import mailersend

mailer = mailersend.NewApiClient()

subject = "Subject"
text = "Greetings from the team, you got this message through MailerSend."
html = "Greetings from the team, you got this message through MailerSend."

my_mail = "nduwayomorris@gmail.com"
subscriber_list = ['nduwayomorris@gmail.com']

mailer.send(my_mail, subscriber_list, subject, html, text)

