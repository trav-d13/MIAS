import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer

from pipeline_interface import Pipeline


class CosinePipeline(Pipeline):
    """This class serves as the transformation pipeline from raw data to usable features, for the similarity calculation
    carried out by the Cosine Similarity class."""

    @staticmethod
    def select_columns(df):
        """This method selects the columns to be included within feature calculations.

        This method, allows for the ignoring/ removal of peripheral or uneeded columns.

        Args:
            df (DataFrame): The dataframe containing the raw data from the `data/tracks.csv` file

        Returns:
            (DataFrame): The modified dataframe object containing only the select columns.
        """
        df = df[['uris', 'artist_pop',
                 'artist_genres', 'track_pop', 'danceability', 'energy',
                 'keys', 'loudness', 'modes', 'speechiness', 'acousticness',
                 'instrumentalness', 'liveness', 'valences', 'tempos', 'durations_ms', 'time_signatures']]
        return df

    @staticmethod
    def ohe_prep(df, column):
        """This method performs a One-Hot-Encoding (OHE) on a specified column

        Args:
            df (DataFrame): The dataframe containing the tracks information, now being processes by the pipeline.
            column (str): The name of the column on which the OHE transformation should be performed.
        """
        df_encoded = pd.get_dummies(df, columns=[column], dtype=int)
        return df_encoded

    @staticmethod
    def tfidf_transformation(df_parm):
        """This method performs the term frequency–inverse document frequency (tfidf) transformation on the `artist genre` column.

        Note, more information on tfidf transformation can be found here: https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/

        Args:
            df_parm (DataFrame): The dataframe containing the tracks information, now undergoing tfidg transfromation

        Returns:
            (DataFrame): The transformed dataframe containing the results of the tfidf transfromation.
        """
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=0.0, max_features=50)
        tfidf_matrix = tf.fit_transform(df_parm['artist_genres'])

        genre_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tf.get_feature_names_out())
        genre_df.columns = ['genre' + "|" + i for i in genre_df.columns]

        df_parm = df_parm.drop(columns=['artist_genres'])

        combined_df = pd.concat([df_parm.reset_index(drop=True), genre_df.reset_index(drop=True)], axis=1)
        return combined_df

    @staticmethod
    def data_pipeline(df):
        """This method enacts the transformation pipeline to produce a set of track features.

        This pipeline makes use of the following transformation methods:
        - One-hot_encoding
        - TFIDF transformation
        - Min-Max Scaling of numerical values

        Args:
            df (DataFrame): The dataframe containing the raw data from the `data/tracks.csv` file

        Returns:
              (DataFrame): A dataframe containing all track features
        """

        df_pipe = CosinePipeline.select_columns(df)

        # Perform OHE
        df_pipe = CosinePipeline.ohe_prep(df_pipe, 'modes')
        df_pipe = CosinePipeline.ohe_prep(df_pipe, 'keys')
        df_pipe = CosinePipeline.ohe_prep(df_pipe, 'time_signatures')

        # Normalize popularity values
        scaler = MinMaxScaler(feature_range=(0, 1))
        columns = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valences', 'durations_ms', 'tempos']
        df_pipe[columns] = scaler.fit_transform(df_pipe[columns])

        # Perform TFID vectorization on genres
        df_pipe = CosinePipeline.tfidf_transformation(df_parm=df_pipe)

        df_pipe = df_pipe.set_index(keys='uris', drop=True)

        return df_pipe

    @staticmethod
    def unique_tracks(df, df_target):
        """Method ensures that df (tracks dataframe) does not contain the same tracks as the playlist (df_target)

        Args:
            df (DataFrame): The dataframe containing the tracks dataset.
            df_target (DataFrame): The dataframe containing the tracks from the playlist

        Returns:
            (DataFrame): The tracks dataframe containing none of the same tracks as in the playlist.
        """
        df = df.drop(df_target['uris'], errors='ignore')
        return df

    @staticmethod
    def extract_target(df, df_target):
        """This method allows for the extraction of tracks in the playlist from the tracks dataset.
        Note, for this method to work, the track uris should be the index in the tracks dataframe (df).

        This method is largely used once the tracks dataset has been transformed into a set of features,
        and the playlist track features are required to be extracted.

        Args:
            df (DataFrame): The dataframe containing the tracks dataset.
            df_target (DataFrame): The dataframe containing the tracks from the playlist

        Returns:
            (DataFrame): A resulting dataframe containing only the tracks from the playlist that were in the tracks dataset.
        """
        target_uris = df_target['uris'].tolist()
        return df[df.index.isin(target_uris)]

