import { dbConnect } from '../../../lib/mongodb';
import Vehicle from '../../../models/Vehicle';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { ids } = req.query;

  if (!ids) {
    return res.status(400).json({ error: 'Vehicle IDs are required' });
  }

  const vehicleIds = ids.split(',');

  if (vehicleIds.length < 2) {
    return res.status(400).json({ error: 'At least two vehicle IDs are required for comparison' });
  }

  if (vehicleIds.length > 3) {
    return res.status(400).json({ error: 'Maximum three vehicles can be compared at once' });
  }

  await dbConnect();

  try {
    const selectedVehicles = await Vehicle.find({ id: { $in: vehicleIds } });

  if (selectedVehicles.length !== vehicleIds.length) {
    return res.status(404).json({ error: 'One or more vehicles not found' });
  }

  // Calculate differences and highlights
  const comparison = {
    vehicles: selectedVehicles,
    differences: {
      range: findBestValue(selectedVehicles, 'specs.range', 'highest'),
      acceleration: findBestValue(selectedVehicles, 'specs.acceleration', 'lowest'),
      price: findBestValue(selectedVehicles, 'price', 'lowest'),
      batteryCapacity: findBestValue(selectedVehicles, 'specs.batteryCapacity', 'highest'),
      chargingTime: findBestValue(selectedVehicles, 'specs.chargingTime', 'lowest'),
    },
    uniqueFeatures: findUniqueFeatures(selectedVehicles),
  };

  res.status(200).json(comparison);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
}

function findBestValue(vehicles, path, criteria) {
  const values = vehicles.map(v => {
    const value = path.split('.').reduce((obj, key) => obj[key], v);
    return { id: v.id, value };
  });

  const compareFn = criteria === 'highest' 
    ? (a, b) => b.value - a.value
    : (a, b) => a.value - b.value;

  values.sort(compareFn);

  return {
    best: values[0],
    difference: values.map(v => ({
      id: v.id,
      difference: criteria === 'highest'
        ? ((v.value - values[values.length - 1].value) / values[values.length - 1].value * 100).toFixed(1)
        : ((v.value - values[0].value) / values[0].value * 100).toFixed(1)
    }))
  };
}

function findUniqueFeatures(vehicles) {
  const featureCounts = {};
  
  // Count occurrences of each feature
  vehicles.forEach(vehicle => {
    vehicle.features.forEach(feature => {
      featureCounts[feature] = (featureCounts[feature] || 0) + 1;
    });
  });

  // Find unique features for each vehicle
  return vehicles.map(vehicle => ({
    id: vehicle.id,
    unique: vehicle.features.filter(feature => featureCounts[feature] === 1)
  }));
}
