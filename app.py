import streamlit as st
from collections import Counter

# -------------------------------
# Initialize session state
# -------------------------------
if "comments" not in st.session_state:
    st.session_state["comments"] = []  # list of dicts: {name, comment, sentiment}

# -------------------------------
# Simple sentiment analysis (Streamlit-native)
# -------------------------------
positive_words = ["good", "great", "excellent", "love", "happy", "nice", "awesome", "like"]
negative_words = ["bad", "poor", "terrible", "hate", "sad", "worst", "dislike", "awful"]

def analyze_sentiment(text):
    """Simple keyword-based sentiment detection"""
    text = text.lower()
    pos_count = sum(text.count(word) for word in positive_words)
    neg_count = sum(text.count(word) for word in negative_words)
    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
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
        st.download_button("📥 Download PDF", uploaded_file, file_name=uploaded_file.name)
        st.info("PDF is available for download. Read it before commenting.")

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

    st.write("### All Comments")
    for i, c in enumerate(comments):
        st.markdown(f"**{c['name']}**: {c['comment']} _(Sentiment: {c['sentiment']})_")
        delete_key = f"delete_{i}"
        if delete_key not in st.session_state:
            st.session_state[delete_key] = False
        if st.button(f"🗑️ Delete Comment {i+1}", key=delete_key):
            st.session_state["comments"].pop(i)
            st.experimental_rerun()

    # Top Words
    st.write("### 🔝 Top Words Used")
    all_words = [
        word for word in " ".join([c["comment"] for c in comments]).lower().split()
        if word.isalpha()
    ]
    common_words = Counter(all_words).most_common(10)
    if common_words:
        st.table(common_words)
        st.bar_chart(dict(common_words))

    # Sentiment Distribution
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

