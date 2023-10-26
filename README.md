# Musically Illiterate Aiding System (MIAS)
Content covering basic content and collaborative filtering recommender systems culminating in a Spotify song recommendation system.

## Developer

### Running the Applcication

```
streamlit run src/app.py
```

### Spotify Credential Management

#### Streamlit Application
The application makes use of Streamlits secrets manager. For the running applications these are stored in the Streamlit running platform. 
In order to make the secrets available during development, please perform the following steps: 

1. Find both your **Client ID** and **Client Secret** from Spotify Developer. 
2. Create the following file `.streamlit/secrets.toml` from the project root directory. 
3. Fill in the following information in the `secrets.toml` file
```toml
CLIENT_ID = "CLIENT ID KEY"
CLIENT_SECRET = "CLIENT SECRET KEY"
```
The application now has access to your spotify credentials.

#### Notebooks
The notebooks make use of environmental variables, please make sure you have a Python file named
`notebooks/credentials.py`.
Inside of `credentials.py` please insert the following with your correct Spotify configuration keys.

```Python
import os


def set_credentials():
    os.environ['CLIENT_ID'] = ""
    os.environ['CLIENT_SECRET'] = ""
```