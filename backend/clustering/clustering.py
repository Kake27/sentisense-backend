from transformers import TFAutoModel, AutoTokenizer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import json
import tensorflow as tf
from dotenv import load_dotenv
import os

load_dotenv()



class Clustering:
    def __init__(self):
        # Construct the absolute path to the model directory
        model_name = os.path.abspath(os.path.join(os.getcwd(), "backend", "clustering", "tfmodel"))
        # Load the tokenizer and model from the local directory
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        self.model = TFAutoModel.from_pretrained(model_name, local_files_only=True)
    
    def mean_pooling(self, model_output, attention_mask):
        """Applies mean pooling over token embeddings"""
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = tf.cast(tf.expand_dims(attention_mask, -1), tf.float32)
        sum_embeddings = tf.reduce_sum(token_embeddings * input_mask_expanded, axis=1)
        sum_mask = tf.reduce_sum(input_mask_expanded, axis=1)
        return sum_embeddings / sum_mask
    
    def encode_text(self, text_list):
        """Encodes text into embeddings using TensorFlow model"""
        tokens = self.tokenizer(text_list, return_tensors="tf", padding=True, truncation=True)
        model_output = self.model(tokens)
        embeddings = self.mean_pooling(model_output, tokens["attention_mask"]).numpy()
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)  # Normalize
        return embeddings
    
    def create_cluster(self, df):
        df["embeddings"] = list(self.encode_text(df["Comment"].tolist()))
        
        num_clusters = 3
        sentiment_clusters = {}

        for sentiment in df["Sentiment"].unique():
            subset = df[df["Sentiment"] == sentiment]
            X = np.vstack(subset["embeddings"].values)
            if len(subset) < num_clusters:
                num_clusters = len(subset)  # Adjust cluster count if less data
            kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X)
            df.loc[df["Sentiment"] == sentiment, "cluster"] = clusters
            
            cluster_map = {}
            for i in range(num_clusters):
                phrases = subset.iloc[np.where(clusters == i)]["Comment"].tolist()
                if phrases:
                    cluster_map[i] = phrases[:3]
            
            sentiment_clusters[sentiment] = cluster_map
        
        json_output = json.dumps(sentiment_clusters, indent=4, ensure_ascii=False)
        return json_output

if __name__ == "__main__":
    # Example usage
    data = {
        "Comment": [
            "Great product!", "I love this!", "Not what I expected.", "Will not buy again.", "Excellent service!", "Very disappointed."
        ],
        "Sentiment": ["Positive", "Positive", "Negative", "Negative", "Positive", "Negative"]
    }
    
    df = pd.DataFrame(data)
    clustering = Clustering()
    result = clustering.create_cluster(df)
    print(result)