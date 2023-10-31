# Musically Illiterate Aid System (MIAS)
Content covering basic content and collaborative filtering recommender systems culminating in a Spotify song recommendation system.

The hosted and running application can be found at: [https://mias-recommender-sys.streamlit.app/](https://mias-recommender-sys.streamlit.app/)

## Developer
Please make use of the Developer documentation available here: [https://trav-d13.github.io/MIAS/](https://trav-d13.github.io/MIAS/).

The most upt-to-date dataset is openly available from: [https://mias-recommender-sys.streamlit.app/dataset](https://mias-recommender-sys.streamlit.app/dataset)

Alternatively, the dataset is hosted on Kaggle and available at:

**Disclaimer:** The dataset was collected to create a simple song recommendation system, based on track acoustic features, artist, popularity, etc. It does not include any propriety Spotify audio content or Spotify audio tracks. 
The dataset contains publicly available information from Spotify and is intended only for learning. 
The application deployed is only for testing creating a usable recommender system, it is not intended as a product for commercial or intensive use. Please respect it, and the Spotify Developer API.

**Copyright:**
Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

### Project Structure
```
MIAS/
│
├── .streamlit/
│   └── secrets.toml
│
├── data/
│
├── notebooks/
│
└── src/

```

## Running the Application

### Docker Container
This section deals with building and running the docker container after making changes in the project. 
Please note, that changes to code will not require the Docker image to be re-build, but altering the `requirements.txt`, 
`Dockerfile`, etc., will require the image to be rebuilt. 

1. Build the Docker image
```
sudo docker build -t mias .
```
2. Run the application
```
sudo docker run -p 8501:8501 -v ./data:/app/data mias
```
The container allows for a volume containing all the required data to be linked to the container to allow data access. 

### Manual Running
```
streamlit run src/app.py
```

------------------------------------------------------------------------------------------------------------------------

## Spotify Developer Credentials
The application makes use of Streamlit's secrets manager. For the running applications these are stored in the Streamlit running platform. 
In order to make the secrets available during development, please perform the following steps: 

##### Application
1. Find both your **Client ID** and **Client Secret** from Spotify Developer. 
2. Create the following file `.streamlit/secrets.toml` from the project root directory. 
3. Fill in the following information in the `secrets.toml` file
```toml
CLIENT_ID = "CLIENT ID KEY"
CLIENT_SECRET = "CLIENT SECRET KEY"
```
The application now has access to your spotify credentials.

##### Notebooks
The notebooks make use of environmental variables, please make sure you have a Python file named
`notebooks/credentials.py`.
Inside of `credentials.py` please insert the following with your correct Spotify configuration keys.

```Python
import os

def set_credentials():
    os.environ['CLIENT_ID'] = ""
    os.environ['CLIENT_SECRET'] = ""
```

## Spotify Data Collection
### Automated Collection
The currently running application runs a Chron jobs to scrape and collect tracks from the top-performing playlists
every two-weeks, updating the tracks dataset. 
Additionally, every playlist queried for recommendations is added to the dataset. 
The dataset is freely available, pleas see the _bottom_ of the **dataset** page on the application available at: ...

### Manual Collection
If you would like to test the data processing and manually collect target playlist or general spotify data, copy and
paste the below script to the bottom of `data_processing.py` and execute it using the following command in terminal: 
``` python src/data_processing.py```

```Python
if __name__ == "__main__":
    client_credentials_manager = SpotifyClientCredentials(client_id=st.secrets['CLIENT_ID'],
                                                          client_secret=st.secrets[
                                                              'CLIENT_SECRET'])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    url = "https://open.spotify.com/playlist/799B2k7VQhsWeA2iQrun9f?si=345d3d94fb484f2c"

    # target_playlist_extraction(sp, url, "Rob Performance Playlist")
    top_playlist_extraction(sp)
```