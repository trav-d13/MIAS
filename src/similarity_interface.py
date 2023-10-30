from abc import ABC, abstractmethod


class Similarity(ABC):
    """This class serves as an outline of the Similarity module for the MIAS application

    There are multiple ways of achieving a recommendation system/ similarity of tracks.
    This modular build allows others to add their own classes to try out various methods in
    a simple way

    Note: The playlist has already been added to the tracks dataset, such that features are
    calculated over the entire database. The playlist tracks are then removed from the tracks dataaset
    in the similarity calculation.

    Additionally: It is recommended that your class take in both `playlist` and `tracks` as done
    in the Cosine Similarity Class
    """
    @abstractmethod
    def calculate_similarity(self):
        """Method calculates the similarity of each track in the dataset to the given playlist feature vector

        Note, this method should populate a field called `self.similarity`, such that it represents a similarity score of
        each track to playlist vector. Please see `similarity.py` for an example implementation.
        """
        pass

    @abstractmethod
    def access_similarity_scores(self):
        """This method is a getter method providing access to the similarity metrics calculated in `calculate_similarity()`"""
        pass

    @abstractmethod
    def get_top_n(self, n: int):
        """This method should return the top-n most similar tracks as a Dataframe with essential features included.
        Note, see `similarity.py` for an example implementation
        Note, depending on your similarity calculation, be careful of the type of ordering you implement.
        """
        pass

    @abstractmethod
    def weight_features(self, weighted_columns: list):
        """This method allows for specific features to be weighted or have a more significant impact on the measures of similarity.
        Note, weighting may vary depending on the method of similarity calculation. Please see `similarity.py` for an example
        implementation
        """
        pass

