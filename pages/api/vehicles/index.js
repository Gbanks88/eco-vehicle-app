import dbConnect from '../../../lib/mongodb';
import Vehicle from '../../../models/Vehicle';

export default async function handler(req, res) {
  await dbConnect();

  if (req.method === 'GET') {
    try {
      // Build query
      const query = {};
      const { category, inStock, maxPrice, search } = req.query;

      if (category && category !== 'All') {
        query.category = category;
      }

      if (inStock === 'true') {
        query['availability.inStock'] = true;
      }

      if (maxPrice) {
        query.price = { $lte: parseInt(maxPrice) };
      }

      if (search) {
        query.$text = { $search: search };
      }

      const vehicles = await Vehicle.find(query)
        .sort({ createdAt: -1 });

      res.status(200).json(vehicles);
  } else if (req.method === 'POST') {
    try {
      const vehicle = await Vehicle.create(req.body);
      res.status(201).json(vehicle);
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  } else if (req.method === 'PUT') {
    try {
      const { id } = req.query;
      const vehicle = await Vehicle.findOneAndUpdate(
        { id },
        req.body,
        { new: true, runValidators: true }
      );
      if (!vehicle) {
        return res.status(404).json({ success: false });
      }
      res.status(200).json(vehicle);
    } catch (error) {
      res.status(400).json({ success: false, error: error.message });
    }
  } else {
    res.setHeader('Allow', ['GET', 'POST', 'PUT']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
} catch (error) {
  res.status(500).json({ success: false, error: error.message });
}
}
