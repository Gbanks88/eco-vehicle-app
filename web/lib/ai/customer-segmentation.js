import { connectToDatabase } from '../mongodb';
import { analyzeUserBehavior } from './user-behavior';

export async function segmentCustomers(options = {}) {
  const { db } = await connectToDatabase();

  try {
    // Get all users with activity in the last 90 days
    const activeUsers = await getActiveUsers(db);
    
    // Analyze each user's behavior
    const userAnalytics = await Promise.all(
      activeUsers.map(user => analyzeUserBehavior(user._id, '90d'))
    );

    // Generate segments
    const segments = await generateSegments(activeUsers, userAnalytics);

    // Calculate segment metrics
    const segmentMetrics = calculateSegmentMetrics(segments);

    // Store segmentation results
    await db.collection('customer_segments').insertOne({
      timestamp: new Date(),
      segments: segmentMetrics,
      totalCustomers: activeUsers.length
    });

    return {
      segments: segmentMetrics,
      recommendations: generateSegmentRecommendations(segmentMetrics)
    };
  } catch (error) {
    console.error('Error segmenting customers:', error);
    return null;
  }
}

async function getActiveUsers(db) {
  const ninetyDaysAgo = new Date();
  ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);

  return await db.collection('users').find({
    lastActivity: { $gte: ninetyDaysAgo }
  }).toArray();
}

async function generateSegments(users, analytics) {
  const segments = {
    // Value-based segments
    high_value: [],
    mid_value: [],
    low_value: [],

    // Engagement-based segments
    highly_engaged: [],
    moderately_engaged: [],
    at_risk: [],

    // Behavior-based segments
    new_customers: [],
    regular_customers: [],
    loyal_customers: [],

    // Interest-based segments
    eco_conscious: [],
    tech_enthusiasts: [],
    luxury_seekers: [],
    budget_conscious: [],

    // Purchase frequency segments
    frequent_buyers: [],
    occasional_buyers: [],
    one_time_buyers: [],

    // Lifecycle segments
    prospects: [],
    first_time: [],
    growing: [],
    mature: [],
    declining: [],
    inactive: []
  };

  users.forEach((user, index) => {
    const analysis = analytics[index];
    if (!analysis) return;

    // Value segmentation
    if (analysis.purchaseBehavior.avgOrderValue > 1000) {
      segments.high_value.push(user._id);
    } else if (analysis.purchaseBehavior.avgOrderValue > 500) {
      segments.mid_value.push(user._id);
    } else {
      segments.low_value.push(user._id);
    }

    // Engagement segmentation
    if (analysis.engagement.activityFrequency > 3) {
      segments.highly_engaged.push(user._id);
    } else if (analysis.engagement.activityFrequency > 1) {
      segments.moderately_engaged.push(user._id);
    } else {
      segments.at_risk.push(user._id);
    }

    // Behavior segmentation
    const daysSinceFirst = (new Date() - new Date(user.createdAt)) / (24 * 60 * 60 * 1000);
    if (daysSinceFirst < 30) {
      segments.new_customers.push(user._id);
    } else if (analysis.purchaseBehavior.purchaseFrequency > 0.1) {
      segments.loyal_customers.push(user._id);
    } else {
      segments.regular_customers.push(user._id);
    }

    // Interest segmentation
    const interests = determineInterests(analysis);
    interests.forEach(interest => {
      if (segments[interest]) {
        segments[interest].push(user._id);
      }
    });

    // Purchase frequency segmentation
    if (analysis.purchaseBehavior.purchaseFrequency > 0.2) {
      segments.frequent_buyers.push(user._id);
    } else if (analysis.purchaseBehavior.purchaseFrequency > 0.05) {
      segments.occasional_buyers.push(user._id);
    } else {
      segments.one_time_buyers.push(user._id);
    }

    // Lifecycle segmentation
    const lifecycle = determineLifecycleStage(analysis, daysSinceFirst);
    segments[lifecycle].push(user._id);
  });

  return segments;
}

