import { connectToDatabase } from '../../../lib/mongodb';
import { segmentCustomers } from '../../../lib/ai/customer-segmentation';
import { analyzeUserBehavior } from '../../../lib/ai/user-behavior';
import { predictInventoryNeeds } from '../../../lib/ai/inventory';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { timeframe = '30d' } = req.query;
    const { db } = await connectToDatabase();

    // Calculate date range
    const endDate = new Date();
    const startDate = new Date();
    const days = parseInt(timeframe);
    startDate.setDate(startDate.getDate() - days);

    // Gather all metrics in parallel
    const [
      revenueMetrics,
      userMetrics,
      orderMetrics,
      conversionMetrics,
      segmentationData,
      productMetrics,
      activityData
    ] = await Promise.all([
      calculateRevenueMetrics(db, startDate, endDate),
      calculateUserMetrics(db, startDate, endDate),
      calculateOrderMetrics(db, startDate, endDate),
      calculateConversionMetrics(db, startDate, endDate),
      segmentCustomers(),
      calculateProductMetrics(db, startDate, endDate),
      getRecentActivity(db)
    ]);

    // Generate insights
    const insights = generateInsights({
      revenue: revenueMetrics,
      users: userMetrics,
      orders: orderMetrics,
      conversion: conversionMetrics,
      segments: segmentationData,
      products: productMetrics
    });

    // Prepare chart data
    const charts = prepareChartData({
      revenue: revenueMetrics,
      users: userMetrics,
      segments: segmentationData,
      products: productMetrics,
      conversion: conversionMetrics
    });

    res.status(200).json({
      revenue: revenueMetrics,
      users: userMetrics,
      orders: orderMetrics,
      conversion: conversionMetrics,
      charts,
      recentActivity: activityData,
      insights
    });
  } catch (error) {
    console.error('Error fetching analytics:', error);
    res.status(500).json({ message: 'Error fetching analytics' });
  }
}

async function calculateRevenueMetrics(db, startDate, endDate) {
  const pipeline = [
    {
      $match: {
        status: 'completed',
        createdAt: { $gte: startDate, $lte: endDate }
      }
    },
    {
      $group: {
        _id: {
          year: { $year: '$createdAt' },
          month: { $month: '$createdAt' },
          day: { $dayOfMonth: '$createdAt' }
        },
        total: { $sum: '$total' }
      }
    },
    { $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1 } }
  ];

  const dailyRevenue = await db.collection('orders').aggregate(pipeline).toArray();

  const total = dailyRevenue.reduce((sum, day) => sum + day.total, 0);
  const trend = calculateTrend(dailyRevenue.map(day => day.total));

  return {
    total,
    trend,
    daily: dailyRevenue
  };
}

async function calculateUserMetrics(db, startDate, endDate) {
  const activeUsers = await db.collection('users').countDocuments({
    lastActivity: { $gte: startDate }
  });

  const previousPeriodStart = new Date(startDate);
  previousPeriodStart.setDate(previousPeriodStart.getDate() - (endDate - startDate) / (24 * 60 * 60 * 1000));

  const previousActiveUsers = await db.collection('users').countDocuments({
    lastActivity: { $gte: previousPeriodStart, $lt: startDate }
  });

  const trend = ((activeUsers - previousActiveUsers) / previousActiveUsers) * 100;

  return {
    active: activeUsers,
    trend,
    new: await db.collection('users').countDocuments({
      createdAt: { $gte: startDate, $lte: endDate }
    })
  };
}

async function calculateOrderMetrics(db, startDate, endDate) {
  const orders = await db.collection('orders').find({
    createdAt: { $gte: startDate, $lte: endDate }
  }).toArray();

  const totalOrders = orders.length;
  const totalValue = orders.reduce((sum, order) => sum + order.total, 0);
  const averageValue = totalValue / totalOrders || 0;

  const previousOrders = await db.collection('orders').find({
    createdAt: { $gte: new Date(startDate.getTime() - (endDate - startDate)), $lt: startDate }
  }).toArray();

  const previousAverageValue = previousOrders.reduce((sum, order) => sum + order.total, 0) / previousOrders.length || 0;
  const trend = ((averageValue - previousAverageValue) / previousAverageValue) * 100;

  return {
    total: totalOrders,
    averageValue,
    trend
  };
}

