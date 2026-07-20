"""
app.py
Smart Resume Analyzer — Streamlit entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

import database as db
import resume_parser
import nlp_utils
import ai_service
import pdf_generator
import visualization as viz
import automation

st.set_page_config(page_title="📊 Smart Resume Analyzer", page_icon="", layout="wide")

# --- Load custom CSS ---------------------------------------------------------
try:
    with open("static/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

db.init_db()

# --- Session state ------------------------------------------------------------
if "username" not in st.session_state:
    st.session_state.username = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_text" not in st.session_state:
    st.session_state.job_text = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# --- Sidebar: identity + navigation -------------------------------------------
with st.sidebar:
    st.title("📊 Smart Resume Analyzer")
    st.caption("Analyze • Optimize • Succeed.")

    if not st.session_state.username:
        name_input = st.text_input("Enter a username to get started")
        if st.button("Continue", use_container_width=True) and name_input.strip():
            st.session_state.username = name_input.strip()
            st.session_state.user_id = db.get_or_create_user(name_input.strip())
            st.rerun()
        st.stop()

    st.success(f"Signed in as **{st.session_state.username}**")
    page = st.radio("Navigate", ["Analyze", "AI Suggestions", "Export", "History"])

    if st.button("Sign out", use_container_width=True):
        for key in ["username", "user_id", "resume_text", "job_text", "analysis"]:
            st.session_state.pop(key, None)
        st.rerun()

user_id = st.session_state.user_id

# --- PAGE: Analyze -------------------------------------------------------------
if page == "Analyze":
    st.header("1. Upload Resume & Job Description")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Your Resume")
        uploaded = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
        if uploaded:
            try:
                st.session_state.resume_text = resume_parser.parse_resume(uploaded)
                st.success(f"Parsed {uploaded.name} ({len(st.session_state.resume_text)} characters)")
            except ValueError as e:
                st.error(str(e))
        st.session_state.resume_text = st.text_area(
            "Resume text (editable)", st.session_state.resume_text, height=250
        )

    with col2:
        st.subheader("💼 Job Description")
        job_url = st.text_input("Optional: paste a job posting URL to auto-fetch")
        if st.button("Fetch from URL") and job_url:
            with st.spinner("Fetching job posting..."):
                try:
                    st.session_state.job_text = automation.fetch_job_description_from_url(job_url)
                    st.success("Fetched job description text below — please review it.")
                except Exception as e:
                    st.error(f"Couldn't fetch that page: {e}")
        st.session_state.job_text = st.text_area(
            "Job description text (editable)", st.session_state.job_text, height=250
        )

    job_title = st.text_input("Job title (for saving)", value="Untitled Role")
    company = st.text_input("Company (optional)")

    if st.button("🔍 Analyze Match", type="primary", use_container_width=True):
        if not st.session_state.resume_text.strip() or not st.session_state.job_text.strip():
            st.warning("Please provide both a resume and a job description.")
        else:
            with st.spinner("Analyzing..."):
                score = nlp_utils.compute_match_score(
                    st.session_state.resume_text, st.session_state.job_text
                )
                gaps = nlp_utils.keyword_gap_analysis(
                    st.session_state.resume_text, st.session_state.job_text
                )
                st.session_state.analysis = {"score": score, **gaps}

                resume_id = db.save_resume(user_id, "Uploaded Resume", st.session_state.resume_text, "text")
                job_id = db.save_job_description(user_id, job_title, company, st.session_state.job_text)
                db.save_analysis(user_id, resume_id, job_id, score, gaps["matched"], gaps["missing"], {})
                st.session_state.last_resume_id = resume_id
                st.session_state.last_job_id = job_id

    if st.session_state.analysis:
        a = st.session_state.analysis
        st.divider()
        st.header("2. Results")

        c1, c2 = st.columns([1, 1])
        with c1:
            st.plotly_chart(viz.match_score_gauge(a["score"]), use_container_width=True)
        with c2:
            st.plotly_chart(
                viz.keyword_coverage_bar(len(a["matched"]), len(a["missing"])),
                use_container_width=True,
            )

        colm, colx = st.columns(2)
        with colm:
            st.subheader("✅ Matched Keywords")
            st.write(", ".join(a["matched"]) if a["matched"] else "None found")
        with colx:
            st.subheader("⚠️ Missing Keywords")
            st.write(", ".join(a["missing"]) if a["missing"] else "None — great coverage!")

# --- PAGE: AI Suggestions -------------------------------------------------------
elif page == "AI Suggestions":
    st.header("🤖 AI Analyzed Suggestions")

    if not st.session_state.analysis:
        st.info("Run an analysis on the **Analyze** page first.")
    else:
        if st.button("Generate AI Suggestions", type="primary"):
            with st.spinner("Asking Gemini for tailored suggestions..."):
                try:
                    suggestions = ai_service.generate_resume_suggestions(
                        st.session_state.resume_text,
                        st.session_state.job_text,
                        st.session_state.analysis["missing"],
                    )
                    st.session_state.ai_suggestions = suggestions
                except EnvironmentError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Gemini request failed: {e}")

        if st.session_state.get("ai_suggestions"):
            s = st.session_state.ai_suggestions
            st.subheader("Summary")
            st.write(s.get("summary", ""))

            st.subheader("Suggested Bullet Rewrites")
            for item in s.get("bullet_rewrites", []):
                with st.expander(item.get("original", "Bullet")[:80]):
                    st.markdown(f"**Original:** {item.get('original','')}")
                    st.markdown(f"**Improved:** {item.get('improved','')}")
                    st.caption(item.get("reason", ""))

            st.subheader("Keywords to Add")
            st.write(", ".join(s.get("keywords_to_add", [])))

        st.divider()
        st.subheader("✉️ Generate Cover Letter")
        tone = st.selectbox("Tone", ["professional", "enthusiastic", "concise", "conversational"])
        if st.button("Generate Cover Letter"):
            with st.spinner("Writing cover letter..."):
                try:
                    letter = ai_service.generate_cover_letter(
                        st.session_state.resume_text, st.session_state.job_text, "", tone
                    )
                    st.session_state.cover_letter = letter
                except Exception as e:
                    st.error(f"Gemini request failed: {e}")

        if st.session_state.get("cover_letter"):
            st.text_area("Cover Letter", st.session_state.cover_letter, height=300)

# --- PAGE: Export -----------------------------------------------------------------
elif page == "Export":
    st.header("📤 Export")

    doc_choice = st.radio("What do you want to export?", ["Resume (as edited)", "Cover Letter"])
    text_to_export = (
        st.session_state.resume_text if doc_choice == "Resume (as edited)"
        else st.session_state.get("cover_letter", "")
    )

    if not text_to_export.strip():
        st.info("Nothing to export yet — generate content first.")
    else:
        fmt = st.radio("Format", ["PDF", "DOCX"], horizontal=True)
        title = "Tailored Resume" if doc_choice.startswith("Resume") else "Cover Letter"

        if fmt == "PDF":
            data = pdf_generator.generate_pdf(title, text_to_export)
            st.download_button("⬇️ Download PDF", data, file_name=f"{title.replace(' ', '_')}.pdf",
                                mime="application/pdf")
        else:
            data = pdf_generator.generate_docx(title, text_to_export)
            st.download_button("⬇️ Download DOCX", data, file_name=f"{title.replace(' ', '_')}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# --- PAGE: History -----------------------------------------------------------------
elif page == "History":
    st.header("📊 Your Analysis History")

    history = db.get_user_history(user_id)
    if not history:
        st.info("No analyses yet — run one on the Analyze page.")
    else:
        trend = viz.history_trend_line(history)
        if trend:
            st.plotly_chart(trend, use_container_width=True)

        df = pd.DataFrame(history)[["created_at", "resume_title", "job_title", "company", "match_score"]]
        df.columns = ["Date", "Resume", "Job Title", "Company", "Match %"]
        st.dataframe(df, use_container_width=True)