function determineInterests(analysis) {
  const interests = [];

  // Check browsing patterns
  analysis.browsingPatterns.topCategories.forEach(([category, views]) => {
    if (category.includes('eco') || category.includes('environmental')) {
      interests.push('eco_conscious');
    }
    if (category.includes('tech') || category.includes('innovation')) {
      interests.push('tech_enthusiasts');
    }
    if (category.includes('luxury') || category.includes('premium')) {
      interests.push('luxury_seekers');
    }
  });

  // Check purchase behavior
  if (analysis.purchaseBehavior.preferredPriceRanges.budget > 0.5) {
    interests.push('budget_conscious');
  }

  return [...new Set(interests)];
}

function determineLifecycleStage(analysis, daysSinceFirst) {
  const { engagement, purchaseBehavior } = analysis;

  if (daysSinceFirst < 1) return 'prospects';
  if (daysSinceFirst < 30) return 'first_time';

  const engagementTrend = calculateEngagementTrend(engagement);
  const purchaseTrend = calculatePurchaseTrend(purchaseBehavior);

  if (engagementTrend > 0.1 && purchaseTrend > 0.1) return 'growing';
  if (engagementTrend > -0.1 && purchaseTrend > -0.1) return 'mature';
  if (engagementTrend < -0.1 || purchaseTrend < -0.1) return 'declining';
  return 'inactive';
}

function calculateSegmentMetrics(segments) {
  const metrics = {};

  for (const [segment, users] of Object.entries(segments)) {
    metrics[segment] = {
      size: users.length,
      percentageOfTotal: 0,
      averageValue: 0,
      retentionRate: 0,
      growthRate: 0
    };
  }

  return metrics;
}

function generateSegmentRecommendations(metrics) {
  const recommendations = [];

  // High-value customer recommendations
  if (metrics.high_value.size > 0) {
    recommendations.push({
      segment: 'high_value',
      actions: [
        'Implement VIP program',
        'Provide early access to new products',
        'Offer exclusive events and services'
      ]
    });
  }

  // At-risk customer recommendations
  if (metrics.at_risk.size > 0) {
    recommendations.push({
      segment: 'at_risk',
      actions: [
        'Launch re-engagement campaign',
        'Offer personalized discounts',
        'Conduct satisfaction survey'
      ]
    });
  }

  // New customer recommendations
  if (metrics.new_customers.size > 0) {
    recommendations.push({
      segment: 'new_customers',
      actions: [
        'Send welcome series emails',
        'Provide onboarding assistance',
        'Offer first-purchase discount'
      ]
    });
  }

  return recommendations;
}

// Helper functions
function calculateEngagementTrend(engagement) {
  const { activityFrequency, featureAdoption } = engagement;
  return featureAdoption.reduce((sum, feature) => sum + feature.usageRate, 0) / featureAdoption.length;
}

function calculatePurchaseTrend(purchaseBehavior) {
  const { purchaseFrequency, avgOrderValue } = purchaseBehavior;
  return (purchaseFrequency * avgOrderValue) / 1000; // Normalized score
}

export async function getSegmentMembers(segmentName) {
  const { db } = await connectToDatabase();

  try {
    const latestSegmentation = await db.collection('customer_segments')
      .findOne({}, { sort: { timestamp: -1 } });

    if (!latestSegmentation || !latestSegmentation.segments[segmentName]) {
      return [];
    }

    return await db.collection('users')
      .find({ _id: { $in: latestSegmentation.segments[segmentName] } })
      .project({ email: 1, name: 1, createdAt: 1 })
      .toArray();
  } catch (error) {
    console.error('Error getting segment members:', error);
    return [];
  }
}

export async function getCustomerSegments(userId) {
  const { db } = await connectToDatabase();

  try {
    const latestSegmentation = await db.collection('customer_segments')
      .findOne({}, { sort: { timestamp: -1 } });

    if (!latestSegmentation) return [];

    return Object.entries(latestSegmentation.segments)
      .filter(([, members]) => members.includes(userId))
      .map(([segment]) => segment);
  } catch (error) {
    console.error('Error getting customer segments:', error);
    return [];
  }
}
