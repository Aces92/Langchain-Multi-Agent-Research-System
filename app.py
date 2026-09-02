import streamlit as st
from src.agents.agent import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Research Writer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# Custom CSS - responsive/mobile friendly
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* Main container */
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Header */
    .hero {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
    }

    .hero h1 {
        font-size: clamp(2rem, 5vw, 3.5rem);
        margin-bottom: 0.5rem;
    }

    .hero p {
        font-size: clamp(0.95rem, 2vw, 1.2rem);
        opacity: 0.75;
    }

    /* Pipeline cards */
    .step-card {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }

    .step-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }

    .step-description {
        font-size: 0.9rem;
        opacity: 0.7;
    }

    /* Report */
    .report-box {
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        min-height: 3rem;
        font-weight: 600;
    }

    /* Mobile */
    @media (max-width: 768px) {

        .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .hero {
            padding-top: 1rem;
        }

        .hero h1 {
            font-size: 2rem;
        }

        .hero p {
            font-size: 0.9rem;
        }

        .step-card {
            padding: 0.8rem;
        }

        /* Make Streamlit columns stack naturally */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🧠 AI Research Writer</h1>
        <p>
            Search the web, read reliable sources, write a report,
            and have an AI critic review it.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Topic input
# ---------------------------------------------------------

st.subheader("What do you want to research?")

topic = st.text_input(
    "Research topic",
    placeholder="e.g. The impact of AI on software development",
    label_visibility="collapsed",
)


# ---------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------

if st.button("🚀 Start Research", type="primary"):

    if not topic.strip():
        st.warning("Please enter a research topic first.")
        st.stop()

    # Progress
    progress = st.progress(0)
    status = st.empty()

    try:

        # -------------------------------------------------
        # STEP 1 - Search
        # -------------------------------------------------

        status.info("🔎 Step 1/4 — Searching for reliable information...")

        search_agent = build_search_agent()

        search_result = search_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Find recent, reliable and detailed "
                            f"information about {topic}"
                        ),
                    }
                ]
            }
        )

        search_content = search_result["messages"][-1].content

        progress.progress(25)

        with st.expander("🔎 Search Results", expanded=False):
            st.markdown(search_content)

        # -------------------------------------------------
        # STEP 2 - Reader
        # -------------------------------------------------

        status.info("📖 Step 2/4 — Reading the most relevant source...")

        reader_agent = build_reader_agent()

        reader_result = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"""
                        Based on the following search results about
                        '{topic}', pick the most relevant URL and
                        scrape it for deeper content.

                        Search Result:

                        {search_content[:800]}
                        """,
                    )
                ]
            }
        )

        scraped_content = reader_result["messages"][-1].content

        progress.progress(50)

        with st.expander("📖 Scraped Content", expanded=False):
            st.markdown(scraped_content)

        # -------------------------------------------------
        # STEP 3 - Writer
        # -------------------------------------------------

        status.info("✍️ Step 3/4 — Writing your research report...")

        research_combined = (
            f"SEARCH RESULTS:\n{search_content}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{scraped_content}"
        )

        report = writer_chain.invoke(
            {
                "topic": topic,
                "research": research_combined,
            }
        )

        progress.progress(75)

        # -------------------------------------------------
        # STEP 4 - Critic
        # -------------------------------------------------

        status.info("🧐 Step 4/4 — Reviewing the report...")

        feedback = critic_chain.invoke(
            {
                "report": report,
            }
        )

        progress.progress(100)

        status.success("✅ Research completed successfully!")

        # -------------------------------------------------
        # Final Report
        # -------------------------------------------------

        st.divider()

        st.header("📄 Final Report")

        st.markdown(
            f"""
            <div class="report-box">
            {report}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------
        # Critic
        # -------------------------------------------------

        st.divider()

        st.header("🧐 AI Critic Review")

        with st.container(border=True):
            st.markdown(feedback)

        # -------------------------------------------------
        # Sources / raw data
        # -------------------------------------------------

        st.divider()

        with st.expander("🔎 View Research Data"):
            st.markdown("### Search Results")
            st.markdown(search_content)

            st.markdown("### Scraped Content")
            st.markdown(scraped_content)

    except Exception as e:

        progress.empty()

        status.error("❌ Something went wrong.")

        st.error(
            f"""
            **Error:**

            `{str(e)}`
            """
        )