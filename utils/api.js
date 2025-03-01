const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export async function fetchVehicles(filters = {}) {
  const queryParams = new URLSearchParams();
  
  // Add filters to query params
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value);
    }
  });

  const queryString = queryParams.toString();
  const url = `${API_BASE_URL}/api/vehicles${queryString ? `?${queryString}` : ''}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch vehicles');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching vehicles:', error);
    throw error;
  }
}

export async function fetchVehicleById(id) {
  if (!id) {
    throw new Error('Vehicle ID is required');
  }

  const url = `${API_BASE_URL}/api/vehicles/${id}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Vehicle not found');
      }
      throw new Error('Failed to fetch vehicle');
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching vehicle ${id}:`, error);
    throw error;
  }
}

export async function searchVehicles(query) {
  const url = `${API_BASE_URL}/api/vehicles/search?q=${encodeURIComponent(query)}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to search vehicles');
    }
    return await response.json();
  } catch (error) {
    console.error('Error searching vehicles:', error);
    throw error;
  }
}

export async function compareVehicles(vehicleIds) {
  if (!Array.isArray(vehicleIds) || vehicleIds.length < 2) {
    throw new Error('At least two vehicle IDs are required for comparison');
  }

  const url = `${API_BASE_URL}/api/vehicles/compare?ids=${vehicleIds.join(',')}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to compare vehicles');
    }
    return await response.json();
  } catch (error) {
    console.error('Error comparing vehicles:', error);
    throw error;
  }
}
