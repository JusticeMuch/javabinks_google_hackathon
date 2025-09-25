import React, { useState } from "react";
import QueryForm from "./components/QueryForm";
import ResultsTable from "./components/ResultsTable";
import SummaryCard from "./components/SummaryCard";
import LoadingSpinner from "./components/LoadingSpinner";
import { fetchMunicipalData } from "./api";
import "./index.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const handleQuerySubmit = async (userQuery) => {
    setLoading(true);
    setError("");
    setData(null);
    try {
      const result = await fetchMunicipalData(userQuery);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Compute summary
  const totalAmount = data?.cells?.reduce((sum, c) => sum + (c["amount.sum"] || 0) / 100, 0) || 0;
  const itemCount = data?.cells?.length || 0;
  const queryInfo = data?.cells?.[0]?.municipality_name || "";

  return (
    <div className="container py-5">
      <h1 className="mb-4 text-center">SA Municipality Financial Data Explorer</h1>
      <QueryForm onSubmit={handleQuerySubmit} />
      {loading && <LoadingSpinner />}
      {error && <div className="alert alert-danger">{error}</div>}
      {data && <SummaryCard total={totalAmount} count={itemCount} queryInfo={queryInfo} />}
      {data && <ResultsTable data={data} />}
    </div>
  );
}

export default App;
