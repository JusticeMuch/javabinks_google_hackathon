// src/components/ResultsTable.js
import React from "react";

export default function ResultsTable({ data }) {
  if (!data || !data.cells || data.cells.length === 0) {
    return <p>No data found for this query.</p>;
  }

  return (
    <div className="table-responsive">
      <table className="table table-hover">
        <thead className="table-dark">
          <tr>
            <th>Item Code</th>
            <th>Item Description</th>
            <th>Function</th>
            <th className="text-end">Amount (ZAR)</th>
          </tr>
        </thead>
        <tbody>
          {data.cells.map((cell, idx) => {
            const amount = (cell["amount.sum"] || 0) / 100; // cents → rands
            const amountClass = amount >= 0 ? "text-success" : "text-danger";
            return (
              <tr key={idx}>
                <td><code>{cell["item.code"]}</code></td>
                <td>{cell["item.label"]}</td>
                <td><small className="text-muted">{cell["function.label"]}</small></td>
                <td className={`text-end ${amountClass}`}>
                  {new Intl.NumberFormat("en-ZA", { style: "currency", currency: "ZAR", minimumFractionDigits: 2 }).format(amount)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
