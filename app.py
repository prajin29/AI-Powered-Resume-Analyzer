import os
import json
from typing import Optional, Dict, Any

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from tenacity import RetryError

from src.resume_extraction import extract_text_from_uploaded_file
from src.analysis import analyze_resume_structure, analyze_job_fit
from src.cohere_client import ensure_cohere_api_key_available, CohereClientError


def set_page_config() -> None:
	st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")


def get_api_key_from_sources() -> Optional[str]:
	# Prefer environment variable first
	env_key = os.getenv("COHERE_API_KEY")
	if env_key:
		return env_key
	try:
		if "COHERE_API_KEY" in st.secrets:
			return st.secrets["COHERE_API_KEY"]
	except StreamlitSecretNotFoundError:
		pass
	return None


def sidebar_controls() -> Dict[str, Any]:
	st.sidebar.header("Settings")
	existing_key = get_api_key_from_sources()

	api_key_input: Optional[str] = None
	if existing_key:
		st.sidebar.success("Server API key detected (COHERE_API_KEY). Users don't need to paste a key.")
	else:
		api_key_input = st.sidebar.text_input(
			"Cohere API Key",
			value="",
			type="password",
			help="If not provided here, the app will use the COHERE_API_KEY env var or Streamlit secrets if present.",
		)

	model = st.sidebar.selectbox(
		"Model",
		options=[
			"command-r",
			"command-r-plus",
		],
		index=0,
		help="Choose the Cohere model to use for analysis.",
	)

	temperature = st.sidebar.slider(
		"Creativity (temperature)", min_value=0.0, max_value=1.0, value=0.2, step=0.05
	)

	return {
		"api_key_input": (api_key_input.strip() if api_key_input else existing_key),
		"model": model,
		"temperature": float(temperature),
	}


def render_header() -> None:
	st.title("📄 AI-Powered Resume Analyzer")
	st.caption("Upload a resume and optionally a job description to get structured insights and tailored recommendations.")


def main() -> None:
	set_page_config()
	render_header()
	controls = sidebar_controls()

	uploaded_file = st.file_uploader("Upload resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
	job_description = st.text_area("Job description (optional)", height=200, placeholder="Paste the job description here for a tailored fit analysis...")

	if uploaded_file is None:
		st.info("Upload a resume file to begin.")
		return

	with st.spinner("Extracting text from resume..."):
		resume_text = extract_text_from_uploaded_file(uploaded_file)

	if not resume_text or len(resume_text.strip()) == 0:
		st.error("No text could be extracted from this file. If it is a scanned PDF, consider uploading a text-based version.")
		return

	with st.expander("Preview extracted text", expanded=False):
		st.text(resume_text[:5000])

	col_a, col_b = st.columns(2)
	with col_a:
		run_structure = st.button("Analyze Resume Structure", type="primary")
	with col_b:
		run_fit = st.button("Analyze Job Fit", disabled=(len(job_description.strip()) == 0))

	if run_structure or run_fit:
		try:
			ensure_cohere_api_key_available(controls["api_key_input"]) 
		except ValueError as err:
			st.error(str(err))
			return

	try:
		results: Dict[str, Any] = {}

		if run_structure:
			with st.spinner("Analyzing resume structure with Cohere..."):
				results["structure"] = analyze_resume_structure(
					resume_text=resume_text,
					model=controls["model"],
					temperature=controls["temperature"],
				)

		if run_fit and job_description.strip():
			with st.spinner("Evaluating job fit with Cohere..."):
				results["fit"] = analyze_job_fit(
					resume_text=resume_text,
					job_description=job_description,
					model=controls["model"],
					temperature=controls["temperature"],
				)

		if not results:
			return

		st.subheader("Results")

		if "structure" in results:
			st.markdown("**Structured Resume Summary**")
			st.json(results["structure"]) 

		if "fit" in results:
			fit = results["fit"]
			st.markdown("**Job Fit Analysis**")
			if isinstance(fit, dict) and "fit_score" in fit:
				st.metric(label="Fit score (0-100)", value=int(fit.get("fit_score", 0)))
			st.json(fit)

		serialized = json.dumps(results, indent=2, ensure_ascii=False)
		st.download_button("Download JSON", data=serialized, file_name="resume_analysis.json", mime="application/json")

	except CohereClientError as err:
		st.error(str(err))
	except RetryError:
		st.error("The request hit rate limits repeatedly. Please wait a minute and try again.")


if __name__ == "__main__":
	main() 