import imaplib
import email
import email.message
from email.header import decode_header, make_header
import re
from markdownify import markdownify as md

imaplib._MAXLINE = 1000000


class mail:

    @staticmethod
    def get(server, user, password):
        messages = []

        imap = imaplib.IMAP4_SSL(server)

        imap.login(user, password)

        status = imap.select('INBOX')

        status, search_data = imap.search(None, '(UNSEEN)')

        if status != 'OK':
            return messages

        unseen = search_data[0].split()
        unseen = map(int, unseen)
        unseen = sorted(unseen, reverse=True)
        unseen = [str(e) for e in unseen]

        for msg_id in unseen:
            status, msg_data = imap.fetch(msg_id, '(RFC822)')
            msg_raw = msg_data[0][1]
            msg = email.message_from_bytes(
                msg_raw, _class=email.message.EmailMessage)

            timestamp = email.utils.parsedate_tz(msg['Date'])
            year, month, day, hour, minute = timestamp[:5]
            date = '{0:02}:{1:02} {2:02}.{3:02}.{4:04}'.format(
                hour, minute, day, month, year)

            body = ''

            for part in msg.walk():
                if body == '' and part.get_content_type() == "text/plain":
                    body_temp = part.get_payload(decode=True).decode('utf-8')
                    body += body_temp+'\n'
                elif body == '' and part.get_content_type() == "text/html":
                    body_temp = part.get_payload(
                        decode=True).decode('utf-8')
                    body_temp = re.sub(
                        '<style [\s\S]+?</style>', '', body_temp)
                    body_temp = md(body_temp, strip=[
                                   'tr', 'td', 'script', 'style'])
                    body += body_temp+'\n'
                else:
                    continue

            body = re.sub('[\xa0\u2003\u200c]', ' ', body)
            body = re.sub('\r\n', '\n', body)
            body = re.sub('\r', '\n', body)
            body = re.sub(' +', ' ', body)
            body = re.sub('\n +', '\n', body)
            body = re.sub('\n{2,}', '\n\n', body)
            body = re.sub('\)([А-я])', ') $1', body)
            body = re.sub('\)\*\*', ')\ns**', body)
            body = body.strip()

            messages.append({
                'date': date,
                'from': str(make_header(decode_header(msg['From']))),
                'subject': str(make_header(decode_header(msg['Subject']))),
                'body': body
            })

            imap.store(msg_id, '+FLAGS', '\\Seen')

        imap.expunge()
        imap.logout()

        return messages
