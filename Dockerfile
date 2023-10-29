# Use the official Python image as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the app files from the src directory to the container
COPY . /app

# Install any dependencies
RUN pip install -r requirements.txt

# Expose the port that Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "src/recommender.py"]