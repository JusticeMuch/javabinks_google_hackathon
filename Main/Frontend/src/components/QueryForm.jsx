import { useState } from 'react';
import { fetchMunicipalityData } from '../api';

export default function QueryForm({ setData, setError, setFormValues }) {
  const [form, setForm] = useState({
    municipality: '',
    year: new Date().getFullYear(),
    amount_type: 'AUDA',
    financial_period: '',
    item_codes: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setFormValues(form); // pass values up for summary

    try {
      const params = { ...form };
      const data = await fetchMunicipalityData(params);
      setData(data);
    } catch (err) {
      setError(err.error || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

    {loading && (
        <div className="loading">
            <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
            </div>
            <p>Fetching municipality data...</p>
        </div>
    )}


  return (
    <form onSubmit={handleSubmit}>
      {/* Municipality select */}
      <div className="mb-3">
        <label>Municipality</label>
        <select
          className="form-select"
          name="municipality"
          value={form.municipality}
          onChange={handleChange}
          required
        >
          <option value="">Select Municipality</option>
          <option value="CPT">City of Cape Town</option>
          <option value="JHB">City of Johannesburg</option>
          <option value="TSH">City of Tshwane</option>
        </select>
      </div>

      {/* Year */}
      <div className="mb-3">
        <label>Financial Year</label>
        <input
          type="number"
          name="year"
          className="form-control"
          value={form.year}
          onChange={handleChange}
          required
        />
      </div>

      {/* Amount type */}
      <div className="mb-3">
        <label>Amount Type</label>
        <select
          name="amount_type"
          value={form.amount_type}
          className="form-select"
          onChange={handleChange}
        >
          <option value="AUDA">Audited Actual</option>
          <option value="ACT">Actual</option>
          <option value="ORGB">Original Budget</option>
          <option value="ADJB">Adjusted Budget</option>
        </select>
      </div>

      {/* Financial period */}
      <div className="mb-3">
        <label>Financial Period</label>
        <select
          name="financial_period"
          value={form.financial_period}
          className="form-select"
          onChange={handleChange}
        >
          <option value="">Annual</option>
          {[...Array(12)].map((_, i) => (
            <option key={i + 1} value={i + 1}>{i + 1}</option>
          ))}
        </select>
      </div>

      {/* Item codes */}
      <div className="mb-3">
        <label>Item Codes (optional)</label>
        <input
          name="item_codes"
          className="form-control"
          placeholder="2800,5200"
          value={form.item_codes}
          onChange={handleChange}
        />
      </div>

      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? 'Loading...' : 'Get Data'}
      </button>
    </form>
  );
}
