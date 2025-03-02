import { connectToDatabase } from '../../../lib/mongodb';
import { getSession } from 'next-auth/react';

export default async function handler(req, res) {
  try {
    const session = await getSession({ req });
    const { db } = await connectToDatabase();

    switch (req.method) {
      case 'GET':
        const vehicles = await db.collection('vehicles')
          .find({})
          .sort({ createdAt: -1 })
          .toArray();
        
        res.status(200).json(vehicles);
        break;

      case 'POST':
        if (!session || session.user.role !== 'admin') {
          res.status(401).json({ message: 'Not authenticated!' });
          return;
        }

        const result = await db.collection('vehicles').insertOne({
          ...req.body,
          createdAt: new Date(),
        });

        res.status(201).json(result);
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
}
