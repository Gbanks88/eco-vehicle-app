import { ObjectId } from 'mongodb';
import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  const session = await getSession({ req });
  
  if (!session) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  const { db } = await connectToDatabase();
  const { id } = req.query;

  if (!ObjectId.isValid(id)) {
    return res.status(400).json({ error: 'Invalid order ID' });
  }

  const orderId = new ObjectId(id);

  switch (req.method) {
    case 'GET':
      try {
        const order = await db.collection('orders').findOne({ _id: orderId });
        
        if (!order) {
          return res.status(404).json({ error: 'Order not found' });
        }

        // Check if user has permission to view this order
        if (session.user.role !== 'admin' && order.userId !== session.user.id) {
          return res.status(403).json({ error: 'Not authorized' });
        }

        res.status(200).json(order);
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch order' });
      }
      break;

    case 'PUT':
      try {
        const order = await db.collection('orders').findOne({ _id: orderId });
        
        if (!order) {
          return res.status(404).json({ error: 'Order not found' });
        }

        // Only admin can update order status
        if (session.user.role !== 'admin') {
          return res.status(403).json({ error: 'Not authorized' });
        }

        const result = await db.collection('orders').updateOne(
          { _id: orderId },
          {
            $set: {
              ...req.body,
              updatedAt: new Date(),
            },
          }
        );

        res.status(200).json({ message: 'Order updated successfully' });
      } catch (error) {
        res.status(500).json({ error: 'Failed to update order' });
      }
      break;

    case 'DELETE':
      if (session.user.role !== 'admin') {
        return res.status(403).json({ error: 'Not authorized' });
      }

      try {
        const result = await db.collection('orders').deleteOne({ _id: orderId });
        
        if (result.deletedCount === 0) {
          return res.status(404).json({ error: 'Order not found' });
        }

        res.status(200).json({ message: 'Order deleted successfully' });
      } catch (error) {
        res.status(500).json({ error: 'Failed to delete order' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'PUT', 'DELETE']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
