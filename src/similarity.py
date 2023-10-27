from abc import ABC, abstractmethod
import pandas as pd
from pipeline import data_pipeline
from sklearn.metrics import pairwise as similarity_measures


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
        pass

    @abstractmethod
    def access_similarity_scores(self):
        pass

    @abstractmethod
    def get_top_n(self, n: int):
        pass


class CosineSimilarity(Similarity):
    def __init__(self, playlist: pd.DataFrame, tracks: pd.DataFrame):
        features, _ = data_pipeline(tracks)

        self.playlist = playlist
        self.tracks = tracks

        self.playlist_features, self.track_features = self.separate_playlist_from_tracks(features)
        self.similarity = None

    def calculate_similarity(self):
        playlist_vector = self.vectorize_playlist()
        track_matrix = self.track_features.to_numpy()

        similarity_score = similarity_measures.cosine_similarity(track_matrix, playlist_vector)
        uris = self.track_features.index.tolist()

        self.similarity = pd.Series(similarity_score.T.tolist()[0], index=uris, name='sim_score')

    def access_similarity_scores(self):
        return self.similarity

    def get_top_n(self, n: int):
        sim_df = pd.DataFrame(self.similarity, columns=['sim_score'])
        sorted_sim = sim_df.sort_values(by='sim_score', ascending=False)
        sorted_top = sorted_sim.head(n)
        return sorted_top.merge(self.tracks, left_index=True, right_on='uris')

    def separate_playlist_from_tracks(self, features: pd.DataFrame):
        playlist_uris = self.playlist['uris'].tolist()
        return features[features.index.isin(playlist_uris)], features[~features.index.isin(playlist_uris)]

    def vectorize_playlist(self):
        playlist_vector = self.playlist_features.mean(axis=0)
        return playlist_vector.to_numpy().reshape(1, -1)
