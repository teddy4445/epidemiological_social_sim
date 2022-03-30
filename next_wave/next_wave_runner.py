# library imports
import os
import json

# project imports
from next_wave.next_wave import NextWave
from next_wave.prepare_signal_data_from_covid_and_twitter import PrepareSignals


class NextWaveRunner:
    """
    This class responsible for the entire 'next wave' predictor pipeline
    """

    def __init__(self):
        pass

    @staticmethod
    def run():
        """
        Single entry function
        """
        # prepare the data for signal extraction from Twitter and WHO data
        if os.path.exists(PrepareSignals.FINAL_RAW_FILE_PATH):
            signals_prepare = PrepareSignals().load_final()
        else:
            signals_prepare = PrepareSignals().load()
        # load cluster data
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "clusters_words.json"), "r") as cluster_data_file:
            word_clusters_in_signals = json.load(cluster_data_file)
        # prepare signal data
        signals = signals_prepare.convert_to_signals(word_clusters_in_signals=word_clusters_in_signals)
        # use signal data for model training
        model_wrapper = NextWave()
        model_wrapper.load_data(path_or_df=signals)
        model_wrapper.fit()


if __name__ == '__main__':
    NextWaveRunner.run()
