# library imports
import os
import pandas as pd
from glob import glob


# project imports


class DataFrameLoader:
    """
    This class responsible for loading the dataframe from memory in an efficient way
    """

    # CONSTS #

    # END - CONSTS #

    def __init__(self,
                 data_folder: str):
        self._dataset_index = 0
        self._dataset_paths = [path for path in glob(os.path.join(data_folder, "*.csv"))]

    def __iter__(self):
        return self

    def __next__(self):
        if self._dataset_index >= len(self._dataset_paths):
            self._dataset_index = 0
            raise StopIteration
        else:
            answer = (os.path.basename(self._dataset_paths[self._dataset_index]),
                      pd.read_csv(self._dataset_paths[self._dataset_index]))
            self._dataset_index += 1
            return answer

    def reset(self):
        self._dataset_index = 0

    def load_folder(self,
                    data_folder: str):
        self._dataset_paths = [path for path in glob(os.path.join(data_folder, "*.csv"))]

    def load_by_index(self,
                      dataset_index: int) -> tuple:
        """
        Load a given dataset by index
        """
        try:
            return pd.read_csv(self._dataset_paths[dataset_index]), os.path.basename(self._dataset_paths[dataset_index])
        except:
            raise IndexError("DataFrameLoader.load_by_index: out of index error with index = {}".format(dataset_index))

    def load_by_name(self,
                      dataset_name: str) -> tuple:
        """
        Load a given dataset by name
        """
        try:
            for path in self._dataset_paths:
                if os.path.basename(path) == dataset_name:
                    return pd.read_csv(path), dataset_name
        except:
            raise IndexError("DataFrameLoader.load_by_name: the folder {} does not contains dataset with the name  = {}".format(os.path.dirname(self._dataset_paths[0]),
                                                                                                                                dataset_name))

    def load_next(self) -> tuple:
        """
        Each call, return the next dataset as pd.DataFrame with its name as the file's name.
        If ended, we return none DF object and empty name
        """
        try:
            answer = (os.path.basename(self._dataset_paths[self._dataset_index]), pd.read_csv(self._dataset_paths[self._dataset_index]))
            self._dataset_index += 1
            return answer
        except:
            return None, ""

    def load_all(self) -> list:
        """
        load as a list all the datasets in the folder
        """
        return [(pd.read_csv(path), os.path.basename(path)) for path in self._dataset_paths]
