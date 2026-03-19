from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv


GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
load_dotenv()

logger = logging.getLogger(__name__)
print("[Gemini] utils.llm_gemini module imported.")


def has_gemini_api_key() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def _extract_json_payload(text: str) -> dict[str, Any] | None:
    cleaned = (text or "").strip()
    if not cleaned:
        return None

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None
    return None


def generate_json(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> dict[str, Any] | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set; skipping Gemini LLM call.")
        print("[Gemini] GEMINI_API_KEY is not set; skipping Gemini LLM call.")
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip() or "gemini-1.5-flash"
    url = f"{GEMINI_API_BASE}/{model}:generateContent?key={api_key}"

    logger.info("Calling Gemini model '%s' via %s", model, GEMINI_API_BASE)
    print(f"[Gemini] Calling model '{model}'")

    combined_prompt = f"System:\n{system_prompt}\n\nUser:\n{user_prompt}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": combined_prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=25)
        if response.status_code != 200:
            logger.error("Gemini API returned non-200 status %s: %s", response.status_code, response.text[:300])
            print(f"[Gemini] API error {response.status_code}: {response.text[:200]}")
            return None

        # Raw body (truncated) for debugging
        raw_body = response.text
        print("[Gemini] Raw response (truncated):", raw_body[:500].replace("\n", " "))

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            logger.warning("Gemini API response contained no candidates.")
            print("[Gemini] Response contained no candidates.")
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            logger.warning("Gemini API response contained no parts.")
            print("[Gemini] Response contained no parts.")
            return None

        text = str(parts[0].get("text", ""))
        print("[Gemini] First candidate text (truncated):", text[:300].replace("\n", " "))
        parsed = _extract_json_payload(text)
        if parsed is None:
            logger.warning("Failed to parse JSON payload from Gemini response text.")
            print("[Gemini] Failed to parse JSON from response text.")
        else:
            print("[Gemini] Parsed JSON payload successfully.")
        return parsed
    except Exception as exc:
        logger.exception("Error while calling Gemini API: %s", exc)
        print(f"[Gemini] Exception while calling API: {exc}")
        return None
