import requests
import json
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import time
from paho.mqtt import subscribe

TOKEN: Final = ''
send_text = 'https://api.telegram.org/bot' + TOKEN + '/getUpdates'
BOT_NAME: Final = '@manu_stream_bot'
# Endpoints to machines
machine_3 = 'https://cnc.kovalev.team/get/3'
machine_5 = 'https://cnc.kovalev.team/get/5'
# MQTT entry data
ip = '82.146.60.95'
port = 1883
login = 'admin1'
password = '@dm!N'
QoS = '0'
clientID = '12333'

def get_chat_id(token):
    bot_token = TOKEN
    send_text = 'https://api.telegram.org/bot' + bot_token + '/getUpdates'
    r = str(json.loads(requests.get(send_text).text)['result'][0].get('message').get('chat').get('id'))
    return r
def telegram_bot_sendtext(bot_message):
   bot_token = TOKEN
   chat_id = get_chat_id(bot_token)
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
   requests.post(send_text)



async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! My name is Manu. I will notify you if there is any issues with the machinery')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('My name is Manu. I collect data from machinery and notify you if there is an error with it.'
                                    ' Hope I can help you in your work!')

async def get_status3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r3 = requests.get(machine_3).json()
    if r3['data'][1][1][2][1] == 'Ошибка':
        await update.message.reply_text('Status: ' + r3['data'][1][1][2][1] + ' Channel number where the error occured: '
                                        + r3['data'][2][1][0][1] + ' Error code: ' + r3['data'][2][1][1][1])
    else:
        await update.message.reply_text(r3['data'][1][1][2][1])



async def get_status5_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r5 = requests.get(machine_5).json()

    if r5['data'][1][1][2][1] == 'Ошибка':
        await update.message.reply_text('Status: ' + r5['data'][1][1][2][1] + ' Channel number where the error occured: '
                                        + r5['data'][2][1][0][1] + ' Error code: ' + r5['data'][2][1][1][1])
    else:
        await update.message.reply_text(r5['data'][1][1][2][1])


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# Error checkers for Manu.
async def error_3_screening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = 0
    last_message = 0
    while status == 0:
        if len(json.loads(requests.get(send_text).text)['result']) == 0:
            pass
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) == '/stop':
            await update.message.reply_text('You stopped the stream!')
            status += 1
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) != '/stop':
            pass
        else:
            pass

        file = requests.get(machine_3).json()
        if file['data'][1][1][2][1] != 'Ошибка' and last_message == 1:
            await update.message.reply_text('You have tackled the error! Everything is fine now!')
            last_message -= 1
        elif last_message == 1:
            await update.message.reply_text('The error is still in place! Tackle it already!')
        elif file['data'][1][1][2][1] == 'Ошибка':
            await update.message.reply_text('An error occurred with machine 3')
            last_message += 1
        else:
            await update.message.reply_text('Everything is fine for now!')
        time.sleep(10)


async def error_5_screening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = 0
    last_message = 0
    while status == 0:
        if len(json.loads(requests.get(send_text).text)['result']) == 0:
            pass
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) == '/stop':
            await update.message.reply_text('You stopped the stream!')
            status += 1
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) != '/stop':
            pass
        else:
            pass

        file = requests.get(machine_5).json()
        if str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) == '/stop':
            await update.message.reply_text('You stopped the stream!')
            status += 1
        elif file['data'][1][1][2][1] != 'Ошибка' and last_message == 1:
            await update.message.reply_text('You have tackled the error! Everything is fine now!')
            last_message -= 1
        elif last_message == 1:
            await update.message.reply_text('The error is still in place! Tackle it already!')
        elif file['data'][1][1][2][1] == 'Ошибка':
            await update.message.reply_text('An error occurred with the machine 5')
            last_message += 1
        else:
            await update.message.reply_text('Everything is fine for now!')
        time.sleep(10)

