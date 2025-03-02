import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).end('Method Not Allowed');
  }

  try {
    const session = await getSession({ req });
    if (!session) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const { amount, currency = 'usd', orderId } = req.body;

    // Create a PaymentIntent with the order amount and currency
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency,
      metadata: {
        orderId,
        userId: session.user.id
      }
    });

    // Update order with payment intent ID
    const { db } = await connectToDatabase();
    await db.collection('orders').updateOne(
      { _id: new ObjectId(orderId) },
      {
        $set: {
          paymentIntentId: paymentIntent.id,
          updatedAt: new Date()
        }
      }
    );

    res.status(200).json({
      clientSecret: paymentIntent.client_secret
    });
  } catch (error) {
    console.error('Payment error:', error);
    res.status(500).json({ error: 'Error processing payment' });
  }
}
