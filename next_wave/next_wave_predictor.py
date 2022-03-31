# library imports
import numpy as np
import pandas as pd
import scipy.stats as stats
from xgboost import XGBRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import cross_val_score

# project imports


class NextWavePredictor:
    """
    A class responsible to train, test, and use of a model that gets a dataset of signals over time with wave data
    of pandemic and returns when it finds next wave in a binary way
    """

    # CONSTS #
    Y_COL_NAME = ""
    DATE_COL_NAME = "date"
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
        model = XGBRegressor(objective='reg:squarederror')
        scores = cross_val_score(model,
                                 x_train,
                                 y_train,
                                 cv=RepeatedKFold(n_splits=5,
                                                  n_repeats=3,
                                                  random_state=73),
                                 scoring='neg_mean_absolute_error',
                                 verbose=1)
        # let the user know about the performance
        scores = [abs(val) for val in scores]
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
            metric = mean_absolute_error
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
            cols.append(df.shift(i) if i < 0 else df.shift(i).drop([var_names[-1]], axis=1))
            names += ['{}(t-{})'.format(var_names[j], i) for j in range(n_vars if i < 0 else n_vars-1)]
        # forecast var
        cols.append(df.shift(-n_out)[var_names[-1]])
        names += "y"
        # put it all together
        agg = pd.concat(cols, axis=1)
        agg.columns = names
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)
        return agg
