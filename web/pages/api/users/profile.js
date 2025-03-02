import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';
import { ObjectId } from 'mongodb';

export default async function handler(req, res) {
  const session = await getSession({ req });
  
  if (!session) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  const { db } = await connectToDatabase();

  switch (req.method) {
    case 'GET':
      try {
        const user = await db.collection('users').findOne(
          { _id: new ObjectId(session.user.id) },
          { projection: { password: 0 } } // Exclude password from response
        );

        if (!user) {
          return res.status(404).json({ error: 'User not found' });
        }

        res.status(200).json(user);
      } catch (error) {
        console.error('Profile fetch error:', error);
        res.status(500).json({ error: 'Failed to fetch profile' });
      }
      break;

    case 'PUT':
      try {
        const { name, email } = req.body;

        // Validate input
        if (!name || !email) {
          return res.status(400).json({ error: 'Name and email are required' });
        }

        // Check if email is already taken by another user
        if (email !== session.user.email) {
          const existingUser = await db.collection('users').findOne({ email });
          if (existingUser) {
            return res.status(400).json({ error: 'Email is already taken' });
          }
        }

        // Update user profile
        const result = await db.collection('users').updateOne(
          { _id: new ObjectId(session.user.id) },
          {
            $set: {
              name,
              email,
              updatedAt: new Date()
            }
          }
        );

        if (result.matchedCount === 0) {
          return res.status(404).json({ error: 'User not found' });
        }

        res.status(200).json({ message: 'Profile updated successfully' });
      } catch (error) {
        console.error('Profile update error:', error);
        res.status(500).json({ error: 'Failed to update profile' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'PUT']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
