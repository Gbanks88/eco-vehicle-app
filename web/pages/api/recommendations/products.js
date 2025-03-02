import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';

async function getPersonalizedRecommendations(db, userId) {
  // Get user's purchase history
  const userOrders = await db.collection('orders')
    .find({ userId, status: 'paid' })
    .toArray();

  const purchasedProductIds = userOrders.map(order => order.productId);

  // Get products similar to what user has purchased
  const recommendations = await db.collection('products')
    .find({
      _id: { $nin: purchasedProductIds },
      category: {
        $in: await db.collection('products')
          .distinct('category', { _id: { $in: purchasedProductIds } })
      }
    })
    .sort({ rating: -1 })
    .limit(5)
    .toArray();

  return recommendations;
}

async function getPopularProducts(db) {
  return await db.collection('products')
    .find()
    .sort({ viewCount: -1, rating: -1 })
    .limit(5)
    .toArray();
}

async function getSimilarProducts(db, productId) {
  const product = await db.collection('products').findOne({
    _id: new ObjectId(productId)
  });

  if (!product) {
    return [];
  }

  return await db.collection('products')
    .find({
      _id: { $ne: product._id },
      category: product.category,
      price: {
        $gte: product.price * 0.7,
        $lte: product.price * 1.3
      }
    })
    .sort({ rating: -1 })
    .limit(5)
    .toArray();
}

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).end('Method Not Allowed');
  }

  try {
    const session = await getSession({ req });
    const { db } = await connectToDatabase();
    const { productId } = req.query;

    let recommendations;

    if (productId) {
      // Get similar products for a specific product
      recommendations = await getSimilarProducts(db, productId);
    } else if (session?.user?.id) {
      // Get personalized recommendations for logged-in user
      recommendations = await getPersonalizedRecommendations(db, session.user.id);
    } else {
      // Get popular products for anonymous users
      recommendations = await getPopularProducts(db);
    }

    res.status(200).json(recommendations);
  } catch (error) {
    console.error('Recommendations error:', error);
    res.status(500).json({ error: 'Failed to fetch recommendations' });
  }
}
