import datetime
import requests

def check_unread_message(avito_user_id, avito_auth_token, token_type):
    url = 'https://api.avito.ru/messenger/v2/accounts/' + avito_user_id + '/chats'
    header = {'Authorization': token_type + ' ' + avito_auth_token}
    params = {"unread_only": 'true'}
    try:
        chats = requests.get(url, params=params, headers=header)
        if chats.status_code == 200:
            if len(chats.json()['chats']) > 0:
                print(str(datetime.datetime.now()) + ' a new messages found!')
                return chats.status_code, chats
            else:
                return chats.status_code, chats
        else:
            print(str(datetime.datetime.now()) + ' Error code ' + str(chats.status_code) + ' ' + chats.json()['result']['message'])
            return chats.status_code, chats
    except:
        return '403', []

def retrieve_message_data(chat):
    chat = chat.json()
    message_count = str(len(chat['chats']))
    chat_id = chat['chats'][0]['id']
    title = chat['chats'][0]['context']['value']['title']
    writer = chat['chats'][0]['users'][0]['name']
    return message_count, chat_id, title, writer