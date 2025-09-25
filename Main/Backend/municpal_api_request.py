import re
import json
import requests
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

# ---------------------
# CONFIG
# ---------------------
load_dotenv()  # Load environment variables from .env

BASE = "https://municipaldata.treasury.gov.za/api"
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL_NAME = os.getenv("MODEL_NAME")
DEFAULT_PAGESIZE = 20

# Init Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_NAME)

# ---------------------
# Robust system prompt (strict drilldown rule)
# ---------------------
SYSTEM_PROMPT_JSON = """
You are an API query builder for the Municipal Money API (https://municipaldata.treasury.gov.za/api).

Your task:
- Convert plain-English user requests into a structured JSON object that can be turned into a valid INCEXP cube query.
- Do not output explanations, code fences, or extra text — only the JSON object.

Rules:
1. Always output a single JSON object.
2. Allowed JSON keys:
   - endpoint: "facts" or "aggregate"
   - cuts: an array of { "dimension": "...", "value": "..." } objects
   - drilldown: MUST always be an array of dimension names, e.g. ["demarcation.code","financial_year_end.year"]
   - aggregates: optional array of aggregate measures, e.g. ["amount.sum"]
   - order: optional string, e.g. "amount.sum:desc"
   - pagesize: integer (default = 20 if not specified)

3. Dimensions you can use in cuts:
   - demarcation.code  (municipality code, e.g. "CPT", "TSH")
   - financial_year_end.year  (integer or range, e.g. 2022 or 2019;2023 for 2019 to 2023)
   - financial_period.period  (period, e.g. 2015)
   - item.code  (financial item, e.g. "0100" for operating revenue)
   - amount_type.code  (e.g. "AUDA" for audited actuals, "ORGB" for original budget)

4. Formatting rules:
   - Use exact dimension names as above.
   - Municipality codes must be uppercase (e.g. "CPT").
   - Item codes and amount_type codes must be strings, e.g. "0100", "AUDA".
   - Years may be integers (2022) or ranges (2019-2023).
   - Always wrap string values in quotes inside the JSON.
   - Do not use curly quotes, only straight quotes.

5. drilldown must NEVER be a single string with commas. It must always be a JSON array of strings.

6. Never return an API URL directly. Only return the JSON specification.

7. Always include "item.label" in the response JSON for each item, so the client can display the item description.
"""

# ---------------------
# Helpers
# ---------------------
def normalize_text(txt: str) -> str:
    replacements = {
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
        '\u2013': '-', '\u2014': '-', '\u00A0': ' ',
        '\u2012': '-', '`': '',
    }
    for k, v in replacements.items():
        txt = txt.replace(k, v)
    return txt.strip()

def extract_first_json(text: str) -> str | None:
    start = text.find('{')
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return None

def format_cut_value(val, always_quote=False, dimension=None):
    """
    Ensure proper quoting:
    - always_quote=True → wrap in quotes even if numeric
    - Do not quote if dimension is financial_year_end.year
    - Always quote for item.code
    """
    val_str = str(val).strip('"').strip("'")

    if dimension == "financial_year_end.year":
        return val_str  # Never quote years

    if dimension == "item.code":
        return f'"{val_str}"'

    if always_quote:
        return f'"{val_str}"'

    if val_str.isdigit() or "-" in val_str:
        return val_str
    return f'"{val_str}"'

def build_cut_param(cuts):
    """
    Build the cut string.
    - If multiple values for the same dimension exist, combine as dim:"val1";"val2"
    - All values in a multi-value cut are always quoted, except financial_year_end.year
    """
    parts_dict = {}

    if isinstance(cuts, list):
        for c in cuts:
            if isinstance(c, dict):
                dim = c.get("dimension")
                val = c.get("value")
                if dim and val is not None:
                    # Convert single value to list
                    if not isinstance(val, (list, tuple)):
                        # If string with semicolons or commas, split
                        if isinstance(val, str) and (';' in val or ',' in val):
                            val = [v.strip() for v in re.split(r'[;,]', val)]
                        else:
                            val = [val]
                    if dim not in parts_dict:
                        parts_dict[dim] = []
                    for v in val:
                        # Always quote if multiple values, unless financial_year_end.year
                        if len(val) > 1:
                            parts_dict[dim].append(format_cut_value(v, always_quote=True, dimension=dim))
                        else:
                            parts_dict[dim].append(format_cut_value(v, dimension=dim))

    # Join multiple values with semicolon (not inside quotes)
    parts = [f"{dim}:{';'.join(values)}" for dim, values in parts_dict.items()]
    return "|".join(parts)

def build_incexp_url(components: dict) -> str:
    """Build URL without URL encoding to prevent 500 errors."""
    endpoint = components.get("endpoint", "facts")
    path = f"/cubes/incexp/{endpoint}"
    params = {}

    cut_val = build_cut_param(components.get("cuts"))
    if cut_val:
        params["cut"] = cut_val

    if components.get("drilldown"):
        if isinstance(components["drilldown"], (list, tuple)):
            params["drilldown"] = "|".join(components["drilldown"])

    if components.get("aggregates"):
        params["aggregates"] = ",".join(components["aggregates"])

    if components.get("order"):
        params["order"] = components["order"]

    params["pagesize"] = str(components.get("pagesize", DEFAULT_PAGESIZE))

    # Manual join, no URL encoding
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{BASE}{path}?{query}"

def is_valid_incexp_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return ("/api/cubes/incexp/" in p.path) and bool(p.query)
    except Exception:
        return False

