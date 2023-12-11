import streamlit as st
import pickle
import pandas as pd
import requests

# API key stored as an environment variable
API_KEY = 'afbfe0eee443a7cbfdaee036c979b83d'


def fetch_poster(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US')
        response.raise_for_status()
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return None


def recommend(movie, movies, similarity):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters


@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()

# Add a brief description
st.write(
    "Welcome to the Movie Recommender System. Select a movie from the dropdown and click the 'Get Recommendations' button to receive personalized movie suggestions.")

st.title("Movie Recommender System")

# Dropdown for movie selection
selected_movie_name = st.selectbox('Select your movie', movies['title'].values)

# Improved button style
if st.button('Get Recommendations', key='recommend_button'):
    # Display loading indicator
    with st.spinner('Getting Recommendations...'):
        names, posters = recommend(selected_movie_name, movies, similarity)

        # Check if there are recommendations
        if names:
            # Display recommendations
            cols = st.columns(5)
            for i in range(min(5, len(names))):
                with cols[i]:
                    st.text(names[i])
                    st.image(posters[i] if posters[i] else 'No poster available')
        else:
            st.warning("No recommendations available for the selected movie.")