async function calculateConversionMetrics(db, startDate, endDate) {
  const sessions = await db.collection('sessions').countDocuments({
    createdAt: { $gte: startDate, $lte: endDate }
  });

  const conversions = await db.collection('orders').countDocuments({
    createdAt: { $gte: startDate, $lte: endDate },
    status: 'completed'
  });

  const rate = sessions > 0 ? conversions / sessions : 0;

  const previousSessions = await db.collection('sessions').countDocuments({
    createdAt: { $gte: new Date(startDate.getTime() - (endDate - startDate)), $lt: startDate }
  });

  const previousConversions = await db.collection('orders').countDocuments({
    createdAt: { $gte: new Date(startDate.getTime() - (endDate - startDate)), $lt: startDate },
    status: 'completed'
  });

  const previousRate = previousSessions > 0 ? previousConversions / previousSessions : 0;
  const trend = ((rate - previousRate) / previousRate) * 100;

  return {
    rate,
    trend,
    sessions,
    conversions
  };
}

async function calculateProductMetrics(db, startDate, endDate) {
  return await db.collection('products').aggregate([
    {
      $lookup: {
        from: 'orders',
        let: { productId: '$_id' },
        pipeline: [
          {
            $match: {
              $expr: {
                $and: [
                  { $in: ['$$productId', '$items.productId'] },
                  { $gte: ['$createdAt', startDate] },
                  { $lte: ['$createdAt', endDate] }
                ]
              }
            }
          }
        ],
        as: 'orders'
      }
    },
    {
      $project: {
        name: 1,
        category: 1,
        sales: { $size: '$orders' },
        revenue: {
          $reduce: {
            input: '$orders',
            initialValue: 0,
            in: { $add: ['$$value', '$total'] }
          }
        }
      }
    },
    { $sort: { sales: -1 } },
    { $limit: 10 }
  ]).toArray();
}

async function getRecentActivity(db) {
  const activities = await db.collection('user_activity')
    .find()
    .sort({ timestamp: -1 })
    .limit(10)
    .toArray();

  return activities.map(activity => ({
    icon: getActivityIcon(activity.type),
    title: formatActivityTitle(activity),
    description: activity.description,
    time: formatRelativeTime(activity.timestamp)
  }));
}

function generateInsights(metrics) {
  const insights = [];

  // Revenue insights
  if (metrics.revenue.trend > 10) {
    insights.push({
      type: 'positive',
      title: 'Strong Revenue Growth',
      description: `Revenue has increased by ${metrics.revenue.trend.toFixed(1)}% compared to the previous period.`,
      recommendation: 'Consider expanding marketing efforts to capitalize on growth.'
    });
  }

  // User insights
  if (metrics.users.trend < 0) {
    insights.push({
      type: 'negative',
      title: 'Declining User Activity',
      description: 'User activity has decreased compared to the previous period.',
      recommendation: 'Launch a re-engagement campaign to bring users back.'
    });
  }

  // Conversion insights
  if (metrics.conversion.rate < 0.02) {
    insights.push({
      type: 'warning',
      title: 'Low Conversion Rate',
      description: 'The current conversion rate is below target.',
      recommendation: 'Review the checkout process and identify potential friction points.'
    });
  }

  return insights;
}

function prepareChartData(metrics) {
  return {
    revenue: {
      labels: metrics.revenue.daily.map(day => 
        `${day._id.month}/${day._id.day}`
      ),
      datasets: [{
        label: 'Daily Revenue',
        data: metrics.revenue.daily.map(day => day.total),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    },
    segments: {
      labels: Object.keys(metrics.segments.segments),
      datasets: [{
        data: Object.values(metrics.segments.segments).map(segment => segment.size),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF'
        ]
      }]
    },
    products: {
      labels: metrics.products.map(product => product.name),
      datasets: [{
        label: 'Sales',
        data: metrics.products.map(product => product.sales),
        backgroundColor: 'rgba(54, 162, 235, 0.5)'
      }]
    },
    funnel: {
      labels: ['Sessions', 'Product Views', 'Add to Cart', 'Checkout', 'Purchase'],
      datasets: [{
        data: [
          metrics.conversion.sessions,
          metrics.conversion.sessions * 0.7,
          metrics.conversion.sessions * 0.3,
          metrics.conversion.sessions * 0.15,
          metrics.conversion.conversions
        ],
        backgroundColor: 'rgba(75, 192, 192, 0.5)'
      }]
    }
  };
}

// Helper functions
function calculateTrend(values) {
  if (values.length < 2) return 0;
  const first = values[0];
  const last = values[values.length - 1];
  return ((last - first) / first) * 100;
}

function getActivityIcon(type) {
  const icons = {
    purchase: '💰',
    view: '👀',
    search: '🔍',
    signup: '👤'
  };
  return icons[type] || '📝';
}

function formatActivityTitle(activity) {
  const titles = {
    purchase: 'New Purchase',
    view: 'Product Viewed',
    search: 'Search Performed',
    signup: 'New User Signup'
  };
  return titles[activity.type] || 'Activity';
}

function formatRelativeTime(timestamp) {
  const diff = (new Date() - new Date(timestamp)) / 1000;
  
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}
