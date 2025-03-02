import { ObjectId } from 'mongodb';
import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  const session = await getSession({ req });
  const { db } = await connectToDatabase();
  const { id } = req.query;

  if (!ObjectId.isValid(id)) {
    return res.status(400).json({ error: 'Invalid product ID' });
  }

  const productId = new ObjectId(id);

  switch (req.method) {
    case 'GET':
      try {
        const product = await db.collection('products').findOne({ _id: productId });
        if (!product) {
          return res.status(404).json({ error: 'Product not found' });
        }
        res.status(200).json(product);
      } catch (error) {
        res.status(500).json({ error: 'Failed to fetch product' });
      }
      break;

    case 'PUT':
      if (!session || session.user.role !== 'admin') {
        return res.status(401).json({ error: 'Not authorized' });
      }

      try {
        const result = await db.collection('products').updateOne(
          { _id: productId },
          {
            $set: {
              ...req.body,
              updatedAt: new Date(),
            },
          }
        );

        if (result.matchedCount === 0) {
          return res.status(404).json({ error: 'Product not found' });
        }

        res.status(200).json({ message: 'Product updated successfully' });
      } catch (error) {
        res.status(500).json({ error: 'Failed to update product' });
      }
      break;

    case 'DELETE':
      if (!session || session.user.role !== 'admin') {
        return res.status(401).json({ error: 'Not authorized' });
      }

      try {
        const result = await db.collection('products').deleteOne({ _id: productId });
        
        if (result.deletedCount === 0) {
          return res.status(404).json({ error: 'Product not found' });
        }

        res.status(200).json({ message: 'Product deleted successfully' });
      } catch (error) {
        res.status(500).json({ error: 'Failed to delete product' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'PUT', 'DELETE']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
