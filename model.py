import numpy as np
import tensorflow as tf
from tensorflow import keras

class DualModel(keras.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        slowLayers = [l for l in self.layers if type(l).__name__ != "LSTM"]
        fastLayers = [l for l in self.layers if not type(l).__name__ != "LSTM"]
        self.slowVars = [var for l in slowLayers for var in l.trainable_variables]
        self.fastVars = [var for l in fastLayers for var in l.trainable_variables]

    def train_step(self, data):
        (vecs, words), rars = data

        for _ in range(10):
            with tf.GradientTape() as tape:
                pred = self((vecs, words), training = True)
                loss = self.compiled_loss(rars, pred, regularization_losses = self.losses)

            gradients = tape.gradient(loss, self.fastVars)
            self.optimizer.apply_gradients(zip(gradients, self.fastVars))
            self.compiled_metrics.update_state(rars, pred)

        with tf.GradientTape() as tape:
            pred = self((vecs, words), training = True)
            loss = self.compiled_loss(rars, pred, regularization_losses = self.losses)

        gradients = tape.gradient(loss, self.slowVars)
        self.optimizer.apply_gradients(zip(gradients, self.slowVars))
        self.compiled_metrics.update_state(rars, pred)

        return {m.name: m.result() for m in self.metrics}