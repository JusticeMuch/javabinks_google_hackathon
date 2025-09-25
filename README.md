# SA Municipality Financial Data Explorer

A comprehensive web application for exploring South African municipal financial data, powered by natural language queries and AI-driven analysis.

## 🌟 Features

- **Natural Language Queries**: Ask questions about municipal spending in plain English
- **AI-Powered Data Retrieval**: Uses Google Gemini to convert natural language to API queries
- **Real-time Data**: Fetches live data from the Municipal Money API
- **Interactive Dashboard**: Clean, responsive interface with Bootstrap styling
- **Financial Forecasting**: AI-based budget allocation and forecasting capabilities
- **Multiple Municipalities**: Support for major SA municipalities (Cape Town, Johannesburg, Tshwane, etc.)

## 🏗️ Architecture

### Frontend (React + Vite)
- Modern React application with functional components and hooks
- Bootstrap for responsive UI design
- Axios for API communication
- Real-time data visualization

### Backend (Flask + Python)
- Flask REST API with CORS support
- Integration with Municipal Money API
- Google Vertex AI for natural language processing
- Smart query parsing and data transformation

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- Google Cloud Platform account with Vertex AI enabled

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sa-municipality-explorer
   ```

2. **Backend Setup**
   ```bash
   cd Main/Backend
   pip install -r requirements.txt
   ```

3. **Create `.env` file in Backend directory**
   ```env
   PROJECT_ID=your-gcp-project-id
   LOCATION=us-central1
   MODEL_NAME=gemini-2.5-flash
   ```

4. **Frontend Setup**
   ```bash
   cd Main/Frontend
   npm install
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd Main/Backend
   python app.py
   ```
   Server will run on `http://localhost:5000`

2. **Start the Frontend Development Server**
   ```bash
   cd Main/Frontend
   npm run dev
   ```
   Application will be available at `http://localhost:5173`

## 📊 Usage Examples

### Natural Language Queries
- "Total spent on infrastructure in Cape Town between 2018 and 2020"
- "Show me health spending for Johannesburg in 2022"
- "Water and sanitation budget for Tshwane from 2019 to 2023"

### Supported Municipalities
- **CPT**: City of Cape Town
- **JHB**: City of Johannesburg  
- **TSH**: City of Tshwane
- **BUF**: Buffalo City
- **EKU**: Ekurhuleni
- **ETH**: eThekwini

## 🛠️ API Endpoints

### Query Endpoint
```http
POST /api/query
Content-Type: application/json

{
  "user_request": "Total spent on infrastructure in Cape Town in 2022"
}
```

### Municipality Data Endpoint
```http
GET /api/municipality-data
?municipality=CPT
&year=2022
&amount_type=AUDA
&item_codes=2800
```

## 🧠 AI Features

### Natural Language Processing
- Converts plain English queries to structured API calls
- Intelligent item code matching based on descriptions
- Automatic year range expansion (e.g., "2018-2020" becomes individual years)
- Smart municipality name recognition

### Budget Forecasting
The `dataForForecast.py` module provides:
- Historical data analysis
- AI-powered budget predictions
- Constraint-based allocation optimization
- Sector-wise spending recommendations

## 📁 Project Structure

```
Main/
├── Frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── QueryForm.jsx
│   │   │   ├── ResultsTable.jsx
│   │   │   ├── SummaryCard.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── index.css
│   └── index.html
└── Backend/
    ├── app.py
    ├── municpal_api_request.py
    ├── dataForForecast.py
    └── requirements.txt
```

## 🔧 Configuration

### Municipal Money API Integration
The application integrates with the official Municipal Money API:
- Base URL: `https://municipaldata.treasury.gov.za/api`
- Supports INCEXP cube queries
- Real-time financial data access

### Google Vertex AI Configuration
- Uses Gemini 2.5 Flash model
- Configurable project and region settings
- Intelligent query parsing and item code matching

## 🎨 UI Components

### QueryForm
- Natural language input interface
- Real-time query submission
- Input validation and formatting

### ResultsTable
- Responsive data table with Bootstrap styling
- Currency formatting for South African Rand
- Color-coded positive/negative amounts
- Item code and description display

### SummaryCard
- Financial overview with gradient styling
- Total amounts, item counts, and query details
- Responsive card layout

## 💾 Data Sources

- **Municipal Money API**: Official SA Treasury municipal financial data
- **Real-time Updates**: Live data from government sources
- **Historical Coverage**: Multi-year financial records
- **Comprehensive Scope**: Revenue, expenditure, and budget data

## 🔒 Security & Compliance

- CORS enabled for cross-origin requests
- Environment variable protection for sensitive data
- Input validation and sanitization
- Error handling and logging

## 🚀 Deployment

### Production Considerations
- Use production WSGI server (e.g., Gunicorn) instead of Flask dev server
- Configure environment variables securely
- Set up proper CORS policies
- Implement rate limiting for API endpoints

### Environment Variables
```env
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1
MODEL_NAME=gemini-2.5-flash
FLASK_ENV=production
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at [Municipal Money](https://municipaldata.treasury.gov.za/)
- Review Google Vertex AI documentation for AI-related issues

## 🔗 Related Resources

- [Municipal Money API Documentation](https://municipaldata.treasury.gov.za/api)
- [Google Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [South African National Treasury](http://www.treasury.gov.za/)
- [React Documentation](https://reactjs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

Built with ❤️ for transparency in South African municipal finance
