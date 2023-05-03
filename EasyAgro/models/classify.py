import numpy as np
import cv2
import tensorflow as tf
import tensorflow_hub as hub
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

model = tf.keras.models.load_model('my_model.h5', custom_objects={'KerasLayer':hub.KerasLayer})

def ident(image):
	# print("FILE NAME: ")
	filename = image

	image = cv2.imread(filename)
	image = cv2.resize(image, (224, 224))
	image = np.array(image) / 255.0
	image = np.expand_dims(image, axis=0)

	prediction = model.predict(image)

	predicted_label = np.argmax(prediction)

	labels = {}
	labels[0] = "Early Blight"
	labels[1] = "Healthy"
	labels[2] = "Late Blight"

	# print(f"{labels[predicted_label]}")
	return f"{labels[predicted_label]}"

# print("FILE NAME: ")
# filename = input()

# image = cv2.imread(filename)
# image = cv2.resize(image, (224, 224))
# image = np.array(image) / 255.0
# image = np.expand_dims(image, axis=0)

# prediction = model.predict(image)

# predicted_label = np.argmax(prediction)

# labels = {}
# labels[0] = "Early Blight"
# labels[1] = "Healthy"
# labels[2] = "Late Blight"

# print(f"{labels[predicted_label]}")
