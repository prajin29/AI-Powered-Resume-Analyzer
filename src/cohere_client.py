import os
import json
from typing import Any, Dict, List

from tenacity import retry, stop_after_attempt, wait_exponential
import cohere


class CohereClientError(RuntimeError):
	pass


def ensure_cohere_api_key_available(optional_key: str | None) -> None:
	if optional_key:
		os.environ["COHERE_API_KEY"] = optional_key
	if not os.getenv("COHERE_API_KEY"):
		raise ValueError(
			"Cohere API key is required. Set COHERE_API_KEY env var, add it to Streamlit secrets, or paste it in the sidebar."
		)


def _build_client() -> cohere.Client:
	api_key = os.getenv("COHERE_API_KEY")
	if not api_key:
		raise CohereClientError("COHERE_API_KEY is not set.")
	return cohere.Client(api_key)


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3), reraise=True)
def chat_completion_json(
	messages: List[Dict[str, str]],
	model: str,
	temperature: float = 0.2,
	max_tokens: int | None = None,
) -> Dict[str, Any]:
	client = _build_client()
	# Build preamble from any system messages
	preamble_parts: List[str] = []
	user_content_parts: List[str] = []
	for m in messages:
		role = m.get("role", "user")
		content = m.get("content", "")
		if role == "system":
			preamble_parts.append(content)
		else:
			user_content_parts.append(content)
	preamble = "\n\n".join(preamble_parts) if preamble_parts else None
	user_text = "\n\n".join(user_content_parts)
	try:
		resp = client.chat(
			model=model,
			message=user_text,
			preamble=preamble,
			temperature=temperature,
		)
		# Try several response shapes depending on SDK version
		text: str | None = None
		if hasattr(resp, "text") and isinstance(resp.text, str):
			text = resp.text
		elif hasattr(resp, "message") and resp.message and hasattr(resp.message, "content"):
			parts = resp.message.content
			if parts and hasattr(parts[0], "text"):
				text = parts[0].text
		if not text and hasattr(resp, "generations") and resp.generations:
			text = resp.generations[0].text
		if not text:
			raise CohereClientError("Cohere response did not contain text content.")
		try:
			return json.loads(text)
		except json.JSONDecodeError:
			start = text.find("{")
			end = text.rfind("}")
			if start != -1 and end != -1 and end > start:
				snippet = text[start : end + 1]
				return json.loads(snippet)
			raise CohereClientError("Failed to parse JSON from model response.")
	except Exception as err:  # Fallback for various Cohere SDK errors
		message = str(err)
		if "quota" in message.lower() or "rate" in message.lower():
			raise CohereClientError("Rate limit or quota exceeded for Cohere. Check your plan/usage at https://dashboard.cohere.com.") from err
		raise CohereClientError(f"Cohere API error: {message}") from err 