// src/components/SummaryCard.js
import React from "react";

export default function SummaryCard({ total, count, queryInfo }) {
  return (
    <div className="card summary-card shadow mb-4 text-center p-3">
      <h4>Financial Summary</h4>
      <div className="row">
        <div className="col-md-4">
          <h5>{new Intl.NumberFormat("en-ZA", { style: "currency", currency: "ZAR", minimumFractionDigits: 2 }).format(total)}</h5>
          <small>Total Amount</small>
        </div>
        <div className="col-md-4">
          <h5>{count}</h5>
          <small>Line Items</small>
        </div>
        <div className="col-md-4">
          <h5>{queryInfo}</h5>
          <small>Query Details</small>
        </div>
      </div>
    </div>
  );
}
