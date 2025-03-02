import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  const session = await getSession({ req });
  const { db } = await connectToDatabase();

  switch (req.method) {
    case 'GET':
      try {
        const products = await db.collection('products')
          .find({})
          .sort({ createdAt: -1 })
          .toArray();
        res.status(200).json(products);
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch products' });
      }
      break;

    case 'POST':
      if (!session || session.user.role !== 'admin') {
        return res.status(401).json({ error: 'Not authorized' });
      }

      try {
        const product = {
          ...req.body,
          createdAt: new Date(),
          updatedAt: new Date(),
        };
        
        const result = await db.collection('products').insertOne(product);
        res.status(201).json(result);
      } catch (error) {
        res.status(500).json({ error: 'Failed to create product' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
