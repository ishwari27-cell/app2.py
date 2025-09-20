# pip install streamlit textblob matplotlib wordcloud PyPDF2

import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
import PyPDF2
from collections import Counter


# Initialize session state for comments
if "comments" not in st.session_state:
    st.session_state["comments"] = []  # list of dicts: {name, comment, sentiment}


def analyze_sentiment(text):
    """Return sentiment category: Positive, Negative, Neutral"""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"


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


def admin_page():
    st.title("🛠️ Admin Page")

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
    else:
        # Show all comments
        st.write("### All Comments")

        for i, c in enumerate(comments):
            st.markdown(
                f"**{c['name']}**: {c['comment']} _(Sentiment: {c['sentiment']})_"
            )
            if st.button(f"🗑️ Delete Comment {i+1}", key=f"delete_{i}"):
                st.session_state["comments"].pop(i)
                st.experimental_rerun()

        # Top 5 words
        if comments:
            all_words = " ".join([c["comment"] for c in comments]).lower().split()
            common_words = Counter(all_words).most_common(5)
            st.write("### 🔝 Top 5 Words Used")
            st.table(common_words)

            # Sentiment distribution
            st.write("### 📈 Sentiment Distribution")
            sentiments = [c["sentiment"] for c in comments]
            sentiment_counts = Counter(sentiments)
            fig, ax = plt.subplots()
            ax.bar(sentiment_counts.keys(), sentiment_counts.values(), color=["green", "red", "blue"])
            ax.set_title("Sentiment Distribution")
            ax.set_xlabel("Sentiment")
            ax.set_ylabel("Count")
            st.pyplot(fig)

            # Word Cloud
            st.write("### ☁️ Word Cloud")
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
                " ".join([c["comment"] for c in comments])
            )
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)


# Navigation
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio("Choose a page:", ["User", "Admin"])

if page == "User":
    user_page()
else:
    admin_page()
