# pip install streamlit
import streamlit as st
from collections import Counter

# ---------------- DYNAMIC DATETIME IMPORT ----------------
# Use built-in import without writing "import datetime" explicitly
datetime = __import__("datetime")

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

    # Proposal upload (TXT only)
    uploaded_file = st.file_uploader("📄 Upload Proposal (TXT only)", type="txt")
    if uploaded_file:
        try:
            st.session_state["proposal_text"] = uploaded_file.read().decode("utf-8")
        except Exception:
            # fallback if already string-like
            st.session_state["proposal_text"] = uploaded_file.read()
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
        date_str = c.get("date", "N/A")
        st.markdown(
            f"**{c.get('name','Anonymous')}** ({date_str}): "
            f"{c.get('comment','')} _(Sentiment: {c.get('sentiment','')})_"
        )
        delete_key = f"delete_{i}"
        if st.button(f"🗑️ Delete Comment {i+1}", key=delete_key):
            delete_index = i

    # Delete after the loop (safe) and handle rerun gracefully
    if delete_index is not None:
        st.session_state["comments"].pop(delete_index)
        # Call experimental_rerun only if it exists in this Streamlit version
        if hasattr(st, "experimental_rerun"):
            try:
                st.experimental_rerun()
            except Exception:
                # If it still fails for some reason, just return to let Streamlit re-render
                return
        else:
            # No experimental_rerun available — return and let Streamlit re-render
            return

    # ---------------- Top 5 words ----------------
    all_words = " ".join([c.get("comment", "") for c in comments]).lower().split()
    common_words = Counter(all_words).most_common(5)
    st.write("### 🔝 Top 5 Words Used")
    st.table(common_words)

    # ---------------- Sentiment distribution ----------------
    st.write("### 📈 Sentiment Distribution")
    sentiments = [c.get("sentiment", "Neutral") for c in comments]
    counts = {
        "Positive": sentiments.count("Positive"),
        "Negative": sentiments.count("Negative"),
        "Neutral": sentiments.count("Neutral"),
    }
    st.bar_chart([counts])

    # ---------------- Timeline line chart ----------------
    st.write("### 📅 Sentiment Timeline (grouped by day)")
    timeline = {}
    for c in comments:
        # group by date part if timestamp present, else use 'N/A'
        d = c.get("date", "N/A").split(" ")[0]
        s = c.get("sentiment", "Neutral")
        if d not in timeline:
            timeline[d] = {"Positive": 0, "Negative": 0, "Neutral": 0}
        timeline[d][s] += 1

    # Prepare series for line chart (dates in chronological order)
    dates = sorted(timeline.keys())
    series = {
        "Positive": [timeline[d]["Positive"] for d in dates],
        "Negative": [timeline[d]["Negative"] for d in dates],
        "Neutral": [timeline[d]["Neutral"] for d in dates],
    }

    if dates:
        # show date labels and then plot lines (x axis will be numeric index)
        st.write("Dates:", ", ".join(dates))
        st.line_chart(series)


# ---------------- NAVIGATION ----------------
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio("Choose a page:", ["User", "Admin"])

if page == "User":
    user_page()
else:
    admin_page()
