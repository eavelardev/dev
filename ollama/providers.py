from __future__ import annotations

import re
import html as html_lib

PROVIDER_RULES: list[tuple[str, list[str]]] = [
    ("OpenAI", [r"\b(?:openai|chatgpt|gpt[-\s]*oss|gpt)\b"]),
    ("Nous Research", [r"\b(?:nous(?:[-\s]*hermes)?|hermes)\b"]),
    ("Alibaba", [r"\b(?:alibaba|qwen\d+|qwen|qwq|tongyi)\b"]),
    ("Deep Cogito", [r"\b(?:deep\s*cogito|cogito)\b"]),
    ("Perplexity", [r"\b(?:perplexity|r1[-\s]*1776)\b"]),
    ("DeepSE", [r"\b(?:deepse|codeup)\b"]),
    ("DeepSeek", [r"\bdeepseek\b"]),
    ("Google", [r"\b(?:google|gemma|gemini|palm)\b"]),
    ("IBM", [r"\b(?:ibm|granite)\b"]),
    ("Meta", [r"\b(?:meta|llama)\b"]),
    ("Microsoft", [r"\b(?:microsoft|phi|orca|wizardlm|minilm)\b"]),
    ("Mistral", [r"\b(?:mistral|mixtral|codestral|mathstral|ministral|devstral|magistral)\b"]),
    ("Cohere", [r"\b(?:cohere|command[-\s]*r7b|command[-\s]*r|command[-\s]*a)\b"]),
    ("NVIDIA", [r"\b(?:nvidia|nemotron)\b"]),
    ("Stability AI", [r"\b(?:stability|stable\s*lm|stable\s*beluga|stable\s*code)\b"]),
    ("Databricks", [r"\b(?:databricks|dbrx)\b"]),
    ("AllenAI", [r"\b(?:tulu(?:[-\s]*\d)?|olmo(?:[-\s]*\d)?)\b"]),
    ("BlockMerge Gradient", [r"\b(?:blockmerge(?:\s+gradient)?|codebooga)\b"]),
    ("AI21", [r"\b(?:ai21|jamba)\b"]),
    ("01.AI", [r"\b(?:01\.ai|yi)\b"]),
    ("Nomic", [r"\bnomic\b"]),
    ("MotherDuck and Numbers Station", [r"\b(?:duckdb|motherduck|numbers\s*station)\b"]),
    ("Snowflake", [r"\b(?:snowflake|arctic)\b"]),
    ("BAAI", [r"\b(?:baai|bge)\b"]),
    ("Zhipu AI", [r"\b(?:zhipu|codegeex|glm4|glm|chatglm)\b"]),
    ("Moonshot AI", [r"\b(?:moonshot|kimi)\b"]),
    ("TII", [r"\b(?:tii|falcon)\b"]),
    ("Hugging Face", [r"\b(?:hugging\s*face|smollm)\b"]),
    ("BigCode", [r"\b(?:bigcode|starcoder)\b"]),
    ("mixedbread.ai", [r"\b(?:mixedbread|mxbai)\b"]),
    ("SentenceTransformers", [r"\b(?:sentence[-\s]*transformers|paraphrase\s*multilingual|all[-\s]*minilm)\b"]),
    ("Cognitive Computations", [r"\b(?:dolphincoder|dolphin)\b"]),
    ("Banghua Zhu", [r"\b(?:banghua\s*zhu|starling[-\s]*lm)\b"]),
    ("InternLM", [r"\binternlm\b"]),
    ("LLaVA", [r"\bllava\b"]),
]


def _clean_text(text: str) -> str:
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _match_provider(text: str) -> str:
    for provider, patterns in PROVIDER_RULES:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return provider
    return ""


def _extract_provider_by_phrase(text: str) -> str:
    if not text:
        return ""
    by_match = re.search(r"\bby\s+([A-Za-z0-9][A-Za-z0-9 .&-]{1,60})", text, re.IGNORECASE)
    if not by_match:
        return ""
    raw = by_match.group(1)
    raw = re.sub(r"\s+", " ", raw).strip().strip(".:-")
    return raw


def _extract_readme_text(page_html: str) -> str:
    display_idx = page_html.find('id="display"')
    if display_idx == -1:
        return ""
    start_idx = page_html.rfind("<", 0, display_idx)
    if start_idx == -1:
        start_idx = display_idx
    end_idx = page_html.find('id="editorContainer"', display_idx)
    if end_idx == -1:
        end_idx = page_html.find("</div>", display_idx)
        if end_idx == -1:
            end_idx = len(page_html)
    snippet = page_html[start_idx:end_idx]
    snippet = re.sub(r"<script[\s\S]*?</script>", " ", snippet, flags=re.IGNORECASE)
    snippet = re.sub(r"<style[\s\S]*?</style>", " ", snippet, flags=re.IGNORECASE)
    snippet = re.sub(r"<[^>]+>", " ", snippet)
    return _clean_text(snippet)


def infer_provider(model_name: str, description: str, page_html: str) -> str:
    provider = _match_provider(model_name)
    if provider:
        return provider

    primary_text = _clean_text(description)
    provider = _match_provider(primary_text)
    if provider:
        return provider

    provider = _extract_provider_by_phrase(primary_text)
    if provider:
        return provider

    readme_text = _extract_readme_text(page_html)
    if readme_text:
        provider = _match_provider(readme_text)
        if provider:
            return provider

    return ""
