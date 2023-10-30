from abc import ABC, abstractmethod


class Pipeline(ABC):
    """This class serves as transformation pipeline from Spotify tracks raw data to track features

    Note, the tracks database is stored in the `data/tracks.csv` file.
    """
    @staticmethod
    @abstractmethod
    def data_pipeline(df):
        """This method enacts the transformation pipeline to produce a set of track features.
        It is expected for the playlist to return a pandas DataFrame containing all features.

        Args:
            df (DataFrame): The dataframe containing the raw data from the `data/tracks.csv` file
        """
        pass
