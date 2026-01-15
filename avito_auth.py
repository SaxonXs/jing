import requests

def get_auth_token(client_id, client_secret):
    avito_token_url = 'https://api.avito.ru/token'

    token_info = requests.post(avito_token_url, data={'client_id': str(client_id), 'client_secret': str(client_secret), 'grant_type': 'client_credentials'})
    if token_info.status_code != 200:
        print(token_info.json()['error'])
        return token_info.status_code, token_info.json()['error']
    else:
        print('received token ' + token_info.json()['access_token'])
        return token_info.json()['access_token'], token_info.json()['token_type']





