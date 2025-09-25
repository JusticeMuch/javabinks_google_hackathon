import logging
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
from flask_cors import CORS  # NEW

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Enable CORS for all routes
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Base configuration
API_BASE_URL = "https://municipaldata.treasury.gov.za/api"

MUNICIPALITIES = {
    'CPT': 'City of Cape Town',
    'JHB': 'City of Johannesburg',
    'TSH': 'City of Tshwane',
    'BUF': 'Buffalo City',
    'EKU': 'Ekurhuleni',
    'ETH': 'eThekwini'
}

AMOUNT_TYPES = {
    'AUDA': 'Audited Actual',
    'ACT': 'Actual',
    'ORGB': 'Original Budget',
    'ADJB': 'Adjusted Budget'
}

class MunicipalDataAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_municipality_incexp(self, municipality_code, year, amount_type, 
                            financial_period=None, item_codes=None):
        cut_filters = [
            f'financial_year_end.year:{year}',
            f'amount_type.code:{amount_type}',
            f'demarcation.code:"{municipality_code}"'
        ]

        if financial_period:
            cut_filters.append(f'financial_period.period:{financial_period}')
            
        if item_codes:
            item_filter = ';'.join([f'"{code}"' for code in item_codes])
            cut_filters.append(f'item.code:{item_filter}')

        # ✅ add item.return_form_structure
        drilldown = (
            'demarcation.code|demarcation.label|'
            'item.code|item.label|'
            'function.code|function.label|'
            'item.return_form_structure'
        )

        params = {
            'drilldown': drilldown,
            'cut': '|'.join(cut_filters),
            'aggregates': 'amount.sum',
            'pagesize': 10000
        }

        try:
            url = f"{self.base_url}/cubes/incexp/aggregate"
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


# Initialize API client
api_client = MunicipalDataAPI(API_BASE_URL)

@app.route('/')
def index():
    current_year = datetime.now().year
    years = list(range(current_year - 1, 2008, -1))
    return render_template('index.html',
                           municipalities=MUNICIPALITIES,
                           amount_types=AMOUNT_TYPES,
                           years=years)

@app.route('/api/municipality-data', methods=['GET'])
def get_municipality_data():
    """API endpoint to fetch municipality financial data"""
    try:
        # Get query params
        municipality_code = request.args.get('municipality')
        year = int(request.args.get('year'))
        amount_type = request.args.get('amount_type')
        financial_period = request.args.get('financial_period')
        item_codes_str = request.args.get('item_codes', '').strip()

        # Parse item codes if provided
        item_codes = None
        if item_codes_str:
            item_codes = [code.strip().strip('"\'') for code in item_codes_str.split(',')]

        # Make API call
        data = api_client.get_municipality_incexp(
            municipality_code=municipality_code,
            year=year,
            amount_type=amount_type,
            financial_period=financial_period or year,  # Default to annual
            item_codes=item_codes
        )

        if 'error' in data:
            return jsonify({'error': data['error']}), 400

        # Process and format the response
        if 'cells' in data and data['cells']:
            # Add municipality name and format amounts
            for cell in data['cells']:
                cell['municipality_name'] = MUNICIPALITIES.get(municipality_code, municipality_code)
                if 'amount.sum' in cell and cell['amount.sum']:
                    cell['amount_formatted'] = f"R {cell['amount.sum']:,.2f}"

            # Sort by amount descending
            data['cells'].sort(key=lambda x: x.get('amount.sum', 0) or 0, reverse=True)

        return jsonify(data)

    except Exception as e:
        logger.exception("Unexpected error in /api/municipality-data")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask app with CORS enabled...")
    app.run(debug=True, host='0.0.0.0', port=5000)