# ---------------------
# Model interaction
# ---------------------
def ask_model_for_intent(user_input: str) -> dict:
    prompt = SYSTEM_PROMPT_JSON + "\n\nUser request: " + user_input + "\n\nJSON:"
    resp = model.generate_content(prompt)
    raw = normalize_text(getattr(resp, "text", str(resp)))
    json_text = extract_first_json(raw)
    if json_text:
        try:
            return json.loads(json_text)
        except Exception:
            return {}
    return {}

def fetch_valid_item_codes():
    """
    Fetch all valid item codes from the API metadata.
    Returns a set of valid item codes as strings.
    """
    items_url = f"{BASE}/cubes/incexp/members/item"
    try:
        resp = requests.get(items_url)
        resp.raise_for_status()
        items = resp.json().get("data", [])
        return set(str(item.get("item.code", "")) for item in items)
    except Exception:
        return set()

def fetch_item_codes_by_description(description: str):
    """
    Use the item metadata endpoint to match item codes by description using LLM.
    Returns a list of unique item codes as strings.
    """
    items_url = f"{BASE}/cubes/incexp/members/item"
    try:
        resp = requests.get(items_url)
        resp.raise_for_status()
        items = resp.json().get("data", [])
        # Build a list of {code, label} for the LLM
        item_list = [
            {"code": str(item.get("item.code", "")), "label": str(item.get("item.label", ""))}
            for item in items if item.get("item.code") and item.get("item.label")
        ]
        # Prepare prompt for LLM
        prompt = (
            "Given the following item codes and their descriptions:\n"
            f"{json.dumps(item_list, ensure_ascii=False)}\n"
            f"Select all item codes relevant to this description: \"{description}\".\n"
            "Be more exclusive rather than inclusive.\n"
            "Return only a JSON array of codes, no explanation."
        )
        resp_llm = model.generate_content(prompt)
        raw = normalize_text(getattr(resp_llm, "text", str(resp_llm)))
        try:
            codes = json.loads(raw)
            if isinstance(codes, list):
                # Remove duplicates while preserving order
                seen = set()
                unique_codes = []
                for code in codes:
                    code_str = str(code)
                    if re.match(r'^\d{4}$', code_str) and code_str not in seen:
                        seen.add(code_str)
                        unique_codes.append(code_str)
                return unique_codes
        except Exception:
            pass
        # Fallback: extract 4-digit codes using regex and remove duplicates, preserving order
        seen = set()
        unique_codes = []
        for code in re.findall(r'\b\d{4}\b', raw):
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)
        return unique_codes
    except Exception:
        return []

def extract_years_from_prompt(prompt: str):
    """
    Extracts financial years from the prompt.
    Expands ranges like '2017-2020', 'between 2018 and 2020', 'from 2014 to 2019' to individual years.
    Returns a sorted list of unique years as strings.
    """
    years = set()

    # Find ranges like 2017-2020
    for rng in re.findall(r'\b(20\d{2})-(20\d{2})\b', prompt):
        start, end = map(int, rng)
        years.update(str(y) for y in range(start, end + 1))

    # Find "between 2018 and 2020" or "from 2014 to 2019"
    for rng in re.findall(r'(?:between|from)\s*(20\d{2})\s*(?:and|to)\s*(20\d{2})', prompt, re.IGNORECASE):
        start, end = map(int, rng)
        years.update(str(y) for y in range(start, end + 1))

    # Find individual years
    for y in re.findall(r'\b20\d{2}\b', prompt):
        years.add(y)

    # Ensure unique and sorted years
    years_sorted = sorted(set(int(y) for y in years))
    return [str(y) for y in years_sorted]

def get_incexp_url_from_user_request(user_request: str) -> str:
    intent = ask_model_for_intent(user_request)
    if not intent:
        raise ValueError("Model output could not be parsed into JSON.")

    cuts = intent.get("cuts", [])

    # If no item codes in cuts, try to fetch by description
    item_codes_in_prompt = fetch_item_codes_by_description(user_request)
    if item_codes_in_prompt:
        cuts.append({"dimension": "item.code", "value": item_codes_in_prompt})
        intent["cuts"] = cuts
    else:
        intent["cuts"] = [c for c in cuts if c.get("dimension") != "item.code"]

    # Always set years to those found in the prompt (replace any existing year cuts)
    years_in_prompt = extract_years_from_prompt(user_request)
    cuts = [c for c in intent["cuts"] if c.get("dimension") != "financial_year_end.year"]
    if years_in_prompt:
        cuts.append({"dimension": "financial_year_end.year", "value": years_in_prompt})
    intent["cuts"] = cuts

    url = build_incexp_url(intent)
    if not is_valid_incexp_url(url):
        raise ValueError(f"Built URL invalid: {url}")
    return url

def call_municipal_api(url: str):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        print("API Error:", e)
        print("Response content:", getattr(e.response, "text", "No content"))
        raise

# ---------------------
# Example usage
# ---------------------
if __name__ == "__main__":
    user_req = "Total spent on infrastructure in cape town between 2018 and 2020"
    
    # Generate the URL
    url = get_incexp_url_from_user_request(user_req)
    print("RAW URL (no encoding, semicolon for repeated dims, multi-values quoted except years):")
    print(url)
    
    # Optional: call the API
    data = call_municipal_api(url)
    # print(data)
    # Print item labels if present
    # if "data" in data:
    #     print("Item labels in response:")
    #     for entry in data["data"]:
    #         label = entry.get("item.label")
    #         code = entry.get("item.code")
    #         if label:
    #             print(f" - item.code: {code}, item.label: {label}")
    # print("Got keys:", list(data.keys()))
    #             print(f" - item.code: {code}, item.label: {label}")
    # print("Got keys:", list(data.keys()))
