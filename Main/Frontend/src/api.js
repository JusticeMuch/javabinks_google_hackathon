import axios from 'axios';

export const fetchMunicipalData = async (userQuery) => {
  try {
    const res = await fetch("http://localhost:5000/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_request: userQuery })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || "Failed to fetch data");
    }

    return await res.json();
  } catch (err) {
    throw err;
  }
};

export const fetchAvailableItems = async (municipality, year) => {
  try {
    const response = await axios.get('http://localhost:5000/api/available-items', {
      params: { municipality, year }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: error.message };
  }
};

export const getForecast = async (nlData) => {
  try {
    const res = await fetch("http://localhost:5000/api/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nl_data: nlData }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "Failed to get forecast");
    }

    const data = await res.json();
    return data.forecast || [];
  } catch (err) {
    throw err;
  }
};
