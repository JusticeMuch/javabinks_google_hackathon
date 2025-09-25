from flask import Flask, request, jsonify
from flask_cors import CORS
from municpal_api_request import get_incexp_url_from_user_request, call_municipal_api  
# from  dataForForecast import
import requests

app = Flask(__name__)
CORS(app)  # enable CORS so React frontend can call API

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
