import { vehicles } from '../../../data/vehicles';

export default function handler(req, res) {
  if (req.method === 'GET') {
    // Optional query parameters for filtering
    const { category, inStock, maxPrice } = req.query;

    let filteredVehicles = [...vehicles];

    // Apply filters if provided
    if (category && category !== 'All') {
      filteredVehicles = filteredVehicles.filter(v => v.category === category);
    }

    if (inStock === 'true') {
      filteredVehicles = filteredVehicles.filter(v => v.availability.inStock);
    }

    if (maxPrice) {
      filteredVehicles = filteredVehicles.filter(v => v.price <= parseInt(maxPrice));
    }

    res.status(200).json(filteredVehicles);
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
