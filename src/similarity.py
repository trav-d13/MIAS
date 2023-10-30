import pandas as pd
from sklearn.metrics import pairwise as similarity_measures

from pipeline import CosinePipeline
from similarity_interface import Similarity


class CosineSimilarity(Similarity):
    """The class implements a Cosine similarity between a playlist vector and the tracks dataset to determine
        similar tracks to the playlist.

        This class inherits the Similarity interface.

        Attributes:
            additional_weighting (int): The weighting factor applied to weighted columns.
            playlist (DataFrame): The tracks dataset dataframe (before pipeline transformation)
            tracks (DataFrame): The playlist tracks dataframe (before pipeline transformation)
            playlist_features (DataFrame): The tracks dataset features (after transformation pipeline)
            track_features (DataFrame): The playlist tracks features (after transformation pipeline)
            similarity (Series): The ordered ranking of track similarity to the playlist vector (The index is uris)
        """
    def __init__(self, playlist: pd.DataFrame, tracks: pd.DataFrame, weighted_features: list):
        """The initialization of the Cosine Similarity class

        Args:
            playlist (DataFrame): The tracks dataset dataframe (before pipeline transformation)
            tracks (DataFrame): The playlist tracks dataframe (before pipeline transformation)
            weighted_features (list): A list of features to be weighted in order to prioritize feature importance in similarity calculation.

        """
        self.additional_weighting = 2  # Feature weighting value
        features = CosinePipeline.data_pipeline(tracks)  # Pass data through pipeline to extract features

        self.playlist = playlist
        self.tracks = tracks

        self.playlist_features, self.track_features = self.separate_playlist_from_tracks(features)
        self.weight_features(weighted_features)
        self.similarity = None

    def calculate_similarity(self):
        """Method calculates the similarity between a playlist vector and the tracks feature matrix using cosine similarity

        This calculation populates the `self.similarity` field.

        The playlist feature dataframe is mean of each feature, creating a playlist vector.
        """
        playlist_vector = self.vectorize_playlist()
        track_matrix = self.track_features.to_numpy()

        similarity_score = similarity_measures.cosine_similarity(track_matrix, playlist_vector)
        uris = self.track_features.index.tolist()

        self.similarity = pd.Series(similarity_score.T.tolist()[0], index=uris, name='sim_score')

    def access_similarity_scores(self):
        """Getter method to access the `similarity` class field.

        Returns:
            (Series): The track similarity to the playlist vector. Similarity is a Series using uris as the index.
        """
        return self.similarity

    def get_top_n(self, n: int):
        """This method should return the top-n most similar tracks as a Dataframe with essential features included.

        Note, due to the cosine similarity. A similarity value of 1 indicates a high similarity, while a value near 0 indicates a low similarity.

        Args:
            n (int): The top-n most similar tracks to the playlist vector

        Returns:
            (DataFrame): A dataframe containing the top-n tracks.
        """
        sim_df = pd.DataFrame(self.similarity, columns=['sim_score'])
        sorted_sim = sim_df.sort_values(by='sim_score', ascending=False)
        sorted_top = sorted_sim.head(n)
        return sorted_top.merge(self.tracks, left_index=True, right_on='uris')

    def separate_playlist_from_tracks(self, features: pd.DataFrame):
        """Method separates the feature dataframe (from pipeline) into tracks and playlist feature dataframes

        Args:
            features (DataFrame): The track dataset features dataframe (This contains the playlist tracks too)

            Returns:
                playlist_features (DataFrame): The playlist track features dataframe
                tracks_features (DataFrame): The track dataset features dataframe
        """
        playlist_uris = self.playlist['uris'].tolist()
        return features[features.index.isin(playlist_uris)], features[~features.index.isin(playlist_uris)]

    def vectorize_playlist(self):
        """Method vectorizes the playlist track features by determining the mean value of each track feature

        Returns:
            (Numpy vector): The playlist feature vector
        """
        playlist_vector = self.playlist_features.mean(axis=0)
        return playlist_vector.to_numpy().reshape(1, -1)

    def weight_features(self, weighted_columns: list):
        """Method weights the track dataset features (all features are normalized [0, 1]) by a scaler value
        to increase the effect of that feature in the similarity calculation.

        Wighting in cosine similarity increases the impact of the feature in the similarity calculation

        Note, this method directly alters the `self.track_features` field.

        Args:
            weighted_columns: The columns to be weighted by the additional weighting factor.

        """
        all_features = pd.Series(self.track_features.columns)
        feature_filter = all_features.isin(weighted_columns).tolist()   # Boolean filter based on if feature is in weighted columns
        binary_filter = [int(feature) for feature in feature_filter]  # Modify boolean filter into a binary filter
        filler = [1] * len(binary_filter)  # Create a filler of 1's to not effect features that have no weighting
        weights = [(self.additional_weighting * weight) + fill for weight, fill in zip(binary_filter, filler)]  # Calculate feature scaler weights

        self.track_features = self.track_features.mul(weights, axis=1)  # Weight features


