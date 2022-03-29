# library imports
import numpy as np
import pandas as pd
import scipy.stats as stats
from tensorflow import keras
from sklearn.metrics import accuracy_score

# project imports


class NextWavePredictor:
    """
    A class responsible to train, test, and use of a model that gets a dataset of signals over time with wave data
    of pandemic and returns when it finds next wave in a binary way
    """

    def __init__(self,
                 prediction_delay: int = 1):
        self._prediction_delay = prediction_delay
        self._model = None

    def fit(self,
            name: str,
            x_train: pd.DataFrame,
            y_train: pd.Series,
            epochs: int = 100,
            batch_size: int = 32):
        """
        Fit the model on the data
        """
        # prepare model
        self._model = NextWavePredictor.make_model(input_shape=x_train.shape[1:])
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                "best_model_{}.h5".format(name),
                save_best_only=True,
                monitor="val_loss"
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=20, min_lr=0.0001
            ),
            keras.callbacks.EarlyStopping(monitor="val_loss", patience=50, verbose=1),
        ]
        self._model.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["sparse_categorical_accuracy"],
        )
        history = self._model.fit(
            x_train,
            y_train,
            batch_size=batch_size,
            epochs=epochs,
            callbacks=callbacks,
            validation_split=0.2,
            verbose=1,
        )
        self._model = keras.models.load_model("best_model_{}.h5".format(name))

    def test(self,
              x_test: pd.DataFrame,
              y_test: pd.Series):
        """
        Used the trained model to predict the outcome
        """
        return self._model.evaluate(x_test, y_test)

    def predict(self,
                x: pd.DataFrame):
        """
        Used the trained model to predict the outcome
        """
        return self._model.predict(x)

    def score(self,
              x_test: pd.DataFrame,
              y_test: pd.Series,
              metric=None):
        """
        Compute the 'metric' of the model on the given test data.
        If not 'metric' function is provided, we would use 'accuracy'
        """
        if metric is None:
            metric = accuracy_score
        return metric(y_true=y_test,
                      y_pred=self.predict(x=x_test))

    @staticmethod
    def prepare(x: pd.DataFrame,
                y: pd.Series,
                y_classify_function):
        """
        Prepare the data for analysis by the model, run before the fit function to get best results.
        Of note, the 'y_classify_function' is a function that gets a pd.Series and returns a binary pd.Series indicates when an event is occurred
        """
        # first, remove lines we cannot use
        x.dropna(inplace=True)
        # normalize signal
        x = x.select_dtypes(include='number').apply(stats.zscore)
        # compute the binary event-based y-signal
        return x, y_classify_function(y)

    @staticmethod
    def make_model(input_shape,
                   num_classes: int = 2):
        """
        Build the structure of the NN
        """
        input_layer = keras.layers.Input(input_shape)

        conv1 = keras.layers.Conv1D(filters=64, kernel_size=3, padding="same")(input_layer)
        conv1 = keras.layers.BatchNormalization()(conv1)
        conv1 = keras.layers.ReLU()(conv1)

        conv2 = keras.layers.Conv1D(filters=64, kernel_size=3, padding="same")(conv1)
        conv2 = keras.layers.BatchNormalization()(conv2)
        conv2 = keras.layers.ReLU()(conv2)

        conv3 = keras.layers.Conv1D(filters=64, kernel_size=3, padding="same")(conv2)
        conv3 = keras.layers.BatchNormalization()(conv3)
        conv3 = keras.layers.ReLU()(conv3)

        gap = keras.layers.GlobalAveragePooling1D()(conv3)

        output_layer = keras.layers.Dense(num_classes, activation="softmax")(gap)

        return keras.models.Model(inputs=input_layer, outputs=output_layer)

