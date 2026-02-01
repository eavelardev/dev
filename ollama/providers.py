import re

PROVIDER_RULES: list[tuple[str, list[str]]] = [
    ("OpenAI", [r"\b(?:chatgpt|gpt[-\s]*oss|gpt)\b"]),
    ("Teknium", [r"\bopenhermes[0-9a-z_-]*\b"]),
    ("Nous Research", [r"\b(?:nous(?:[-\s]*hermes)?|hermes[0-9a-z_-]*|yarn[0-9a-z._-]*)\b"]),
    ("Alibaba", [r"\b(?:qwen\d+|qwen|qwq|tongyi|codeqwen[0-9a-z_-]*)\b"]),
    ("Deep Cogito", [r"\b(?:deep\s*cogito|cogito)\b"]),
    ("Perplexity", [r"\b(?:perplexity|r1[-\s]*1776)\b"]),
    ("DeepSE", [r"\b(?:codeup)\b"]),
    ("DeepSeek", [r"\bdeepseek\b"]),
    ("Google", [r"\b(?:gemini|palm|[a-z]*gemma[0-9a-z_-]*)\b"]),
    ("IBM", [r"\b(?:granite[0-9a-z_-]*)\b"]),
    ("Open Orca", [r"\b(?:open-orca-platypus[0-9a-z._-]*|orca-mini[0-9a-z._-]*)\b"]),
    ("Tencent", [r"\b(?:llama-pro|llama-promodel)[0-9a-z._-]*\b"]),
    ("Phind", [r"\bphind[0-9a-z_-]*\b"]),
    ("FlagAlpha", [r"\bllama2-chinese[0-9a-z_-]*\b"]),
    ("Liquid", [r"\blfm[0-9a-z._-]*\b"]),
    ("Gradient", [r"\bgradient[0-9a-z_-]*\b"]),
    ("Groq", [r"\bgroq[0-9a-z_-]*\b"]),
    ("George Sung", [r"\bllama2-uncensored[0-9a-z_-]*\b"]),
    ("Bespoke Labs", [r"\bbespoke[0-9a-z_-]*\b"]),
    ("LG AI Research", [r"\bexaone[0-9a-z._-]*\b"]),
    ("Essential AI", [r"\brnj-1[0-9a-z_-]*\b"]),
    ("Siraj Raval", [r"\bmedllama[0-9a-z_-]*\b"]),
    ("MelodysDreamj", [r"\bwizard-vicuna(?!-uncensored)[0-9a-z_-]*\b"]),
    ("Eric Hartford", [r"\b(?:dolphin[0-9a-z_-]*|megadolphin[0-9a-z_-]*|tinydolphin[0-9a-z_-]*|wizard-vicuna-uncensored|samantha-mistral[0-9a-z._-]*)\b"]),
    ("WizardLM", [r"\bwizardlm[0-9a-z._-]*\b"]),
    ("SentenceTransformers", [r"\b(?:sentence[-\s]*transformers|paraphrase\s*multilingual|all[-\s]*minilm[0-9a-z._-]*)\b"]),
    ("XTuner", [r"\bllava-phi[0-9a-z._-]*\b"]),
    ("Microsoft", [r"\b(?:phi(?:[0-9][0-9a-z._-]*)?|orca(?!-mini)[0-9a-z._-]*|minilm)\b"]),
    ("Mistral", [r"\b(?:mistral|mixtral|codestral|mathstral|ministral|devstral|magistral)\b"]),
    ("Cohere", [r"\b(?:aya[0-9a-z_-]*|command[-\s]*r7b|command[-\s]*r|command[-\s]*a)\b"]),
    ("NVIDIA", [r"\b(?:nemotron|chatqa[0-9a-z_-]*)\b"]),
    ("Stability AI", [r"\b(?:stability|stable\s*lm|stable\s*beluga|stable\s*code)\b"]),
    ("Databricks", [r"\b(?:dbrx)\b"]),
    ("AllenAI", [r"\b(?:tulu(?:[-\s]*\d)?|olmo(?:[-\s]*\d)?)\b"]),
    ("BlockMerge Gradient", [r"\b(?:blockmerge(?:\s+gradient)?|codebooga)\b"]),
    ("AI21", [r"\b(?:ai21|jamba)\b"]),
    ("01.AI", [r"\b(?:01\.ai|yi)\b"]),
    ("Nomic", [r"\bnomic\b"]),
    ("MotherDuck and Numbers Station", [r"\b(?:duckdb)\b"]),
    ("Snowflake", [r"\b(?:snowflake|arctic)\b"]),
    ("BAAI", [r"\b(?:baai|bge)\b"]),
    ("Zhipu AI", [r"\b(?:codegeex|glm4|glm|chatglm)\b"]),
    ("Moonshot AI", [r"\b(?:kimi)\b"]),
    ("TII", [r"\b(?:falcon[0-9a-z_-]*)\b"]),
    ("Hugging Face", [r"\b(?:smollm)\b"]),
    ("BigCode", [r"\b(?:bigcode|starcoder)\b"]),
    ("mixedbread.ai", [r"\b(?:mixedbread|mxbai)\b"]),
    ("Cognitive Computations", [r"\b(?:dolphincoder|dolphin)\b"]),
    ("Banghua Zhu", [r"\b(?:banghua\s*zhu|starling[-\s]*lm)\b"]),
    ("InternLM", [r"\binternlm\b"]),
    ("LLaVA", [r"\bllava\b"]),
    ("Peiyuan Zhang", [r"\btinyllama[0-9a-z._-]*\b"]),
    ("Meta", [r"\b(?:[0-9a-z._-]*llama[0-9a-z._-]*)\b"]),
]


def infer_provider(text: str) -> str:
    for provider, patterns in PROVIDER_RULES:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return provider

    return "Unknown"