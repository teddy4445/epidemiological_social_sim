# library imports
import os
import json
import pandas as pd


# projects imports


class PrepareSignals:
    """
    This class responsible to get the data from twitter about signals and the corresponding pandemic data from WHO for the entire USA.

    The twitter data is obtained from Arriel (co-author).
    The COVID-19 data is obtained from https://github.com/nytimes/covid-19-data/blob/master/us-states.csv
    """

    # CONSTS #
    DEFAULT_TWITTER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "clean_tweets.csv")
    DEFAULT_WHO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "covid_us.csv")

    TWITTER_COLS_DROP = ["name", "location", "retweets", "Time", "week", "followers", "like", "day", "month", "year", "year_week",
                         "year_month"]
    WHO_COLS_DROP = ["deaths"]

    TWITTER_DATE_COL_NAME = "Date"
    WHO_DATE_COL_NAME = "date"
    TWITTER_DATE_FORMAT = "%y-%m-%d"
    WHO_DATE_FORMAT = "%y-%m-%d"

    FIXED_DEFAULT_TWITTER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "fixed_clean_tweets.csv")
    FIXED_DEFAULT_WHO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "fixed_covid_us.csv")
    FINAL_RAW_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "raw_signal_file.csv")

    Y_COL_NAME = "cases"
    WORDS_COL_NAME = "words"

    # END - CONSTS #

    def __init__(self):
        self._df = None

    def load(self,
             twitter_data_file_path: str = "",
             covid_data_file_path: str = ""):
        # load data
        print("PrepareSignals.load: Loading data")
        _twitter = pd.read_csv(twitter_data_file_path if twitter_data_file_path != "" else PrepareSignals.DEFAULT_TWITTER_PATH)
        _who = pd.read_csv(covid_data_file_path if covid_data_file_path != "" else PrepareSignals.DEFAULT_WHO_PATH)
        # clear empty rows
        print("PrepareSignals.load: drop nulls")
        _twitter.dropna(inplace=True)
        _who.dropna(inplace=True)
        # clear unwanted data
        print("PrepareSignals.load: leave only needed columns")
        _twitter.drop(PrepareSignals.TWITTER_COLS_DROP, axis=1, inplace=True)
        _who.drop(PrepareSignals.WHO_COLS_DROP, axis=1, inplace=True)
        # treat the date cols as dates
        print("PrepareSignals.load: treat date column as date object")
        _twitter[PrepareSignals.TWITTER_DATE_COL_NAME] = _twitter[PrepareSignals.TWITTER_DATE_COL_NAME].apply(lambda x: x.split(" ")[0])
        _twitter[PrepareSignals.TWITTER_DATE_COL_NAME] = pd.to_datetime(_twitter[PrepareSignals.TWITTER_DATE_COL_NAME],
                                                                        infer_datetime_format=True)
        _who[PrepareSignals.WHO_DATE_COL_NAME] = pd.to_datetime(_who[PrepareSignals.WHO_DATE_COL_NAME],
                                                                infer_datetime_format=True)
        # remove twits that not in the right scope of the epidemiology data
        print("PrepareSignals.load: filter from twitter data only the same dates as in the who data")
        min_epi_date = min(_who[PrepareSignals.WHO_DATE_COL_NAME])
        max_epi_date = max(_who[PrepareSignals.WHO_DATE_COL_NAME])
        _twitter.drop(_twitter[(_twitter[PrepareSignals.TWITTER_DATE_COL_NAME] < min_epi_date) | (_twitter[PrepareSignals.TWITTER_DATE_COL_NAME] > max_epi_date)].index, inplace=True)
        # merge data based on the date
        print("PrepareSignals.load: build final dataset")
        self._df = pd.DataFrame(data=_who.values,
                                index=_who.index,
                                columns=_who.columns)
        all_text_per_date = list(_twitter.groupby(PrepareSignals.TWITTER_DATE_COL_NAME)["tweet_text"].apply(lambda x: ','.join(x[1:-1].replace("\'", ""))))
        self._df = self._df.iloc[:len(all_text_per_date), :]
        self._df[PrepareSignals.WORDS_COL_NAME] = [[word.strip()
                                                    for word in line.replace("\'", "").replace("[", "").replace("]", "").split(",")]
                                                   for line in all_text_per_date]
        self._df[PrepareSignals.WORDS_COL_NAME] = self._df[PrepareSignals.WORDS_COL_NAME].apply(lambda x: {word: x.count(word) for word in set(x)})
        print("PrepareSignals.__init__: save final dataset")
        self._df.to_csv(PrepareSignals.FINAL_RAW_FILE_PATH,
                        index=False)
        return self

    def load_final(self,
                   final_file_path: str = ""):
        print("PrepareSignals.load_final: Loading data")
        self._df = pd.read_csv(final_file_path if final_file_path != "" else PrepareSignals.FINAL_RAW_FILE_PATH)
        return self

    def convert_to_signals(self,
                           word_clusters_in_signals: list,
                           save_results_path: str = ""):
        """
        Convert the data generated from the raw data into signals based on the words associated with each signal
        """
        signals_sizes = [len(signal) for signal in word_clusters_in_signals]
        answer = self._df[[PrepareSignals.WHO_DATE_COL_NAME, PrepareSignals.Y_COL_NAME]].copy()
        answer[PrepareSignals.Y_COL_NAME] = answer[PrepareSignals.Y_COL_NAME].diff(1)
        for signal_index, signal_cluster in enumerate(word_clusters_in_signals):
            answer["signal_{}".format(signal_index)] = [sum([val
                                                             for key, val in json.loads(word_set.replace("'", "\"")).items() if key in word_clusters_in_signals[signal_index]])/signals_sizes[signal_index]
                                                        for word_set in self._df[PrepareSignals.WORDS_COL_NAME]]
        answer.dropna(inplace=True)
        if save_results_path != "":
            answer.to_csv(save_results_path,
                          index=False)
        return answer
