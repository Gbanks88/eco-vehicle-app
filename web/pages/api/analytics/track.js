import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).end('Method Not Allowed');
  }

  try {
    const session = await getSession({ req });
    const { db } = await connectToDatabase();
    
    const {
      eventType,
      eventData,
      url,
      referrer,
      userAgent
    } = req.body;

    const analyticsEvent = {
      eventType,
      eventData,
      url,
      referrer,
      userAgent,
      userId: session?.user?.id || null,
      timestamp: new Date(),
      sessionId: req.headers['x-session-id'],
      ip: req.headers['x-forwarded-for'] || req.socket.remoteAddress
    };

    await db.collection('analytics').insertOne(analyticsEvent);

    // If this is a product view, update product view count
    if (eventType === 'product_view' && eventData.productId) {
      await db.collection('products').updateOne(
        { _id: new ObjectId(eventData.productId) },
        { $inc: { viewCount: 1 } }
      );
    }

    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Analytics error:', error);
    res.status(500).json({ error: 'Failed to track analytics event' });
  }
}
