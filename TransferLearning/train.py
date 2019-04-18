from __future__ import absolute_import, division, print_function

import matplotlib.pylab as plt

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow.keras.backend as K
import numpy as np
import PIL.Image as Image
from tensorflow.keras import layers

def feature_extractor(x):
  feature_extractor_module = hub.Module(HUB_URL)
  return feature_extractor_module(x)


EPOCHS=1
DATA_ROOT='/home/joao/repos/FoodDataset/images'
HUB_URL = "https://tfhub.dev/google/imagenet/inception_v3/feature_vector/1"
IMAGE_SIZE = hub.get_expected_image_size(hub.Module(HUB_URL))
image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1/255)
image_data = image_generator.flow_from_directory(str(DATA_ROOT), target_size=IMAGE_SIZE)


for image_batch,label_batch in image_data:
  print("Image batch shape: ", image_batch.shape)
  print("Labe batch shape: ", label_batch.shape)
  break

#MODEL_NAME='{}-{}_epochs-numclasses_{}'.format('Inceptionv3', EPOCHS, image_data.batch_size)
VERSION = 1
features_extractor_layer = layers.Lambda(feature_extractor, input_shape=IMAGE_SIZE+[3])
features_extractor_layer.trainable = False

model = tf.keras.Sequential([
  features_extractor_layer,
  layers.Dense(image_data.num_classes, activation='softmax')
])

init = tf.global_variables_initializer()
sess = K.get_session()
sess.run(init)

model.summary()

model.compile(
  optimizer=tf.keras.optimizers.Adam(), 
  loss='categorical_crossentropy',
  metrics=['accuracy'])

steps_per_epoch = image_data.samples//image_data.batch_size
model.fit((item for item in image_data), epochs=EPOCHS, 
                    steps_per_epoch=steps_per_epoch)


with tf.keras.backend.get_session() as sess:
    tf.saved_model.simple_save(
        sess,
        './export_model/{}'.format(VERSION),
        inputs={'input_image': model.input},
        outputs={t.name: t for t in model.outputs})