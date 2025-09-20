import streamlit as st
from collections import Counter

# -------------------------------
# Initialize session state
# -------------------------------
if "comments" not in st.session_state:
    st.session_state["comments"] = []  # list of dicts: {name, comment, sentiment}
if "proposal_file" not in st.session_state:
    st.session_state["proposal_file"] = None  # Uploaded PDF

# -------------------------------
# Simple keyword-based sentiment
# -------------------------------
positive_words = ["good", "great", "excellent", "love", "happy", "nice", "awesome", "like"]
negative_words = ["bad", "poor", "terrible", "hate", "sad", "worst", "dislike", "awful"]

def analyze_sentiment(text):
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
# Admin Page
# -------------------------------
def admin_page():
    st.title("🛠️ Admin Page")

    # Upload proposal PDF
    uploaded_file = st.file_uploader("📄 Upload Proposal (PDF)", type="pdf", key="admin_pdf")
    if uploaded_file:
        st.session_state["proposal_file"] = uploaded_file
        st.success("✅ Proposal uploaded successfully!")

    # Comments analysis
    comments = st.session_state["comments"]
    st.subheader("📊 Comments Analysis")
    if not comments:
        st.info("No comments yet.")
        return

    # Display comments with safe deletion
    st.write("### All Comments")
    delete_index = None  # Track which comment to delete
    for i, c in enumerate(comments):
        st.markdown(f"**{c['name']}**: {c['comment']} _(Sentiment: {c['sentiment']})_")
        delete_key = f"delete_{i}"
        if st.button(f"🗑️ Delete Comment {i+1}", key=delete_key):
            delete_index = i

    if delete_index is not None:
        st.session_state["comments"].pop(delete_index)
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
# User Page
# -------------------------------
def user_page():
    st.title("💬 User Page")
    st.write("View the proposal and submit your comment:")

    # Show proposal if uploaded
    if st.session_state["proposal_file"]:
        st.download_button("📥 Download Proposal", st.session_state["proposal_file"],
                           file_name=st.session_state["proposal_file"].name)
        st.info("Read the proposal before commenting.")
    else:
        st.warning("No proposal uploaded yet. Please check back later.")

    # User comment section
    name = st.text_input("Your Name")
    comment = st.text_area("Your Comment")

    if st.button("Submit Comment"):
        if not st.session_state["proposal_file"]:
            st.error("Cannot submit comment because no proposal is available.")
            return
        if name.strip() and comment.strip():
            sentiment = analyze_sentiment(comment)
            st.session_state["comments"].append(
                {"name": name, "comment": comment, "sentiment": sentiment}
            )
            st.success("✅ Comment submitted successfully!")
        else:
            st.error("⚠️ Please enter both name and comment.")

# -------------------------------
# Navigation
# -------------------------------
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio("Choose a page:", ["User", "Admin"])

if page == "User":
    user_page()
else:
    admin_page()

