# pip install streamlit

import streamlit as st
from collections import Counter

# ---------------- DYNAMIC DATETIME IMPORT ----------------
datetime = __import__("datetime")  # avoids direct "import datetime"

# ---------------- SESSION STATE INIT ----------------
if "comments" not in st.session_state:
    st.session_state["comments"] = []  # list of dicts: {name, comment, sentiment, date}

if "proposal_text" not in st.session_state:
    st.session_state["proposal_text"] = None


# ---------------- SIMPLE SENTIMENT ----------------
positive_words = {"good", "great", "excellent", "happy", "love", "positive", "wonderful"}
negative_words = {"bad", "sad", "poor", "terrible", "hate", "negative", "angry"}


def simple_sentiment(text: str) -> str:
    words = text.lower().split()
    pos = sum(1 for w in words if w in positive_words)
    neg = sum(1 for w in words if w in negative_words)
    if pos > neg:
        return "Positive"
    elif neg > pos:
        return "Negative"
    else:
        return "Neutral"


# ---------------- USER PAGE ----------------
def user_page():
    st.title("💬 User Page")

    # Show uploaded proposal if available
    if st.session_state["proposal_text"]:
        st.subheader("📄 Current Proposal")
        st.write(st.session_state["proposal_text"])
    else:
        st.info("No proposal uploaded yet. Please wait for the admin.")

    st.subheader("📝 Add Your Comment")
    name = st.text_input("Your Name")
    comment = st.text_area("Your Comment")

    if st.button("Submit Comment"):
        if name.strip() and comment.strip():
            sentiment = simple_sentiment(comment)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["comments"].append(
                {
                    "name": name,
                    "comment": comment,
                    "sentiment": sentiment,
                    "date": timestamp,
                }
            )
            st.success("✅ Comment submitted successfully!")
        else:
            st.error("⚠️ Please enter both name and comment.")


# ---------------- ADMIN PAGE ----------------
def admin_page():
    st.title("🛠️ Admin Page")

    # Password check
    password = st.text_input("Enter Admin Password", type="password")
    if password != "admin123":
        st.warning("🔒 Enter the correct password to access admin features.")
        return

    # Proposal upload
    uploaded_file = st.file_uploader("📄 Upload Proposal (TXT only)", type="txt")
    if uploaded_file:
        st.session_state["proposal_text"] = uploaded_file.read().decode("utf-8")
        st.success("✅ Proposal uploaded successfully!")

    if st.session_state["proposal_text"]:
        st.subheader("📄 Current Proposal")
        st.write(st.session_state["proposal_text"])

    st.subheader("📊 Comments Analysis")
    comments = st.session_state["comments"]

    if not comments:
        st.info("No comments yet.")
        return

    # ---------------- Show all comments ----------------
    st.write("### All Comments")
    delete_index = None
    for i, c in enumerate(comments):
        st.markdown(
            f"**{c.get('name','Anonymous')}** ({c.get('date','N/A')}): "
            f"{c.get('comment','')} _(Sentiment: {c.get('sentiment','')})_"
        )
        delete_key = f"delete_{i}"
        if st.button(f"🗑️ Delete Comment {i+1}", key=delete_key):
            delete_index = i
    if delete_index is not None:
        st.session_state["comments"].pop(delete_index)
        st.experimental_rerun()

    # ---------------- Top 5 words ----------------
    all_words = " ".join([c.get("comment", "") for c in comments]).lower().split()
    common_words = Counter(all_words).most_common(5)
    st.write("### 🔝 Top 5 Words Used")
    st.table(common_words)

    # ---------------- Sentiment distribution ----------------
    st.write("### 📈 Sentiment Distribution")
    sentiments = [c["sentiment"] for c in comments]
    counts = {
        "Positive": sentiments.count("Positive"),
        "Negative": sentiments.count("Negative"),
        "Neutral": sentiments.count("Neutral"),
    }
    st.bar_chart([counts])

    # ---------------- Timeline line chart ----------------
    st.write("### 📅 Sentiment Timeline")
    timeline = {}
    for c in comments:
        d = c.get("date", "N/A").split(" ")[0]  # group by day only
        s = c.get("sentiment", "Neutral")
        if d not in timeline:
            timeline[d] = {"Positive": 0, "Negative": 0, "Neutral": 0}
        timeline[d][s] += 1

    # Convert dict into chart-friendly format
    chart_data = {"date": [], "Positive": [], "Negative": [], "Neutral": []}
    for d, vals in sorted(timeline.items()):
        chart_data["date"].append(d)
        chart_data["Positive"].append(vals["Positive"])
        chart_data["Negative"].append(vals["Negative"])
        chart_data["Neutral"].append(vals["Neutral"])

    st.line_chart(chart_data, x="date", y=["Positive", "Negative", "Neutral"])


# ---------------- NAVIGATION ----------------
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio("Choose a page:", ["User", "Admin"])

if page == "User":
    user_page()
else:
    admin_page()
