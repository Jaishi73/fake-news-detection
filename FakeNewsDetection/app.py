from flask import Flask, render_template, request, jsonify, request,redirect, url_for, session, flash
import pickle
import requests
import re
import nltk
from nltk.corpus import stopwords
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '3136298b3be1c582feb05ba6db20bdb34bf55183da07775f827c85946a002d8a'

# Load the trained model and vectorizer
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

# Google Fact Check API Key
API_KEY = "AIzaSyBeoTMITNsDpmeS5i0ohsRN412qbJyQC2E"

# News API Key
NEWS_API_KEY = "6ce7d5ab4ecc48e6b8aeb5ffbe986b59"

#search news api 
NEWSDATA_API_KEY = "pub_72918454bc7e4d9473cba1e27b034533920f2"


# Download stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Preprocessing function
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)  # Remove special characters
    text = text.lower()
    text = text.split()
    text = [word for word in text if word not in stop_words]  # Remove stopwords
    return ' '.join(text)

# FIXED: Improved Google Fact Check API extraction
def check_fact_with_google(query):
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error if the request fails
        data = response.json()

        # Debug: Print API Response
        print("API RESPONSE:", data)  #  Add this to see full API output in terminal/logs

        claims = data.get("claims", [])
        if not claims:
            print("No claims found in API response")  # 👈 Debug message if no claims

        fact_checks = []
        for claim in claims[:3]:  # Limit to top 3 claims
            fact_check_info = claim.get("claimReview", [{}])[0]

            fact_checks.append({
                "claim": claim.get("text", "No claim text available"),
                "publisher": fact_check_info.get("publisher", {}).get("name", "Unknown"),
                "title": fact_check_info.get("title", "No title available"),
                "url": fact_check_info.get("url", "No URL available"),
                "rating": fact_check_info.get("textualRating", "No rating available")
            })

        return fact_checks if fact_checks else None

    except requests.exceptions.RequestException as e:
        print("Error contacting Google API:", e)  # Catch network errors
        return None  # Return None if API request fails


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    news_text = request.form.get('news_text', '')

    if not news_text:
        return jsonify({"error": "No text provided"}), 400

    processed_text = preprocess_text(news_text)

    # Check Google Fact Check API first
    fact_check_results = check_fact_with_google(news_text)

    if fact_check_results:  # If fact-check results exist
        return jsonify({
            "result": "Fact Checked",
            "fact_check": fact_check_results
        })  

    #  If no fact-check result, use ML model
    text_vectorized = vectorizer.transform([processed_text])
    prediction = model.predict(text_vectorized)[0]
    confidence = max(model.predict_proba(text_vectorized)[0]) * 100

    result = "Real News" if prediction == 1 else "Fake News"

    return jsonify({
        "result": result,
        "confidence": f"{confidence:.2f}",
        "fact_check": "No relevant claim found in Google Fact Check API"
    })

@app.route('/fetch-news', methods=['GET'])
def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])[:8]
        news_items = [
            {
                "title": article.get("title", "No title available"),
                "url": article.get("url", "#"),
                "image": article.get("urlToImage", "https://via.placeholder.com/150"),
                "video": article["url"] if "youtube.com" in article["url"] else ""  # For potential video links
            }
            for article in articles
        ]
        return jsonify(news_items)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch news", "details": str(e)})

@app.route('/search-news')
def search_news():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    api_url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q={query}&language=en,&country=in"
    response = requests.get(api_url)
    data = response.json()

    news_items = [
        {
            "title": item.get("title", "No Title"),
            "published_date": item.get("pubDate"),
            "url": item.get("link", "#"),
            "image": item.get("image_url", 'default-news.jpg')
        }
        for item in data.get("results", [])
    ]
    return jsonify(news_items)

# Feedback Submission Route
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    news_title = request.form.get('news-title')
    news_content = request.form.get('news-content')
    user_name = request.form.get('user-name')
    user_email = request.form.get('user-email')

    # Example: Save to database or file (for simplicity)
    with open('feedback_data.txt', 'a') as f:
        f.write(f"{news_title} | {news_content} | {user_name} | {user_email}\n")

    return jsonify({'message': 'Feedback submitted successfully!'})


# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tiger@1234'
app.config['MYSQL_DB'] = 'fakenews_db3'

mysql = MySQL(app)

# ---------- ROUTES ----------

 #Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user1 WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Username or Email already exists. Choose a different one.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password and insert the new user
        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO user1 (username, email, password) VALUES (%s, %s, %s)", 
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('home'))

    return render_template('signupfact.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user1 WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['email'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('loginfact.html')


 #Logout Route
@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

    
  



if __name__ == '__main__':
    app.run(debug=True)
