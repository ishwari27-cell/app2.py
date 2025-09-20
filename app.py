# pip install streamlit textblob  wordcloud PyPDF2
import streamlit as st
from collections import Counter
from wordcloud import WordCloud
from io import BytesIO
from PIL import Image

# Inside admin_page():

comments = st.session_state["comments"]

if comments:
    # Top 5 words
    from nltk.corpus import stopwords
    import nltk
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))

    all_words = [
        word for word in " ".join([c["comment"] for c in comments]).lower().split()
        if word not in stop_words
    ]
    common_words = Counter(all_words).most_common(5)
    st.write("### 🔝 Top 5 Words Used")
    st.table(common_words)

    # Sentiment distribution using st.bar_chart
    st.write("### 📈 Sentiment Distribution")
    sentiments = [c["sentiment"] for c in comments]
    sentiment_counts = Counter(sentiments)
    st.bar_chart(sentiment_counts)

    # Word Cloud using st.image
    st.write("### ☁️ Word Cloud")
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        " ".join([c["comment"] for c in comments])
    )
    img = BytesIO()
    wordcloud.to_image().save(img, format="PNG")
    st.image(Image.open(img), use_column_width=True)



