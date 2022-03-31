# library imports
import os
import json

# project imports
from next_wave.next_wave_manager import NextWaveManager
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
        cluster_words_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "word_clusters.json")
        try:
            with open(cluster_words_file_path, "r") as cluster_data_file:
                word_clusters_in_signals = json.load(cluster_data_file)
        except:
            word_clusters_in_signals = PrepareSignals().get_clusters_words_from_file(save_path=cluster_words_file_path,
                                                                                     top_k=1000)
        # prepare signal data
        signals = signals_prepare.convert_to_signals(word_clusters_in_signals=word_clusters_in_signals)
        # use signal data for model training
        model_wrapper = NextWaveManager()
        model_wrapper.load_data(path_or_df=signals)
        model_wrapper.fit()
        model_wrapper.eval()


if __name__ == '__main__':
    NextWaveRunner.run()
