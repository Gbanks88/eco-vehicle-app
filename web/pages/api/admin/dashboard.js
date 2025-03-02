import { getSession } from 'next-auth/react';
import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  const session = await getSession({ req });
  
  if (!session || session.user.role !== 'admin') {
    return res.status(403).json({ error: 'Not authorized' });
  }

  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const { db } = await connectToDatabase();

    // Get various metrics
    const [
      totalOrders,
      recentOrders,
      totalRevenue,
      productStats,
      userStats
    ] = await Promise.all([
      // Total orders count
      db.collection('orders').countDocuments(),
      
      // Recent orders
      db.collection('orders')
        .find()
        .sort({ createdAt: -1 })
        .limit(10)
        .toArray(),
      
      // Total revenue
      db.collection('orders')
        .aggregate([
          { $match: { status: 'paid' } },
          { $group: { _id: null, total: { $sum: '$amount' } } }
        ])
        .toArray(),
      
      // Product statistics
      db.collection('products')
        .aggregate([
          {
            $lookup: {
              from: 'orders',
              localField: '_id',
              foreignField: 'productId',
              as: 'orders'
            }
          },
          {
            $project: {
              name: 1,
              totalOrders: { $size: '$orders' },
              revenue: {
                $sum: {
                  $map: {
                    input: '$orders',
                    as: 'order',
                    in: { $cond: [{ $eq: ['$$order.status', 'paid'] }, '$$order.amount', 0] }
                  }
                }
              }
            }
          }
        ])
        .toArray(),
      
      // User statistics
      db.collection('users')
        .aggregate([
          {
            $lookup: {
              from: 'orders',
              localField: '_id',
              foreignField: 'userId',
              as: 'orders'
            }
          },
          {
            $project: {
              email: 1,
              totalOrders: { $size: '$orders' },
              totalSpent: {
                $sum: {
                  $map: {
                    input: '$orders',
                    as: 'order',
                    in: { $cond: [{ $eq: ['$$order.status', 'paid'] }, '$$order.amount', 0] }
                  }
                }
              }
            }
          }
        ])
        .toArray()
    ]);

    res.status(200).json({
      totalOrders,
      recentOrders,
      totalRevenue: totalRevenue[0]?.total || 0,
      productStats,
      userStats
    });
  } catch (error) {
    console.error('Dashboard error:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard data' });
  }
}
