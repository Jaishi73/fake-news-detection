import pandas as pd
import re
import nltk
import pickle
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load Dataset
df_fake = pd.read_csv('Fake.csv')
df_real = pd.read_csv('True.csv')

df_fake['label'] = 0  # Fake News
df_real['label'] = 1  # Real News

# Combine both datasets
df = pd.concat([df_fake, df_real])

# Shuffle dataset
df = df.sample(frac=1).reset_index(drop=True)

# Download stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Preprocessing function
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)  # Remove special characters
    text = text.lower()  # Convert to lowercase
    text = text.split()  # Tokenization
    text = [word for word in text if word not in stop_words]  # Remove stopwords
    return ' '.join(text)

# Apply preprocessing
df['text'] = df['title'] + " " + df['text']  # Combine title and content
df['text'] = df['text'].apply(preprocess_text)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

# Convert text to numerical features using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train Logistic Regression Model
model = LogisticRegression()
model.fit(X_train_vec, y_train)

# Evaluate Model
y_pred = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model Accuracy: {accuracy * 100:.2f}%')

# Save the trained model and vectorizer
with open('model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

print("Model and vectorizer saved successfully!")
