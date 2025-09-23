import streamlit as st
from collections import Counter, defaultdict

# -------------------------
# Simple sentiment analyzer
# -------------------------
positive_words = {"good", "great", "excellent", "amazing", "love", "nice", "positive", "happy", "wonderful"}
negative_words = {"bad", "terrible", "awful", "hate", "poor", "negative", "sad", "angry", "worst"}

def analyze_sentiment(text):
    text = text.lower().split()
    pos = sum(1 for w in text if w in positive_words)
    neg = sum(1 for w in text if w in negative_words)

    if pos > neg:
        return "Positive"
    elif neg > pos:
        return "Negative"
    else:
        return "Neutral"


# -------------------------
# Initialize session state
# -------------------------
if "proposal_pdf" not in st.session_state:
    st.session_state["proposal_pdf"] = None
    st.session_state["proposal_name"] = None
if "comments" not in st.session_state:
    st.session_state["comments"] = []  # {name, comment, sentiment, date}
if "day" not in st.session_state:
    st.session_state["day"] = 1
if "month" not in st.session_state:
    st.session_state["month"] = 1
if "year" not in st.session_state:
    st.session_state["year"] = 2025


# -------------------------
# Helper to simulate dates
# -------------------------
def get_next_date():
    d, m, y = st.session_state["day"], st.session_state["month"], st.session_state["year"]
    # Save current date
    date_str = f"{d:02d}-{m:02d}-{y}"
    # Increment date
    d += 1
    if d > 30:  # simulate 30 days per month
        d = 1
        m += 1
    if m > 12:  # simulate 12 months per year
        m = 1
        y += 1
    # Update state
    st.session_state["day"], st.session_state["month"], st.session_state["year"] = d, m, y
    return date_str


# -------------------------
# Admin Page
# -------------------------
def admin_page():
    st.title("🛠️ Admin Page")
    password = st.text_input("Enter Admin Password", type="password")
    if password != "admin123":
        st.warning("🔒 Enter the correct password to access admin features.")
        return

    uploaded_file = st.file_uploader("📄 Upload Proposal (PDF)", type="pdf")
    if uploaded_file:
        st.session_state["proposal_pdf"] = uploaded_file.read()
        st.session_state["proposal_name"] = uploaded_file.name
        st.success("✅ PDF Proposal uploaded successfully!")

    st.subheader("📊 Comments Analysis")
    comments = st.session_state["comments"]

    if not comments:
        st.info("No comments yet.")
    else:
        # Show all comments
        for i, c in enumerate(comments):
            st.markdown(
                f"**{c['name']}** ({c['date']}): {c['comment']} _(Sentiment: {c['sentiment']})_"
            )
            if st.button(f"🗑️ Delete Comment {i+1}", key=f"del_{i}"):
                st.session_state["comments"].pop(i)
                st.rerun()

        # Top 5 words
        all_words = " ".join([c["comment"] for c in comments]).lower().split()
        common_words = Counter(all_words).most_common(5)
        st.write("### 🔝 Top 5 Words Used")
        for word, count in common_words:
            st.write(f"{word}: {count}")

        # Sentiment distribution
        st.write("### 📈 Sentiment Distribution")
        sentiments = [c["sentiment"] for c in comments]
        sentiment_counts = Counter(sentiments)
        st.bar_chart({"Sentiment": list(sentiment_counts.values())}, x=None)

        # Timeline by date
        st.write("### 📅 Timeline of Comments (Daily)")
        timeline = defaultdict(lambda: {"Positive": 0, "Negative": 0, "Neutral": 0})
        for c in comments:
            timeline[c["date"]][c["sentiment"]] += 1

        days = list(timeline.keys())
        pos = [timeline[d]["Positive"] for d in days]
        neg = [timeline[d]["Negative"] for d in days]
        neu = [timeline[d]["Neutral"] for d in days]
        st.line_chart({"Positive": pos, "Negative": neg, "Neutral": neu})

        # Monthly aggregation
        st.write("### 🗓️ Timeline of Comments (Monthly)")
        monthly = defaultdict(lambda: {"Positive": 0, "Negative": 0, "Neutral": 0})
        for c in comments:
            # Extract month-year from date string
            _, m, y = c["date"].split("-")
            key = f"{m}-{y}"
            monthly[key][c["sentiment"]] += 1

        months = list(monthly.keys())
        mpos = [monthly[m]["Positive"] for m in months]
        mneg = [monthly[m]["Negative"] for m in months]
        mneu = [monthly[m]["Neutral"] for m in months]
        st.line_chart({"Positive": mpos, "Negative": mneg, "Neutral": mneu})

        # Monthly aggregation (fixed)
st.write("### 🗓️ Timeline of Comments (Monthly)")
monthly = defaultdict(lambda: {"Positive": 0, "Negative": 0, "Neutral": 0})
for c in comments:
    d, m, y = c["date"].split("-")  # correct unpacking
    key = f"{m}-{y}"                # month-year key
    monthly[key][c["sentiment"]] += 1

months = list(monthly.keys())
mpos = [monthly[m]["Positive"] for m in months]
mneg = [monthly[m]["Negative"] for m in months]
mneu = [monthly[m]["Neutral"] for m in months]

st.line_chart({
    "Positive": mpos,
    "Negative": mneg,
    "Neutral": mneu
})



# -------------------------
# User Page
# -------------------------
def user_page():
    st.title("👥 User Page")

    if st.session_state["proposal_pdf"]:
        st.subheader("📄 Current Proposal")
        st.download_button(
            label="⬇️ Download Proposal",
            data=st.session_state["proposal_pdf"],
            file_name=st.session_state["proposal_name"],
            mime="application/pdf"
        )
    else:
        st.info("No proposal uploaded yet.")

    st.write("### 💬 Add Your Comment")
    name = st.text_input("Your Name")
    comment = st.text_area("Your Comment")

    if st.button("Submit Comment"):
        if name.strip() and comment.strip():
            sentiment = analyze_sentiment(comment)
            date_str = get_next_date()
            comment_data = {
                "name": name,
                "comment": comment,
                "sentiment": sentiment,
                "date": date_str
            }
            st.session_state["comments"].append(comment_data)
            st.success("✅ Comment submitted successfully!")
        else:
            st.error("⚠️ Please enter both name and comment.")


# -------------------------
# Navigation
# -------------------------
page = st.sidebar.radio("Navigate", ["User", "Admin"])
if page == "User":
    user_page()
else:
    admin_page()
