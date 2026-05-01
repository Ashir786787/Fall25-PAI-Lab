import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from flask import Flask, render_template, request, jsonify
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

print("Loading dataset...")
df = pd.read_csv(str(BASE_DIR / "dataset.csv"))
questions = df["Question"].tolist()
answers = df["Answer"].tolist()

print("Loading MiniLM model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Embedding questions...")
question_embeddings = model.encode(questions)

dimension = question_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(question_embeddings))
print("FAISS index created successfully!")

def get_bot_reply(user_message):
    if not user_message.strip():
        return "Please ask a question."
        
    query_embedding = model.encode([user_message])
    
    k = 1 
    distances, indices = index.search(np.array(query_embedding), k)
    
    best_distance = distances[0][0]
    best_index = indices[0][0]
    
    if best_distance > 1.2:
        return "Sorry, I am not sure about that. Try asking about our doctors, timings, or location."
        
    return answers[best_index]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        bot_reply = get_bot_reply(user_message)
        return jsonify({"reply": bot_reply})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "I am sorry, something went wrong."}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
