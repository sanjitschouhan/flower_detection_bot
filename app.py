import os

from flask import Flask, make_response, request

from predict import predict

app = Flask(__name__)


@app.route('/<token>', methods=['POST'])
def web_hook(token):
    body = request.json
    print(body)
    response = predict(token, body)
    print(response.json())
    return make_response("", 200)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
