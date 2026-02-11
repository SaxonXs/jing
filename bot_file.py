import os

import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time
from dotenv import load_dotenv
import avito_auth
import avito_handler


load_dotenv() #loading env file with auth credentials
#telegram keys
token = os.getenv("TG_TOKEN")
send_text = 'https://api.telegram.org/bot' + token + '/getUpdates'
bot_name = os.getenv("BOT_NAME")
#avito keys
avito_id = os.getenv("AVITO_ID") #идентификатор пользователя чаты которого надо собрать
client_id = os.getenv("AVITO_CLIENT_ID")
client_secret = os.getenv("AVITO_CLIENT_SECRET")


#avito chat link. Need chat id after url
chat_url = 'https://www.avito.ru/profile/messenger/channel/'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello!')

async def new_message_screening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = 0
    avito_token = []
    token_type = []
    messages = []
    while status == 0:
        if len(avito_token) == 0 and len(token_type) == 0:
            print('asking for a new token')
            new_avito_token, new_token_type = avito_auth.get_auth_token(client_id,
                                                                client_secret)  # requesting auth token for avito
            avito_token.append(new_avito_token)
            token_type.append(new_token_type)

            status_code, response = avito_handler.check_unread_message(avito_id, avito_token[0], token_type[0])
            if status_code == 200 and len(response.json()['chats']) > 0:
                message_count, chat_id, title, writer, text, message_id = avito_handler.retrieve_message_data(response)

                if message_id not in messages:
                    messages.append(message_id)
                    try:
                        await update.message.reply_text(
                            'Получено ' + message_count + ' новое сообщение от ' + writer + ' для объявления '
                            + title + '! Ссылка на чат: https://www.avito.ru/profile/messenger/channel/'
                            + chat_id) # + '/n Текст сообщения: ' + text)
                        time.sleep(2)
                        pass
                    except:
                        print(str(datetime.datetime.now()) + ' Error with Telegram API occured. retrying loop')
                        pass
                else:
                    print(str(datetime.datetime.now()) + ' new messages not found. Awaiting 1 minute.')
                    pass
        else:
            status_code, response = avito_handler.check_unread_message(avito_id, avito_token[0], token_type[0])
            if status_code == 200 and len(response.json()['chats']) > 0:
                message_count, chat_id, title, writer = avito_handler.retrieve_message_data(response)

                if message_id not in messages:
                    messages.append(message_id)
                    try:
                        await update.message.reply_text('Получено ' + message_count + ' новое сообщение от '+ writer + ' для объявления '
                                                + title + '! Ссылка на чат: https://www.avito.ru/profile/messenger/channel/'
                                                + chat_id) #+ ' /n Текст сообщения: ' + text)
                        pass
                    except:
                        print(str(datetime.datetime.now()) + ' Error with Telegram API occured. retrying loop')
                        pass
                else:
                    pass
            elif status_code == 403:
                print('Токен просрочился, запрашиваю новый')
                del avito_token[0]
                del token_type[0]
                pass
            elif status_code not in (200, 403):
                await update.message.reply_text('Получена ошибка от авито с текстом' + response['result']['message'])
                time.sleep(60000)
                pass
            else:
                print(str(datetime.datetime.now()) + ' messages not found. Awaiting 1 minute.')
                pass
        if len(messages) > 100:
            messages.clear()
            print('Cleared message history at ' + str(datetime.datetime.now()))
        else:
            pass
        time.sleep(60)


# Creating the app itself
if __name__ == '__main__':
    print('Manu is starting...')

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('new_message_screening', new_message_screening))


    print('Polling...')
    app.run_polling(poll_interval=3)