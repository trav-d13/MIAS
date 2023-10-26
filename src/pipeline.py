import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer


def select_columns(df):
    df = df[['uris', 'artist_pop',
             'artist_genres', 'track_pop', 'danceability', 'energy',
             'keys', 'loudness', 'modes', 'speechiness', 'acousticness',
             'instrumentalness', 'liveness', 'valences', 'tempos', 'durations_ms', 'time_signatures']]
    return df


def ohe_prep(df, column):
    df_encoded = pd.get_dummies(df, columns=[column], dtype=int)
    return df_encoded


def tfidf_transformation(df_parm, tf=None):
    if tf is None:
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=0.0)
        tfidf_matrix = tf.fit_transform(df_parm['artist_genres'])
    else:
        tfidf_matrix = tf.transform(df_parm['artist_genres'])

    genre_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tf.get_feature_names_out())
    genre_df.columns = ['genre' + "|" + i for i in genre_df.columns]

    df_parm = df_parm.drop(columns=['artist_genres'])

    combined_df = pd.concat([df_parm.reset_index(drop=True), genre_df.reset_index(drop=True)], axis=1)
    return combined_df, tf


def data_pipeline(df, tf=None):
    # Select only the necessary columns
    df = select_columns(df)
    print(f'After select columns {df.shape}')

    # Perform OHE
    df = ohe_prep(df, 'modes')
    df = ohe_prep(df, 'keys')
    print(f'After ohe {df.shape}')

    # Normalize popularity values
    scaler = MinMaxScaler()
    df[['artist_pop', 'track_pop']] = scaler.fit_transform(df[['artist_pop', 'track_pop']])
    print(f'After scaling {df.shape}')

    # Perform TFID vectorization on genres
    df, tf = tfidf_transformation(df_parm=df, tf=tf)
    print(f'After tfid {df.shape}')

    df = df.set_index(keys='uris', drop=True)
    print(f'After index reset {df.shape}')

    return df, tf


def unique_tracks(df, df_target):
    df = df.drop(df_target['uris'], errors='ignore')
    return df


def extract_target(df, df_target):
    target_uris = df_target['uris'].tolist()
    return df[df.index.isin(target_uris)]


if __name__ == "__main__":
    df_target = pd.read_csv('../data/target.csv', index_col=0)
    df = pd.read_csv('../data/tracks.csv', index_col=0)

    dataset_complete = pd.concat([df_target, df], axis=0)
    dataset_complete = dataset_complete.reset_index(drop=True)
    print(f'prior {dataset_complete.shape}')

    dataset_complete = dataset_complete.drop_duplicates(subset='uris', keep='first')
    print(f'After duplicate drop {dataset_complete.shape}')

    dataset_complete, _ = data_pipeline(df=dataset_complete)
    print(f'After feature creation {dataset_complete.shape}')

    target_features = extract_target(dataset_complete, df_target)
    print(target_features.shape)

    df_unique = unique_tracks(dataset_complete, df_target)
    print(df_unique.shape)