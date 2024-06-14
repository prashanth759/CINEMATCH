from flask import Flask, render_template, request, redirect, url_for
import joblib
app = Flask(__name__)
model_path = 'movie_rating_model.pkl'
class Movie:
    def __init__(self, title, genres, rating):
        self.title = title
        self.genres = genres  # List of genres
        self.rating = rating

class CineMatch:
    def __init__(self, model_path):
        self.movies = []
        self.model = joblib.load(model_path)

    def add_movie(self, title, genres):
        # Check if the movie already exists
        if any(movie.title.lower() == title.lower() for movie in self.movies):
            return False
        # Combine title and genres into a single text feature
        combined_features = title + ' ' + ' '.join(genres)
        # Predict the rating using the trained model
        predicted_rating = self.model.predict([combined_features])[0]
        movie = Movie(title, genres, round(predicted_rating, 1))
        self.movies.append(movie)
        return True

    def search_by_title(self, title):
        return next((movie for movie in self.movies if movie.title.lower() == title.lower()), None)
    def search_by_genre(self, genre):
        return [movie for movie in self.movies if any(g.lower() == genre.lower() for g in movie.genres)]

    def recommend_top_n_movies(self, n):
        sorted_movies = sorted(self.movies, key=lambda movie: movie.rating, reverse=True)
        return sorted_movies[:n]

    def delete_movie(self, title):
        initial_count = len(self.movies)
        self.movies = [movie for movie in self.movies if movie.title.lower() != title.lower()]
        return len(self.movies) < initial_count

cinematch = CineMatch(model_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        genres = request.form['genres'].split(',')  # Split genres by comma
        if cinematch.add_movie(title, genres):
            return redirect(url_for('index'))
        else:
            return "Movie already exists!"
    return render_template('add_movie.html')

@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST':
        title = request.form.get('title')
        genre = request.form.get('genre')
        
        results = []

        if title and genre:
            movie = cinematch.search_by_title(title)
            if movie and genre.lower() in (g.lower() for g in movie.genres):
                results.append(movie)
        elif title:
            movie = cinematch.search_by_title(title)
            if movie:
                results.append(movie)
        elif genre:
            results = cinematch.search_by_genre(genre)

        return render_template('search_movie.html', movies=results)
    
    return render_template('search_movie.html', movies=None)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend_movie():
    if request.method == 'POST':
        top_n = request.form.get('top_n')
        genre = request.form.get('genre')

        if top_n:  # If top_n is provided, recommend top N movies
            n = int(top_n)
            top_movies = cinematch.recommend_top_n_movies(n)
            return render_template('recommend_movie.html', movies=top_movies, mode='Top N')
        elif genre:  # If genre is provided, recommend movies of that genre
            genre_movies = cinematch.search_by_genre(genre)
            return render_template('recommend_movie.html', movies=genre_movies, mode='Genre')
        else:
            return "Please provide either Top N or Genre for recommendations."

    return render_template('recommend_movie.html', movies=None)

@app.route('/delete', methods=['GET', 'POST'])
def delete_movie():
    if request.method == 'POST':
        title = request.form['title']
        if cinematch.delete_movie(title):
            return redirect(url_for('index'))
        else:
            return "Movie not found!"
    return render_template('delete_movie.html')

if __name__ == '__main__':
    app.run(debug=True)
