import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer

from pipeline_interface import Pipeline


class CosinePipeline(Pipeline):
    @staticmethod
    def select_columns(df):
        df = df[['uris', 'artist_pop',
                 'artist_genres', 'track_pop', 'danceability', 'energy',
                 'keys', 'loudness', 'modes', 'speechiness', 'acousticness',
                 'instrumentalness', 'liveness', 'valences', 'tempos', 'durations_ms', 'time_signatures']]
        return df

    @staticmethod
    def ohe_prep(df, column):
        df_encoded = pd.get_dummies(df, columns=[column], dtype=int)
        return df_encoded

    @staticmethod
    def tfidf_transformation(df_parm, tf=None):
        if tf is None:
            tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=0.0, max_features=50)
            tfidf_matrix = tf.fit_transform(df_parm['artist_genres'])
        else:
            tfidf_matrix = tf.transform(df_parm['artist_genres'])

        genre_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tf.get_feature_names_out())
        genre_df.columns = ['genre' + "|" + i for i in genre_df.columns]

        df_parm = df_parm.drop(columns=['artist_genres'])

        combined_df = pd.concat([df_parm.reset_index(drop=True), genre_df.reset_index(drop=True)], axis=1)
        return combined_df, tf

    @staticmethod
    def data_pipeline(df, tf=None):
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
        df_pipe, tf = CosinePipeline.tfidf_transformation(df_parm=df_pipe, tf=tf)

        df_pipe = df_pipe.set_index(keys='uris', drop=True)
        print(f'Transform final shape {df_pipe.shape}')

        return df_pipe, tf

    @staticmethod
    def unique_tracks(df, df_target):
        df = df.drop(df_target['uris'], errors='ignore')
        return df

    @staticmethod
    def extract_target(df, df_target):
        target_uris = df_target['uris'].tolist()
        return df[df.index.isin(target_uris)]

