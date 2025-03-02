import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';
import { ObjectId } from 'mongodb';

export default async function handler(req, res) {
  const session = await getSession({ req });
  
  if (!session) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  if (req.method !== 'PUT') {
    res.setHeader('Allow', ['PUT']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const { subscribed } = req.body;

    if (typeof subscribed !== 'boolean') {
      return res.status(400).json({ error: 'Subscribed status must be a boolean' });
    }

    const { db } = await connectToDatabase();

    // Update newsletter preferences
    const result = await db.collection('users').updateOne(
      { _id: new ObjectId(session.user.id) },
      {
        $set: {
          newsletterSubscribed: subscribed,
          updatedAt: new Date()
        }
      }
    );

    if (result.matchedCount === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    // If user subscribed, add to newsletter list
    if (subscribed) {
      await db.collection('newsletter_subscribers').updateOne(
        { email: session.user.email },
        {
          $set: {
            email: session.user.email,
            name: session.user.name,
            userId: new ObjectId(session.user.id),
            updatedAt: new Date()
          }
        },
        { upsert: true }
      );
    } else {
      // If user unsubscribed, remove from newsletter list
      await db.collection('newsletter_subscribers').deleteOne({
        email: session.user.email
      });
    }

    res.status(200).json({ message: 'Newsletter preferences updated successfully' });
  } catch (error) {
    console.error('Newsletter preferences update error:', error);
    res.status(500).json({ error: 'Failed to update newsletter preferences' });
  }
}
