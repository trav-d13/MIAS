# Musically Illiterate Aide System (MIAS)
Content covering basic content and collaborative filtering recommender systems culminating in a Spotify song recommendation system.

## Developer

### Spotify Credential Management

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



### Streamlit Application

#### Running the Application

```
streamlit run src/app.py
```

#### Spotify Developer Credentials
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
