# University Lab - NLP Sentiment Analysis

## Student Information
- **Course**: Programming for AI (Lab)
- **Task**: Lab 9 (NLP Text Classification)
- **Topic**: Movie Review Sentiment Analysis

## Project Overview
In this lab, I developed an NLP-based text classifier that categorizes input sentences into **Positive** or **Negative** sentiments. The project is built using Python and Flask, with a custom-built machine learning model implemented from scratch.

## Implementation Details
For this assignment, I followed a standard NLP pipeline to ensure accuracy and reliability:

1. **Dataset Creation**: 
   I used a custom dataset of movie-style reviews, labeled with 1 (Positive) and 0 (Negative).

2. **Data Preprocessing**:
   - Converted all text to lowercase to maintain uniformity.
   - Used a custom tokenizer to extract words.
   - Implemented a stop-word removal step to filter out common words (like 'the', 'is', 'a') that don't add semantic value.

3. **Feature Engineering**:
   I implemented a **Bag of Words** (BoW) model to convert text data into numerical vectors. This allows the mathematical model to process the text by counting the frequency of each word in the vocabulary.

4. **Machine Learning Model**:
   I built a **Multinomial Naive Bayes** classifier from scratch. This model uses probability theory (Bayes' Theorem) to predict the most likely sentiment for a given set of words.

5. **Validation**:
   The dataset was split into training and testing sets. I calculated the **Accuracy** and generated a **Classification Report** (Precision, Recall, F1-Score) to evaluate the model's performance.

## Technology Stack
- **Backend**: Python 3
- **Web Framework**: Flask
- **Frontend**: HTML5 / CSS3 (with Responsive Design)
- **Libraries**: `os`, `math`, `re`, `collections`

## How to Set Up and Run
1. **Install Requirements**:
   ```bash
   pip install flask
   ```

2. **Run the Server**:
   ```bash
   python main.py
   ```

3. **Access the App**:
   Open your browser and navigate to `http://127.0.0.1:5001`

## Project Structure
- `main.py`: The main server file containing the ML model logic and Flask routes.
- `templates/index.html`: The user interface for entering text and viewing predictions.
- `requirements.txt`: List of dependencies.
