"""
Shared cross-provider LLM call shapers (stdlib only, no pip).

Bongo is vendor-neutral: the cheap model and the strong model can be on DIFFERENT providers.
Used by demo/real_proof.py (the real cross-provider proof) and demo/gateway.py (the wired
"point your base_url at Bongo" path). Each function reads its key from the environment.
"""
import json
import os
import re
import urllib.request


def _post(url, headers, payload, timeout=90):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def call_mistral(prompt, model="mistral-small-latest"):
    data = _post("https://api.mistral.ai/v1/chat/completions",
                 {"Authorization": "Bearer " + os.environ["MISTRAL_API_KEY"],
                  "Content-Type": "application/json"},
                 {"model": model, "temperature": 0,
                  "messages": [{"role": "user", "content": prompt}]})
    return data["choices"][0]["message"]["content"]


def call_openai(prompt, model="gpt-4o"):
    data = _post("https://api.openai.com/v1/chat/completions",
                 {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                  "Content-Type": "application/json"},
                 {"model": model, "temperature": 0,
                  "messages": [{"role": "user", "content": prompt}]})
    return data["choices"][0]["message"]["content"]


def call_anthropic(prompt, model="claude-sonnet-4-5"):
    data = _post("https://api.anthropic.com/v1/messages",
                 {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                  "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                 {"model": model, "max_tokens": 1024,
                  "messages": [{"role": "user", "content": prompt}]})
    return "".join(b.get("text", "") for b in data["content"])


PROVIDERS = {"mistral": call_mistral, "openai": call_openai, "anthropic": call_anthropic}


def have_key(provider):
    return bool(os.environ.get({"mistral": "MISTRAL_API_KEY", "openai": "OPENAI_API_KEY",
                                "anthropic": "ANTHROPIC_API_KEY"}[provider]))


def generate(provider, prompt, model=None):
    """Provider-agnostic generation. provider in {'mistral','openai','anthropic'}."""
    fn = PROVIDERS[provider]
    return fn(prompt, model) if model else fn(prompt)


def extract_code(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()
