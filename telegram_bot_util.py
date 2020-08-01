import requests

# bot_token = "1258354561:AAGstJOjdzGrK2yHi3x2e2U3781dREi-lUQ"

send_message_url = "https://api.telegram.org/bot{bot_token}/sendMessage"

get_file_url = "https://api.telegram.org/bot{bot_token}/getFile"

file_download_url = "https://api.telegram.org/file/bot{bot_token}/"


def get_chat_id(request_body):
    return request_body.get("message", dict()).get("chat", dict()).get("id")


def send_message(token, chat_id, text):
    params = {
        "text": text,
        "chat_id": chat_id
    }

    return requests.request("GET", send_message_url.format(bot_token=token), params=params)


def get_file_info(token, file_id):
    params = {
        "file_id": file_id
    }

    response = requests.request("GET", get_file_url.format(bot_token=token), params=params).json()
    if response.get("ok"):
        return file_download_url.format(bot_token=token) + response.get("result").get("file_path")
    else:
        return None
