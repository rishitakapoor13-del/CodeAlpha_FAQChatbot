# CodeAlpha_FAQChatbot

An FAQ chatbot built for the **CodeAlpha Artificial Intelligence Internship (Task 2)**.

Meet **Willow**, a friendly assistant for a demo online shop. Willow answers questions about orders, shipping, returns and getting started by finding the FAQ that is most similar to what the user typed.
The shop and its policies are made up for this project.

## How it works
1. FAQs (category, question, answer and keywords) are stored in `faqs.json`
2. The text is preprocessed with **NLTK**: lowercase, tokenize, remove stopwords, lemmatize
3. Each FAQ is converted into a **TF-IDF** vector (calculated from scratch in `chatbot.py`, in plain Python, so no scikit-learn is needed)
4. The user's question is converted into a vector in the same way
5. **Cosine similarity** finds the closest FAQ, and its answer is shown with a match percentage
6. Very short phrases such as "who are you" are matched exactly, because all their words are stopwords
7. If nothing is similar enough, Willow says so and suggests related questions

## Features
- NLP preprocessing with NLTK
- Cosine similarity matching, with the matched FAQ and match % shown under each answer
- 39 FAQs in 4 topics: Orders & tracking, Shipping & delivery, Returns & refunds, Getting started
- Chat UI in the browser (Flask) with topic buttons, quick questions and a "Start over" button
- Terminal mode as well
- Easy to change the topic: edit `faqs.json`

## Project files
| File | Purpose |
|------|---------|
| `chatbot.py` | NLP and matching logic (can run alone in the terminal) |
| `app.py` | Flask web server |
| `index.html`, `style.css`, `script.js` | Chat user interface |
| `faqs.json` | The FAQ data |
| `requirements.txt` | Python libraries |

## How to run
1. Install Python 3.9 or newer
2. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
3. Start the chat page:
   ```
   python app.py
   ```
4. Open http://127.0.0.1:5000 in your browser

Terminal-only mode: `python chatbot.py`

The first run downloads two small NLTK data files (stopwords and wordnet), so an internet connection is needed once.

## Changing the topic
Open `faqs.json` and replace the entries. Each one looks like this:
```json
{
  "category": "Shipping & delivery",
  "question": "How long does delivery take?",
  "answer": "Standard delivery takes 3 to 5 business days.",
  "keywords": ["delivery time", "when will it arrive", "how many days"]
}
```
Adding different ways people might ask the same thing to `keywords` makes the matching better.

## Author
Rishita Kapoor - CodeAlpha AI Intern
