import re
from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto


def plain_handler(bot, update, logger):
    logger.info(
        {'msg': 'message from chat: ' + str(update.message.chat_id), 'chat_id': update.message.chat_id})

    return
