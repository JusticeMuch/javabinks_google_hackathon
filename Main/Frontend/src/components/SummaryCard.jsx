export default function SummaryCard({ data, form }) {
  if (!data?.cells?.length) return null;

  const totalAmount = data.cells.reduce((sum, cell) => sum + (cell['amount.sum'] || 0), 0);
  const itemCount = data.cells.length;
  const municipalityName = data.cells[0].municipality_name || form.municipality;

  return (
    <div className="card summary-card shadow mb-4" style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white'}}>
      <div className="card-body text-center">
        <h4 className="card-title mb-4">Financial Summary</h4>
        <div className="row">
          <div className="col-md-4">
            <h5>R {totalAmount.toLocaleString()}</h5>
            <small>Total Amount</small>
          </div>
          <div className="col-md-4">
            <h5>{itemCount}</h5>
            <small>Line Items</small>
          </div>
          <div className="col-md-4">
            <h5>{municipalityName} {form.year}</h5>
            <small>Query Details</small>
          </div>
        </div>
      </div>
    </div>
  );
}
