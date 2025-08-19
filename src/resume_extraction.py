from __future__ import annotations

import io
from typing import BinaryIO

from pypdf import PdfReader
from docx import Document


def extract_text_from_uploaded_file(uploaded_file) -> str:
	file_name = getattr(uploaded_file, "name", "uploaded")
	lower_name = file_name.lower()
	if lower_name.endswith(".pdf"):
		return _extract_text_from_pdf(uploaded_file)
	if lower_name.endswith(".docx"):
		return _extract_text_from_docx(uploaded_file)
	return _extract_text_from_txt(uploaded_file)


def _extract_text_from_pdf(uploaded_file) -> str:
	binary = uploaded_file.getvalue()
	reader = PdfReader(io.BytesIO(binary))
	texts: list[str] = []
	for page in reader.pages:
		page_text = page.extract_text() or ""
		texts.append(page_text)
	return "\n".join(texts).strip()


def _extract_text_from_docx(uploaded_file) -> str:
	doc = Document(uploaded_file)
	paragraphs = [p.text for p in doc.paragraphs if p.text]
	return "\n".join(paragraphs).strip()


def _extract_text_from_txt(uploaded_file) -> str:
	binary = uploaded_file.getvalue()
	try:
		return binary.decode("utf-8")
	except UnicodeDecodeError:
		return binary.decode("latin-1", errors="ignore") 