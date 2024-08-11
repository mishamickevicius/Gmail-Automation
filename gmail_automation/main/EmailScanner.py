from joblib import load

from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer


class EmailScanner:
    def __init__(self):
        self.vectorizer: TfidfVectorizer = load('/home/dude/Desktop/Projects/Gmail-Automation/gmail_automation/vectorizer.joblib')
        self.model: LinearSVC = load('/home/dude/Desktop/Projects/Gmail-Automation/gmail_automation/model.joblib')

    def regular_scan(self, subject:str, body:str):
        full_msg = subject.lower() + " " + body.lower()
        vectorized = self.vectorizer.transform([full_msg])
        result = self.model.predict(vectorized)
        return result[0]


if __name__ == '__main__':
    scanner = EmailScanner()
    print(scanner.regular_scan("Greetings from Misha", "I am writing this email to say hello. Have a good day"))
