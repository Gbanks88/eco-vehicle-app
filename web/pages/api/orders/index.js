import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  const session = await getSession({ req });
  
  if (!session) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  const { db } = await connectToDatabase();

  switch (req.method) {
    case 'GET':
      try {
        const query = session.user.role === 'admin' 
          ? {} 
          : { userId: session.user.id };

        const orders = await db.collection('orders')
          .find(query)
          .sort({ createdAt: -1 })
          .toArray();

        res.status(200).json(orders);
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch orders' });
      }
      break;

    case 'POST':
      try {
        const order = {
          ...req.body,
          userId: session.user.id,
          status: 'pending',
          createdAt: new Date(),
          updatedAt: new Date(),
        };
        
        const result = await db.collection('orders').insertOne(order);
        res.status(201).json(result);
      } catch (error) {
        res.status(500).json({ error: 'Failed to create order' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
