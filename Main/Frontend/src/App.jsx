import { useState } from 'react';
import QueryForm from './components/QueryForm';
import ResultsTable from './components/ResultsTable';
import SummaryCard from './components/SummaryCard';

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [formValues, setFormValues] = useState({}); // store form values for summary

  return (
    <div className="container py-5">
      <h1 className="mb-4 text-center">SA Municipality Financial Data Explorer</h1>

      <QueryForm 
        setData={(d) => setData(d)} 
        setError={(e) => setError(e)} 
        setFormValues={setFormValues} 
      />

      {error && <div className="alert alert-danger mt-3">{error}</div>}

      <SummaryCard data={data} form={formValues} />

      <ResultsTable data={data} />
    </div>
  );
}

export default App;
