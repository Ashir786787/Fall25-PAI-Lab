import os
import math
import random
import re
from collections import Counter
from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

samples = [
    ("This movie was fantastic and full of emotions", 1),
    ("I really liked the direction and acting", 1),
    ("What a wonderful and heart touching story", 1),
    ("The film was boring and too long", 0),
    ("Worst script I have seen this year", 0),
    ("The acting was poor and the plot was weak", 0),
    ("Amazing visuals and a great soundtrack", 1),
    ("I enjoyed every scene of this movie", 1),
    ("The experience was disappointing and dull", 0),
    ("Not worth the ticket price", 0),
    ("Excellent screenplay and strong performances", 1),
    ("The ending was predictable and bad", 0),
    ("I would recommend this to my friends", 1),
    ("The dialogues were unnatural and forced", 0),
    ("A very refreshing and entertaining film", 1),
    ("Too much noise and no real story", 0),
    ("Superb camera work and editing", 1),
    ("It felt like a waste of time", 0),
    ("Great pacing and impressive character development", 1),
    ("Music was loud and irritating", 0),
    ("The cast delivered a memorable performance", 1),
    ("I almost slept during the second half", 0),
    ("Storyline was creative and engaging", 1),
    ("Nothing new, very average and forgettable", 0),
]

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he",
    "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "were",
    "will", "with", "this", "i", "what", "very", "too", "no", "not",
}

def tokenize(text):
    text = text.lower()
    words = re.findall(r"[a-z']+", text)
    tokens = []
    for w in words:
        if w not in STOP_WORDS:
            tokens.append(w)
    return tokens

def split_data(data, test_ratio=0.25):
    pos_samples = []
    neg_samples = []
    for s in data:
        if s[1] == 1:
            pos_samples.append(s)
        else:
            neg_samples.append(s)

    random.seed(42)
    random.shuffle(pos_samples)
    random.shuffle(neg_samples)

    pos_test_size = int(len(pos_samples) * test_ratio)
    neg_test_size = int(len(neg_samples) * test_ratio)

    test_data = pos_samples[:pos_test_size] + neg_samples[:neg_test_size]
    train_data = pos_samples[pos_test_size:] + neg_samples[neg_test_size:]

    random.shuffle(test_data)
    random.shuffle(train_data)
    return train_data, test_data

def get_vocab(texts):
    vocab = {}
    for t in texts:
        tokens = tokenize(t)
        for tok in tokens:
            if tok not in vocab:
                vocab[tok] = len(vocab)
    return vocab

def text_to_vector(text, vocab):
    tokens = tokenize(text)
    counts = Counter(tokens)
    vec = {}
    for word, count in counts.items():
        if word in vocab:
            word_idx = vocab[word]
            vec[word_idx] = count
    return vec

class MultinomialNB:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes = [0, 1]
        self.priors = {}
        self.probs = {}

    def train(self, vectors, labels, vocab_size):
        total_docs = len(labels)
        label_counts = Counter(labels)

        class_word_counts = {0: Counter(), 1: Counter()}
        class_total_words = {0: 0, 1: 0}

        for i in range(len(vectors)):
            vec = vectors[i]
            label = labels[i]
            for idx, count in vec.items():
                class_word_counts[label][idx] += count
                class_total_words[label] += count

        for c in self.classes:
            self.priors[c] = math.log(label_counts[c] / total_docs)
            denom = class_total_words[c] + self.alpha * vocab_size
            self.probs[c] = {}
            for i in range(vocab_size):
                count = class_word_counts[c].get(i, 0)
                self.probs[c][i] = math.log((count + self.alpha) / denom)

    def calculate_scores(self, vector):
        scores = {}
        for c in self.classes:
            s = self.priors[c]
            for idx, count in vector.items():
                s += count * self.probs[c].get(idx, 0)
            scores[c] = s
        return scores

    def predict(self, vectors):
        results = []
        for v in vectors:
            scores = self.calculate_scores(v)
            if scores[1] > scores[0]:
                results.append(1)
            else:
                results.append(0)
        return results

    def get_probs(self, vector):
        scores = self.calculate_scores(vector)
        max_s = max(scores.values())
        e0 = math.exp(scores[0] - max_s)
        e1 = math.exp(scores[1] - max_s)
        total = e0 + e1
        return [e0/total, e1/total]

def get_report(y_true, y_pred):
    report = "label      precision    recall  f1-score   support\n"
    for label, name in [(0, "negative"), (1, "positive")]:
        tp = 0
        fp = 0
        fn = 0
        support = 0
        for i in range(len(y_true)):
            if y_true[i] == label:
                support += 1
                if y_pred[i] == label:
                    tp += 1
                else:
                    fn += 1
            elif y_pred[i] == label:
                fp += 1
        
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        report += f"{name:<10} {p:>9.2f} {r:>9.2f} {f1:>9.2f} {support:>9}\n"
    return report

def start_training():
    train_data, test_data = split_data(samples)
    x_train = [s[0] for s in train_data]
    y_train = [s[1] for s in train_data]
    x_test = [s[0] for s in test_data]
    y_test = [s[1] for s in test_data]

    vocab = get_vocab(x_train)
    train_vecs = [text_to_vector(t, vocab) for t in x_train]
    test_vecs = [text_to_vector(t, vocab) for t in x_test]

    model = MultinomialNB()
    model.train(train_vecs, y_train, len(vocab))

    preds = model.predict(test_vecs)
    correct = 0
    for i in range(len(y_test)):
        if y_test[i] == preds[i]:
            correct += 1
    acc = correct / len(y_test)
    rep = get_report(y_test, preds)

    return model, vocab, acc, rep

trained_model, vocabulary, accuracy, report_str = start_training()

@app.route("/", methods=["GET", "POST"])
def home():
    input_val = ""
    prediction = None
    confidence = None
    pos_score = None
    neg_score = None
    words = 0
    chars = 0

    if request.method == "POST":
        input_val = request.form.get("review_text", "").strip()
        if input_val:
            vec = text_to_vector(input_val, vocabulary)
            pred = trained_model.predict([vec])[0]
            prediction = "positive" if pred == 1 else "negative"

            probs = trained_model.get_probs(vec)
            neg_score = round(probs[0] * 100, 2)
            pos_score = round(probs[1] * 100, 2)
            confidence = max(pos_score, neg_score)
            words = len(input_val.split())
            chars = len(input_val)

    return render_template(
        "index.html",
        accuracy=round(accuracy * 100, 2),
        report=report_str,
        input_text=input_val,
        prediction=prediction,
        confidence=confidence,
        positive_score=pos_score,
        negative_score=neg_score,
        word_count=words,
        char_count=chars
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
