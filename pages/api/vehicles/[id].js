import dbConnect from '../../../lib/mongodb';
import Vehicle from '../../../models/Vehicle';

export default async function handler(req, res) {
  const { id } = req.query;

  await dbConnect();

  try {
    if (req.method === 'GET') {
      const vehicle = await Vehicle.findOne({ id });

      if (!vehicle) {
        return res.status(404).json({ message: 'Vehicle not found' });
      }

      res.status(200).json(vehicle);
    } else if (req.method === 'DELETE') {
      const deletedVehicle = await Vehicle.findOneAndDelete({ id });

      if (!deletedVehicle) {
        return res.status(404).json({ message: 'Vehicle not found' });
      }

      res.status(200).json({ message: 'Vehicle deleted successfully' });
    } else {
      res.setHeader('Allow', ['GET', 'DELETE']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
}
