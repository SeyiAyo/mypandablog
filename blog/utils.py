from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd

def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity


def recommend_posts(post_id, posts_df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(posts_df['content'])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    sim_scores = list(enumerate(cosine_sim[posts_df[posts_df['id'] == post_id].index[0]]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:4]  # Get top 3 recommendations

    post_indices = [i[0] for i in sim_scores]
    return posts_df.iloc[post_indices]['title']


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
