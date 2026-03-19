import streamlit as st


st.set_page_config(
    page_title="Skill-Bridge Career Navigator",
    page_icon="SB",
    layout="wide",
)

# Global theming and typography
st.markdown(
    """
    <style>
    /* App-wide background tweak on top of Streamlit theme */
    .stApp {
        /* Slightly more purple, still dark and subtle */
        background: radial-gradient(circle at top, #4b2e83 0, #1f2937 40%, #05001a 100%);
    }

    /* Main title */
    h1, .stTitle {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        letter-spacing: 0.04em;
        font-weight: 800;
    }

    /* Section headers */
    h2, h3 {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 700;
    }

    /* Metrics and labels */
    .stMetric label, .stCaption, .stMarkdown p {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Skill-Bridge Career Navigator")
st.write(
    "AI-powered career intelligence for students and early-career professionals. "
    "Use the pages in the left sidebar to onboard, analyze job fit, and practice interviews."
)

st.info(
    "Start from the Home page to upload your resume and connect your GitHub profile."
)
