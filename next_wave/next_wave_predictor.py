# library imports
import numpy as np
import pandas as pd
import scipy.stats as stats
from xgboost import XGBRegressor
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score

# project imports


class NextWavePredictor:
    """
    A class responsible to train, test, and use of a model that gets a dataset of signals over time with wave data
    of pandemic and returns when it finds next wave in a binary way
    """

    # CONSTS #
    Y_COL_NAME = ""
    DATE_COL_NAME = ""
    # END - CONSTS #

    def __init__(self,
                 prediction_delay: int = 1):
        self._prediction_delay = prediction_delay
        self._model = None

    def fit(self,
            x_train: pd.DataFrame,
            y_train: pd.DataFrame):
        """
        Fit the model on the data
        """
        df = x_train.copy()
        df["y_delayed"] = y_train
        df = NextWavePredictor.series_to_supervised(df=df,
                                                    n_in=14,
                                                    n_out=self._prediction_delay,
                                                    dropnan=True)
        x_train, y_train = df.drop(["y"], axis=1), df["y"]
        model = XGBRegressor(objective='reg:squarederror')
        scores = cross_val_score(model,
                                 x_train,
                                 y_train,
                                 cv=5,
                                 scoring='mean_squared_error',
                                 verbose=1)
        # let the user know about the performance
        print("NextWavePredictor.fit: mean = {:.3f}, std = {:.3f}".format(np.nanmean(scores),
                                                                          np.nanstd(scores)))
        # train on all the train data
        self._model = model.fit(x_train,
                                y_train)

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
    def prepare(x: pd.DataFrame):
        """
        Prepare the data for analysis by the model, run before the fit function to get best results.
        """
        # first, remove lines we cannot use
        x.dropna(inplace=True)
        # remove unneed data
        unneeded_cols = []
        x.drop(unneeded_cols, axis=1, inplace=True)
        # sort by date
        x = x.sort_values(NextWavePredictor.DATE_COL_NAME)
        # normalize signal
        x = x.select_dtypes(include='number').apply(stats.zscore)
        # compute the binary event-based y-signal
        return x

    @staticmethod
    def series_to_supervised(df,
                             n_in=1,
                             n_out=1,
                             dropnan=True):
        """
        Frame a time series as a supervised learning dataset.
        Arguments:
            data: Sequence of observations as a list or NumPy array.
            n_in: Number of lag observations as input (X).
            n_out: Number of observations as output (y).
            dropnan: Boolean whether or not to drop rows with NaN values.
        Returns:
            Pandas DataFrame of series framed for supervised learning.
        """
        n_vars = 1 if type(df) is list else df.shape[1]
        var_names = list(df)
        cols, names = list(), list()
        # input sequence (t-n, ... t-1)
        for i in range(n_in, -1, -1):
            cols.append(df.shift(i))
            names += ['{}(t-{})'.format(var_names[j], i) for j in range(n_vars)]
        # forecast var
        cols.append(df.shift(-n_out))
        names += "y"
        # put it all together
        agg = pd.concat(cols, axis=1)
        agg.columns = names
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)
        return agg
