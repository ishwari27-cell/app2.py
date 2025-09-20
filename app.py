# pip install streamlit nltk

import streamlit as st
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
import base64

# -------------------------------
# NLTK setup
# -------------------------------
nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)

stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()

# -------------------------------
# Initialize session state
# -------------------------------
if "comments" not in st.session_state:
    st.session_state["comments"] = []  # list of dicts: {name, comment, sentiment}

# -------------------------------
# Sentiment Analysis
# -------------------------------
def analyze_sentiment(text):
    """Return sentiment category using VADER"""
    scores = sia.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# -------------------------------
# User Page
# -------------------------------
def user_page():
    st.title("💬 User Page")
    st.write("View the proposal and submit your comment:")

    uploaded_file = st.file_uploader("📄 Upload Proposal (PDF)", type="pdf", key="user_pdf")
    if uploaded_file:
        # Display PDF download button
        st.download_button("📥 Download PDF", uploaded_file, file_name=uploaded_file.name)

        # Embed PDF for viewing
        base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
        st.components.v1.html(pdf_display, height=500)

    # User comment section
    name = st.text_input("Your Name")
    comment = st.text_area("Your Comment")

    if st.button("Submit Comment"):
        if name.strip() and comment.strip():
            sentiment = analyze_sentiment(comment)
            st.session_state["comments"].append(
                {"name": name, "comment": comment, "sentiment": sentiment}
            )
            st.success("✅ Comment submitted successfully!")
        else:
            st.error("⚠️ Please enter both name and comment.")

# -------------------------------
# Admin Page
# -------------------------------
def admin_page():
    st.title("🛠️ Admin Page")
    st.write("Users' comments analysis:")

    comments = st.session_state["comments"]

    if not comments:
        st.info("No comments yet.")
        return

    # Display comments with delete buttons
    st.write("### All Comments")
    for i, c in enumerate(comments):
        st.markdown(f"**{c['name']}**: {c['comment']} _(Sentiment: {c['sentiment']})_")
        delete_key = f"delete_{i}"
        if delete_key not in st.session_state:
            st.session_state[delete_key] = False
        if st.button(f"🗑️ Delete Comment {i+1}", key=delete_key):
            st.session_state["comments"].pop(i)
            st.experimental_rerun()

    # -------------------------------
    # Top Words
    # -------------------------------
    st.write("### 🔝 Top Words Used")
    all_words = [
        word for word in " ".join([c["comment"] for c in comments]).lower().split()
        if word.isalpha() and word not in stop_words
    ]
    common_words = Counter(all_words).most_common(10)
    if common_words:
        st.table(common_words)
        st.bar_chart(dict(common_words))

    # -------------------------------
    # Sentiment Distribution
    # -------------------------------
    st.write("### 📈 Sentiment Distribution")
    sentiments = [c["sentiment"] for c in comments]
    sentiment_counts = Counter(sentiments)
    st.bar_chart(dict(sentiment_counts))

# -------------------------------
# Navigation
# -------------------------------
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio("Choose a page:", ["User", "Admin"])

if page == "User":
    user_page()
else:
    admin_page()


