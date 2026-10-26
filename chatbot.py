"""
FAQ Chatbot - CodeAlpha AI Internship (Task 2)

How it works:
1. Load the FAQs (questions + answers) from faqs.json
2. Preprocess the text with NLTK: lowercase, tokenize, remove stopwords, lemmatize
   (very short phrases like "who are you" are matched exactly instead)
3. Turn every FAQ into a TF-IDF vector
4. Turn the user's question into a vector the same way
5. Use cosine similarity to find the most similar FAQ
6. Return that FAQ's answer (or ask the user to rephrase if nothing is similar enough)
"""
import json
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FAQ_FILE = Path(__file__).with_name("faqs.json")
THRESHOLD = 0.15  # minimum similarity needed to answer
DEFAULT_SUGGESTIONS = {
    "How do I track my order?",
    "How long does delivery take?",
    "What is your return policy?",
}


def _ensure_nltk_data():
    """Download the small NLTK data files the first time the bot runs."""
    for package in ("stopwords", "wordnet"):
        try:
            if package == "stopwords":
                stopwords.words("english")
            else:
                WordNetLemmatizer().lemmatize("tests")
        except LookupError:
            nltk.download(package, quiet=True)


_ensure_nltk_data()
_tokenizer = RegexpTokenizer(r"[a-z0-9@]+")
_lemmatizer = WordNetLemmatizer()
# Keep "not" and "no" because they change the meaning of a question
_stop_words = set(stopwords.words("english")) - {"not", "no"}


def preprocess(text):
    """Clean text: lowercase -> tokenize -> remove stopwords -> lemmatize."""
    tokens = _tokenizer.tokenize(text.lower())
    tokens = [_lemmatizer.lemmatize(t) for t in tokens if t not in _stop_words]
    return " ".join(tokens)


def normalize(text):
    """Lowercase words only (no stopword removal). Used for exact phrase matching."""
    return " ".join(_tokenizer.tokenize(text.lower()))


class FAQBot:
    def __init__(self, faq_file=FAQ_FILE):
        with open(faq_file, encoding="utf-8") as f:
            self.faqs = json.load(f)
        # Each FAQ is searched by its question plus extra keywords
        documents = [
            preprocess(item["question"] + " " + " ".join(item.get("keywords", [])))
            for item in self.faqs
        ]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(documents)

        # Short phrases such as "who are you" are all stopwords, so we also keep an
        # exact-phrase lookup built from every question, sub-question and keyword.
        self.exact = {}
        for index, item in enumerate(self.faqs):
            phrases = [item["question"]] + [p for p in item["question"].split("?") if p.strip()] + item.get("keywords", [])
            for phrase in phrases:
                self.exact.setdefault(normalize(phrase), index)

    def categories(self):
        """FAQ questions grouped by topic (used for the topic buttons)."""
        groups = {}
        for item in self.faqs:
            category = item.get("category")
            if category and category != "General":
                groups.setdefault(category, []).append(item["question"])
        return [{"name": name, "questions": questions} for name, questions in groups.items()]

    def ask(self, user_text):
        exact_index = self.exact.get(normalize(user_text))
        if exact_index is not None:
            return {
                "answer": self.faqs[exact_index]["answer"],
                "matched_question": self.faqs[exact_index]["question"],
                "score": 1.0,
                "suggestions": [],
            }
        cleaned = preprocess(user_text)
        if not cleaned:
            return self._fallback([], 0.0)

        user_vector = self.vectorizer.transform([cleaned])
        scores = cosine_similarity(user_vector, self.matrix)[0]
        best = int(scores.argmax())
        best_score = float(scores[best])

        if best_score >= THRESHOLD:
            return {
                "answer": self.faqs[best]["answer"],
                "matched_question": self.faqs[best]["question"],
                "score": round(best_score, 2),
                "suggestions": [],
            }
        top = [i for i in scores.argsort()[::-1][:3] if scores[i] > 0]
        return self._fallback(top, best_score)

    def _fallback(self, top_indexes, score):
        if not top_indexes:
            # Nothing matched at all: offer a few popular questions instead
            top_indexes = [i for i, f in enumerate(self.faqs) if f["question"] in DEFAULT_SUGGESTIONS]
        return {
            "answer": "Sorry, I could not find a good answer to that. Try rephrasing, or pick one of these questions.",
            "matched_question": None,
            "score": round(score, 2),
            "suggestions": [self.faqs[i]["question"] for i in top_indexes],
        }


if __name__ == "__main__":
    # Simple terminal chat: python chatbot.py
    bot = FAQBot()
    print("Willow - FAQ assistant (type 'quit' to exit)")
    while True:
        text = input("You: ").strip()
        if text.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        if not text:
            continue
        result = bot.ask(text)
        print("Bot:", result["answer"])
        if result["matched_question"]:
            print(f"     (matched: {result['matched_question']} | similarity {result['score']})")
