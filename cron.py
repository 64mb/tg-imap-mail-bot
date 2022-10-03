import os
from mail import *
import re


class cron:

    @staticmethod
    def check(bot, logger):
        imap_server = os.environ.get('IMAP_SERVER')
        imap_user = os.environ.get('IMAP_USER')
        imap_password = os.environ.get('IMAP_PASSWORD')

        chat_id = int(os.environ.get('TELEGRAM_CHAT_ID'))

        messages = mail.get(
            imap_server, imap_user, imap_password)

        for msg in messages:
            body = msg['body']
            if len(body) > 2048:
                body = body[:2048] + '...'

            subject = msg['subject']
            subject = subject.replace('_', '\\_').replace('*', '\\*')

            from_f = msg['from']
            from_f = from_f.replace('_', '\\_').replace('*', '\\*')

            message = '*Дата:* '+msg['date'] + '\n*От:* '+from_f + \
                '\n*Тема:* '+subject + '\n\n*Письмо:* \n'+body
            bot.send_message(chat_id, text=message, parse_mode='Markdown')
