import { buffer } from 'micro';
import Stripe from 'stripe';
import { connectToDatabase } from '../../../lib/mongodb';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

export const config = {
  api: {
    bodyParser: false,
  },
};

async function updateOrderStatus(orderId, status) {
  const { db } = await connectToDatabase();
  await db.collection('orders').updateOne(
    { _id: new ObjectId(orderId) },
    {
      $set: {
        status,
        updatedAt: new Date(),
      },
    }
  );
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).end('Method Not Allowed');
  }

  try {
    const buf = await buffer(req);
    const sig = req.headers['stripe-signature'];

    let event;
    try {
      event = stripe.webhooks.constructEvent(buf, sig, webhookSecret);
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle the event
    switch (event.type) {
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object;
        await updateOrderStatus(paymentIntent.metadata.orderId, 'paid');
        break;
        
      case 'payment_intent.payment_failed':
        const failedPayment = event.data.object;
        await updateOrderStatus(failedPayment.metadata.orderId, 'failed');
        break;
        
      default:
        console.log(`Unhandled event type ${event.type}`);
    }

    res.json({ received: true });
  } catch (err) {
    console.error('Webhook error:', err.message);
    res.status(500).json({ error: 'Webhook handler failed' });
  }
}
