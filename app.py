# pip install streamlit textblob PyPDF2 nltk

import streamlit as st
from textblob import TextBlob
import PyPDF2
from collections import Counter
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

# -------------------------------
# Initialize session state
# -------------------------------
if "comments" not in st.session_state:
    st.session_state["comments"] = []  # List of dicts: {name, comment, sentiment}


# -------------------------------
# Sentiment Analysis
# -------------------------------
def analyze_sentiment(text):
    """Return sentiment category: Positive, Negative, Neutral"""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"


# -------------------------------
# User Page
# -------------------------------
def user_page():
    st.title("💬 User Page")
    st.write("Enter your name and comment on the uploaded proposal:")

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

    # Upload PDF
    uploaded_file = st.file_uploader("📄 Upload Proposal (PDF)", type="pdf")
    if uploaded_file:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        proposal_text = ""
        for page in pdf_reader.pages:
            proposal_text += page.extract_text() or ""
        st.subheader("Proposal Content")
        st.write(proposal_text)

    st.subheader("📊 Comments Analysis")
    comments = st.session_state["comments"]

    if not comments:
        st.info("No comments yet.")
        return

    # Show all comments with delete buttons
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
    stop_words = set(stopwords.words('english'))
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




