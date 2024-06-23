import contextlib
from os import listdir
from os.path import isfile, join, exists, isdir, abspath
import numpy as np
import tensorflow as tf
from tensorflow import keras
from Alexa import alexa_bot
import tensorflow_hub as hub

IMAGE_DIM = 224

@alexa_bot.run_in_exc
def load_images(image_paths, image_size):
    loaded_images = []
    loaded_image_paths = []
    if isdir(image_paths):
        parent = abspath(image_paths)
        image_paths = [join(parent, f) for f in listdir(
            image_paths) if isfile(join(parent, f))]
    elif isfile(image_paths):
        image_paths = [image_paths]
    for img_path in image_paths:
        image = keras.preprocessing.image.load_img(
                img_path, target_size=image_size)
        image = keras.preprocessing.image.img_to_array(image)
        image /= 255
        loaded_images.append(image)
        loaded_image_paths.append(img_path)
    return np.asarray(loaded_images), loaded_image_paths


def load_model(model_path):
    if model_path is None or not exists(model_path):
        raise ValueError( "saved_model_path must be the valid directory of a saved model to load.")
    model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)
    tf.config.run_functions_eagerly(True)
    return model

async def classify(model, input_paths, image_dim=IMAGE_DIM):
    print(input_paths)
    images, image_paths = await load_images(input_paths, (image_dim, image_dim))
    probs = await classify_nd(model, images)
    return dict(zip(['data'], probs))

@alexa_bot.run_in_exc
def classify_nd(model, nd_images):
    model_preds = model.predict(nd_images)
    categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
    probs = []
    for single_preds in model_preds:
        single_probs = {categories[j]: round(float(pred), 6) * 100 for j, pred in enumerate(single_preds)}
        probs.append(single_probs)
    return probs
