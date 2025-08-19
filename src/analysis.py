from __future__ import annotations

from typing import Any, Dict

from .cohere_client import chat_completion_json


def analyze_resume_structure(resume_text: str, model: str, temperature: float) -> Dict[str, Any]:
	messages = [
		{
			"role": "system",
			"content": (
				"You are a helpful assistant that extracts structured data from resumes. "
				"Return a strict JSON object only."
			),
		},
		{
			"role": "user",
			"content": (
				"Extract key information from the following resume text. "
				"Return a JSON object with these top-level keys: contact, summary, skills, experience, education, certifications, projects, achievements, keywords. "
				"For each experience item include: title, company, start_date, end_date, location, responsibilities (list), achievements (list), technologies (list). "
				"If a field is unknown, use null or an empty list.\n\n"
				f"RESUME:\n{resume_text}"
			),
		},
	]
	return chat_completion_json(messages=messages, model=model, temperature=temperature)


def analyze_job_fit(resume_text: str, job_description: str, model: str, temperature: float) -> Dict[str, Any]:
	messages = [
		{
			"role": "system",
			"content": (
				"You are an expert technical recruiter and hiring manager. "
				"Compare a candidate's resume to a job description. Return a strict JSON object only."
			),
		},
		{
			"role": "user",
			"content": (
				"Compare the resume to the job description. "
				"Return JSON with keys: fit_score (0-100), key_strengths (list), missing_requirements (list), "
				"tailored_resume_tips (list), suggested_keywords (list), summary (string). "
				"Focus on measurable impact and alignment with responsibilities.\n\n"
				f"JOB DESCRIPTION:\n{job_description}\n\n"
				f"RESUME:\n{resume_text}"
			),
		},
	]
	return chat_completion_json(messages=messages, model=model, temperature=temperature) 