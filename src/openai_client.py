import os
import json
from typing import Any, Dict, List

from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI, AuthenticationError, RateLimitError


class OpenAIClientError(RuntimeError):
	pass


def ensure_openai_api_key_available(optional_key: str | None) -> None:
	if optional_key:
		os.environ["OPENAI_API_KEY"] = optional_key
	if not os.getenv("OPENAI_API_KEY"):
		raise ValueError(
			"OpenAI API key is required. Set OPENAI_API_KEY env var, add it to Streamlit secrets, or paste it in the sidebar."
		)


def _build_client() -> OpenAI:
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		raise OpenAIClientError("OPENAI_API_KEY is not set.")
	return OpenAI(api_key=api_key)


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3), reraise=True)
def chat_completion_json(
	messages: List[Dict[str, str]],
	model: str,
	temperature: float = 0.2,
	max_tokens: int | None = None,
) -> Dict[str, Any]:
	client = _build_client()
	try:
		response = client.chat.completions.create(
			model=model,
			temperature=temperature,
			messages=messages,
		)
	except AuthenticationError as err:
		raise OpenAIClientError(
			"Authentication failed: your API key is invalid or revoked. Re-copy your key from https://platform.openai.com/account/api-keys and try again."
		) from err
	except RateLimitError as err:
		raise OpenAIClientError(
			"Rate limit or quota exceeded: check your usage and billing at https://platform.openai.com/usage and https://platform.openai.com/account/billing/overview."
		) from err

	content = response.choices[0].message.content or "{}"
	try:
		return json.loads(content)
	except json.JSONDecodeError:
		start = content.find("{")
		end = content.rfind("}")
		if start != -1 and end != -1 and end > start:
			snippet = content[start : end + 1]
			return json.loads(snippet)
		raise OpenAIClientError("Failed to parse JSON from model response.") 