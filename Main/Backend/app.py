from flask import Flask, request, jsonify
from flask_cors import CORS
from municpal_api_request import get_incexp_url_from_user_request, call_municipal_api  
import  dataForForecast
import requests
import pandas as pd
from random import randint
import json
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)
CORS(app)  # enable CORS so React frontend can call API

# Vertex AI config
PROJECT_ID = "hackathon-25-09-2025"
REGION = "us-central1"
MODEL_ID = "gemini-2.5-flash"
BUDGET_TOTAL = 10_000_000_000  # example total budget in ZAR

vertexai.init(project=PROJECT_ID, location=REGION)
model = GenerativeModel(MODEL_ID)

API_BASE_URL = "https://municipaldata.treasury.gov.za/api"

MUNICIPALITIES = {
    'CPT': 'City of Cape Town',
    'JHB': 'City of Johannesburg',
    'TSH': 'City of Tshwane',
    'BUF': 'Buffalo City',
    'EKU': 'Ekurhuleni',
    'ETH': 'eThekwini'
}

@app.route("/api/query", methods=["POST"])
def query_municipal_data():
    data = request.get_json()
    user_request = data.get("user_request")
    if not user_request:
        return jsonify({"error": "user_request missing"}), 400
    try:
        # Use all your existing functions here
        url = get_incexp_url_from_user_request(user_request)
        response_data = call_municipal_api(url)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/municipality-data', methods=['GET'])
def get_municipality_data():
    municipality = request.args.get('municipality')
    year = request.args.get('year')
    amount_type = request.args.get('amount_type', 'AUDA')
    financial_period = request.args.get('financial_period') or year
    item_codes = request.args.get('item_codes')

    cut_filters = [
        f'financial_year_end.year:{year}',
        f'amount_type.code:{amount_type}',
        f'financial_period.period:{financial_period}',
        f'demarcation.code:"{municipality}"'
    ]

    if item_codes:
        item_filter = ';'.join([f'"{code.strip()}"' for code in item_codes.split(',')])
        cut_filters.append(f'item.code:{item_filter}')

    drilldown = 'demarcation.code|demarcation.label|item.code|item.label|function.code|function.label|item.return_form_structure'

    params = {
        'drilldown': drilldown,
        'cut': '|'.join(cut_filters),
        'aggregates': 'amount.sum',
        'pagesize': 10000
    }

    try:
        resp = requests.get(f"{API_BASE_URL}/cubes/incexp/aggregate", params=params)
        resp.raise_for_status()
        data = resp.json()

        # Add municipality names
        for cell in data.get('cells', []):
            cell['municipality_name'] = MUNICIPALITIES.get(municipality, municipality)
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500
    
def forecast_budget_from_nl_data(nl_data, total_budget=BUDGET_TOTAL):
    """
    nl_data: list of dicts returned from your NL model / municipal API
    total_budget: total ZAR to allocate
    """
    if not nl_data or len(nl_data) == 0:
        raise ValueError("No NL data provided for budget forecast")

    # Convert NL data into CSV-like string for prompt
    df = pd.DataFrame(nl_data)
    # Ensure at least columns: time, item_id, target (map your NL fields)
    if 'amount.sum' in df.columns:
        df = df.rename(columns={"item.label": "item_id", "amount.sum": "target"})
    if 'time' not in df.columns:
        df['time'] = pd.to_datetime("today").strftime("%Y-%m-%d")  # fallback
    
    data_str = df[['time', 'item_id', 'target']].to_csv(index=False)

    prompt = f"""
You are a municipal budget planning AI.
Here is the recent municipal financial data (time,item_id,target):

{data_str}

Based on this data, provide a forecast for the next financial year's required amounts per sector/item.
Then allocate a total budget of {total_budget} ZAR across sectors/items.
Constraints:
- Health >= 2_000_000_000
- Water >= 1_000_000_000
- Education >= 1_500_000_000

Only output your response as a raw JSON array of objects, showing sector/item, forecast, and allocation.
Do not provide code or commentary.
"""

    # Call Gemini
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.2, "max_output_tokens": 10000},
    )
    result_text = response.text

    # Parse JSON output
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from multiple lines
        lines = result_text.splitlines()
        json_text = "\n".join(lines[1:-1]) if len(lines) > 2 else result_text
        return json.loads(json_text)

from flask import request

@app.route("/api/forecast", methods=["POST"])
def forecast_endpoint():
    """
    Expects JSON payload:
    {
        "nl_data": [...]  # list of dicts from NL query
    }
    """
    try:
        data = request.get_json()
        nl_data = data.get("nl_data", [])
        allocation = forecast_budget_from_nl_data(nl_data)
        return jsonify({"forecast": allocation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
