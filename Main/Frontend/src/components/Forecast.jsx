// Forecast.jsx
import { useState } from "react";

export default function Forecast({ nlData }) {
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(false);

  const getForecast = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/api/forecast", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nl_data: nlData }),
      });
      const data = await res.json();
      setForecast(data.forecast || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={getForecast} disabled={loading || !nlData.length}>
        {loading ? "Loading..." : "Get Budget Forecast"}
      </button>

      {forecast.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Sector/Item</th>
              <th>Forecast</th>
              <th>Allocation</th>
            </tr>
          </thead>
          <tbody>
            {forecast.map((item) => (
              <tr key={item.sector || item.item_id}>
                <td>{item.sector || item.item_id}</td>
                <td>{item.forecast}</td>
                <td>{item.allocation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
