import requests
import json


def get_chat_id(tg_token):
    bot_token = tg_token
    send_text = 'https://api.telegram.org/bot' + bot_token + '/getUpdates'
    r = str(json.loads(requests.get(send_text).text)['result'][0].get('message').get('chat').get('id'))
    return r

def telegram_bot_sendtext(tg_token, bot_message):
   bot_token = tg_token
   chat_id = get_chat_id(bot_token)
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
   requests.post(send_text)