import { vehicles } from '../../../data/vehicles';

export default function handler(req, res) {
  const { id } = req.query;

  if (req.method === 'GET') {
    const vehicle = vehicles.find(v => v.id === id);

    if (!vehicle) {
      return res.status(404).json({ message: 'Vehicle not found' });
    }

    res.status(200).json(vehicle);
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