async def sensor_screening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = 0

    def on_message_print(client, userdata, message):
        if message.topic == 'sensor/hump' and str(message.payload.decode()) == 'true':
            pass
        elif message.topic == 'sensor/temp' and str(message.payload.decode()) == 'true':
            pass

        elif message.topic == 'sensor/hump' and int(message.payload.decode()) > 70:
            telegram_bot_sendtext('The humidity is high above 70%!')

        elif message.topic == 'sensor/temp' and int(message.payload.decode()) > 30:
            telegram_bot_sendtext('The temperature is high above 30C!')


        else:
            print('nothing')
        client.disconnect()

    while status == 0:
        if len(json.loads(requests.get(send_text).text)['result']) == 0:
            pass
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) == '/stop':
            await update.message.reply_text('You stopped the stream!')
            status += 1
            break
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) != '/stop':
            pass
        else:
            pass
        # Humidity check
        subscribe.callback(on_message_print, "sensor/hump", hostname=ip, port=1883,
                           client_id='', auth={'username': login, 'password': password}, keepalive=1)
        # Temperature check
        subscribe.callback(on_message_print, "sensor/temp", hostname=ip, port=1883,
                           client_id='', auth={'username': login, 'password': password}, keepalive=1)

        time.sleep(1)


async def error_screening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = 0
    last_message_3 = 0
    last_message_5 = 0

    def on_message_print(client, userdata, message):
        if message.topic == 'sensor/hump' and int(message.payload.decode()) > 70:
            telegram_bot_sendtext('The humidity is high above 70%!')
        elif message.topic == 'sensor/temp' and int(message.payload.decode()) > 30:
            telegram_bot_sendtext('The temperature is high above 30C!')
        else:
            print('nothing')
        client.disconnect()


    while status == 0:

        if len(json.loads(requests.get(send_text).text)['result']) == 0:
            pass
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) == '/stop':
            await update.message.reply_text('You stopped the stream!')
            status += 1
            break
        elif str(json.loads(requests.get(send_text).text)['result'][-1].get('message').get('text')) != '/stop':
            pass
        else:
            pass

        # Machine 3 check
        file_3 = requests.get(machine_3).json()
        if file_3['data'][1][1][2][1] != 'Ошибка' and last_message_3 == 1:
            await update.message.reply_text('You have tackled the error with machine 3! Everything is fine now!')
            last_message_3 -= 1
        elif last_message_3 == 1:
            await update.message.reply_text('The error with machine 3 is still in place! Tackle it already!')
        elif file_3['data'][1][1][2][1] == 'Ошибка':
            await update.message.reply_text('An error occurred with machine 3')
            last_message_3 += 1

        # Machine 5 check

        file_5 = requests.get(machine_5).json()
        if file_5['data'][1][1][2][1] != 'Ошибка' and last_message_5 == 1:
            await update.message.reply_text('You have tackled the error with machine 5! Everything is fine now!')
            last_message_5 -= 1
        elif last_message_5 == 1:
            await update.message.reply_text('The error with machine 5 is still in place! Tackle it already!')
        elif file_5['data'][1][1][2][1] == 'Ошибка':
            await update.message.reply_text('An error occurred with machine 5')
            last_message_5 += 1

        # Humidity check
        subscribe.callback(on_message_print, "sensor/hump", hostname=ip, port=1883,
                           client_id='', auth={'username': login, 'password': password}, keepalive=1)
        # Temperature check
        subscribe.callback(on_message_print, "sensor/temp", hostname=ip, port=1883,
                           client_id='', auth={'username': login, 'password': password}, keepalive=1)

        time.sleep(1)





# One loop doesn't allow for another to check... Need to think about a way of how to manage it. Maybe a program with two loops?
def on_message_print(client, userdata, message):
    print("%s %s" % (message.topic, message.payload))
    client.disconnect()



subscribe.callback(on_message_print, "sensor/hump", hostname=ip, port=1883,
                   client_id='', auth={'username': login, 'password': password}, keepalive=1)

# Creating the app itself
if __name__ == '__main__':
    print('Manu is starting...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('check_3_status', get_status3_command))
    app.add_handler(CommandHandler('check_5_status', get_status5_command))
    app.add_handler(CommandHandler('error_3_screening', error_3_screening))
    app.add_handler(CommandHandler('error_5_screening', error_5_screening))
    app.add_handler(CommandHandler('sensor_screening', sensor_screening))
    app.add_handler(CommandHandler('error_screening', error_screening))


    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)