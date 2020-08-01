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
    print("Getting Image")
    im = get_image(image_path)
    test_image = np.asarray(im)

    print("Preprocessing image")
    processed_test_image = process_image(test_image)
    batched_test_image = np.expand_dims(processed_test_image, axis=0)

    print("Predicting Flower")
    preds = model.predict(batched_test_image)[0]
    preds, ind = tf.nn.top_k(preds, 3)
    print("Prediction Complete")
    # print(ind)
    return ind + 1, preds


def predict(token, request_body):
    chat_id = get_chat_id(request_body)
    file_id = request_body.get("message", dict()).get("photo", [dict()])[0].get("file_id")
    if not file_id:
        return send_message(token, chat_id, "Please send a picture of flower")

    file_url = get_file_info(token, file_id)

    if not file_url:
        return send_message(token, chat_id, "Please send a picture of flower")

    classes, probs = _predict(file_url)
    message = ""
    for i in range(len(classes)):
        cls = str(classes[i].numpy())
        prob = probs[i].numpy()
        # print(cls, prob)
        class_name = class_names.get(cls, cls)
        probability = f"{prob * 100:>.3f}%"
        message_part = f"{class_name}: {probability}"
        message += "\n" + message_part

    print("Sending Reply:", message)
    return send_message(token, chat_id, message)


def get_image(image_path):
    fd = urllib.urlopen(image_path, timeout=15)
    image_file = io.BytesIO(fd.read())
    im = Image.open(image_file)
    return im
