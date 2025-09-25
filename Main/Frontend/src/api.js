import axios from 'axios';

export const fetchMunicipalityData = async (params) => {
  try {
    const response = await axios.get('http://localhost:5000/api/municipality-data', {
      params
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: error.message };
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
