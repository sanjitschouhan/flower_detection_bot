import io
import json
from urllib import request as urllib

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image

from telegram_bot_util import send_message, get_chat_id, get_file_info

image_size = 224


def load_model(model_file):
    return tf.keras.models.load_model(model_file, custom_objects={'KerasLayer': hub.KerasLayer})


model = load_model("my_model.h5")

with open("label_map.json", 'r') as f:
    class_names = json.load(f)


def process_image(image):
    image = tf.cast(image, tf.float32)
    image = tf.image.resize(image, (image_size, image_size))
    image /= 255
    return image


def _predict(image_path):
    im = get_image(image_path)
    test_image = np.asarray(im)

    processed_test_image = process_image(test_image)
    batched_test_image = np.expand_dims(processed_test_image, axis=0)

    preds = model.predict(batched_test_image)[0]
    ind = np.argmax(preds)
    return ind + 1, preds[ind]


def predict(token, request_body):
    chat_id = get_chat_id(request_body)
    file_id = request_body.get("message", dict()).get("photo", [dict()])[0].get("file_id")
    if not file_id:
        return send_message(token, chat_id, "Please send a picture of flower")

    file_url = get_file_info(token, file_id)

    if not file_url:
        return send_message(token, chat_id, "Please send a picture of flower")

    cls, prob = _predict(file_url)
    cls = str(cls)

    class_name = class_names.get(cls, cls)
    probability = f"{prob * 100:>.3f}%"

    return send_message(token, chat_id, f"Flower Name: {class_name}\nProbability: {probability}")


def get_image(image_path):
    fd = urllib.urlopen(image_path, timeout=15)
    image_file = io.BytesIO(fd.read())
    im = Image.open(image_file)
    return im
