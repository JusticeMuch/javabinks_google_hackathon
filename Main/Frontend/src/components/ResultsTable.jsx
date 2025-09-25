export default function ResultsTable({ data }) {
  if (!data?.cells?.length) return null;

  return (
    <table className="table table-hover mt-4">
      <thead className="table-dark">
        <tr>
          <th>Item Code</th>
          <th>Item Description</th>
          <th>Function</th>
          <th className="text-end">Amount (ZAR)</th>
        </tr>
      </thead>
      <tbody>
        {data.cells.map((cell, idx) => (
          <tr key={idx}>
            <td><code>{cell['item.code']}</code></td>
            <td>{cell['item.label']}</td>
            <td>{cell['function.label']}</td>
            <td className={`text-end ${cell['amount.sum'] >= 0 ? 'text-success' : 'text-danger'}`}>
              R {cell['amount.sum']?.toLocaleString() || '0.00'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
