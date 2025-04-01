from keras._tf_keras.keras.preprocessing.sequence import pad_sequences
from keras._tf_keras.keras.models import load_model
import pickle
from dotenv import load_dotenv
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

load_dotenv()

class SentimentAnalysis:
    def __init__(self):
        self.model = load_model(os.path.join(os.path.dirname(__file__), 'sentisensemodel.h5'))

        with open(os.path.join(os.path.dirname(__file__), 'sstokenizer.pickle'), 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    def predict_class(self, text):
        sentiment_classes = ['Negative', 'Neutral', 'Positive']
        max_len=50

        xt = self.tokenizer.texts_to_sequences(text)

        xt = pad_sequences(xt, padding='post', maxlen=max_len)

        yt = self.model.predict(xt).argmax(axis=1)

        return sentiment_classes[yt[0]]


if __name__ == "__main__":
    analyser = SentimentAnalysis()
    s1 = analyser.predict_class(["I am gay"])
    s2 = analyser.predict_class(["That was the worst movie ever"])
    s3 = analyser.predict_class(["I neither love you nor hate you"])

    print(s1, s2, s3)