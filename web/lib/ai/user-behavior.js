import { connectToDatabase } from '../mongodb';

export async function analyzeUserBehavior(userId, timeframe = '30d') {
  const { db } = await connectToDatabase();

  try {
    // Calculate date range
    const timeframes = {
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000,
      '90d': 90 * 24 * 60 * 60 * 1000
    };
    
    const startDate = new Date(Date.now() - (timeframes[timeframe] || timeframes['30d']));

    // Gather user activities
    const activities = await db.collection('user_activity').find({
      userId,
      timestamp: { $gte: startDate }
    }).toArray();

    // Analyze browsing patterns
    const browsingPatterns = analyzeBrowsingPatterns(activities);

    // Analyze purchase behavior
    const purchaseBehavior = await analyzePurchaseBehavior(db, userId, startDate);

    // Analyze search patterns
    const searchPatterns = analyzeSearchPatterns(activities);

    // Calculate engagement metrics
    const engagement = calculateEngagementMetrics(activities);

    // Generate user segments
    const segments = await generateUserSegments(db, userId, {
      browsingPatterns,
      purchaseBehavior,
      searchPatterns,
      engagement
    });

    // Store analysis results
    await db.collection('user_behavior_analysis').insertOne({
      userId,
      timestamp: new Date(),
      timeframe,
      browsingPatterns,
      purchaseBehavior,
      searchPatterns,
      engagement,
      segments
    });

    return {
      browsingPatterns,
      purchaseBehavior,
      searchPatterns,
      engagement,
      segments
    };
  } catch (error) {
    console.error('Error analyzing user behavior:', error);
    return null;
  }
}

function analyzeBrowsingPatterns(activities) {
  const pageViews = activities.filter(a => a.type === 'pageview');
  
  // Analyze most viewed categories
  const categoryViews = pageViews.reduce((acc, view) => {
    if (view.category) {
      acc[view.category] = (acc[view.category] || 0) + 1;
    }
    return acc;
  }, {});

  // Calculate average session duration
  const sessions = groupIntoSessions(pageViews);
  const avgSessionDuration = sessions.reduce((sum, session) => 
    sum + (session.endTime - session.startTime), 0) / sessions.length;

  // Analyze peak activity times
  const activityByHour = new Array(24).fill(0);
  pageViews.forEach(view => {
    const hour = new Date(view.timestamp).getHours();
    activityByHour[hour]++;
  });

  return {
    topCategories: Object.entries(categoryViews)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5),
    avgSessionDuration,
    peakActivityHours: activityByHour
      .map((count, hour) => ({ hour, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 3)
      .map(({ hour }) => hour)
  };
}

async function analyzePurchaseBehavior(db, userId, startDate) {
  const orders = await db.collection('orders').find({
    userId,
    createdAt: { $gte: startDate }
  }).toArray();

  // Calculate purchase frequency
  const purchaseFrequency = orders.length / 30; // Orders per day

  // Calculate average order value
  const totalValue = orders.reduce((sum, order) => sum + order.total, 0);
  const avgOrderValue = orders.length > 0 ? totalValue / orders.length : 0;

  // Analyze preferred price ranges
  const priceRanges = orders.reduce((acc, order) => {
    order.items.forEach(item => {
      const range = getPriceRange(item.price);
      acc[range] = (acc[range] || 0) + 1;
    });
    return acc;
  }, {});

  // Analyze purchase categories
  const categories = orders.reduce((acc, order) => {
    order.items.forEach(item => {
      if (item.category) {
        acc[item.category] = (acc[item.category] || 0) + 1;
      }
    });
    return acc;
  }, {});

  return {
    purchaseFrequency,
    avgOrderValue,
    preferredPriceRanges: priceRanges,
    preferredCategories: Object.entries(categories)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([category]) => category)
  };
}

function analyzeSearchPatterns(activities) {
  const searches = activities.filter(a => a.type === 'search');

  // Analyze search terms
  const searchTerms = searches.reduce((acc, search) => {
    const terms = search.query.toLowerCase().split(' ');
    terms.forEach(term => {
      acc[term] = (acc[term] || 0) + 1;
    });
    return acc;
  }, {});

  // Analyze filter usage
  const filterUsage = searches.reduce((acc, search) => {
    if (search.filters) {
      Object.keys(search.filters).forEach(filter => {
        acc[filter] = (acc[filter] || 0) + 1;
      });
    }
    return acc;
  }, {});

  return {
    topSearchTerms: Object.entries(searchTerms)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([term]) => term),
    popularFilters: Object.entries(filterUsage)
      .sort(([,a], [,b]) => b - a)
      .map(([filter, count]) => ({
        filter,
        usageRate: count / searches.length
      }))
  };
}

function calculateEngagementMetrics(activities) {
  const now = new Date();
  const daysSinceFirstActivity = (now - new Date(activities[0]?.timestamp || now)) / (24 * 60 * 60 * 1000);

  // Calculate activity frequency
  const activityFrequency = activities.length / daysSinceFirstActivity;

  // Calculate feature adoption
  const featureUsage = activities.reduce((acc, activity) => {
    acc[activity.type] = (acc[activity.type] || 0) + 1;
    return acc;
  }, {});

  // Calculate bounce rate
  const sessions = groupIntoSessions(activities);
  const bounceRate = sessions.filter(s => s.activities.length === 1).length / sessions.length;

  return {
    activityFrequency,
    featureAdoption: Object.entries(featureUsage).map(([feature, count]) => ({
      feature,
      usageRate: count / activities.length
    })),
    bounceRate,
    retentionScore: calculateRetentionScore(activities, daysSinceFirstActivity)
  };
}

async function generateUserSegments(db, userId, metrics) {
  const segments = [];

  // Engagement level
  if (metrics.engagement.activityFrequency > 3) {
    segments.push('highly_engaged');
  } else if (metrics.engagement.activityFrequency > 1) {
    segments.push('moderately_engaged');
  } else {
    segments.push('low_engagement');
  }

  // Purchase behavior
  if (metrics.purchaseBehavior.purchaseFrequency > 0.1) {
    segments.push('frequent_buyer');
  }
  if (metrics.purchaseBehavior.avgOrderValue > 1000) {
    segments.push('high_value_customer');
  }

  // Interest-based
  metrics.browsingPatterns.topCategories.forEach(([category]) => {
    segments.push(`interested_in_${category}`);
  });

  return segments;
}

// Helper functions
function groupIntoSessions(activities, sessionTimeout = 30 * 60 * 1000) {
  const sortedActivities = [...activities].sort((a, b) => 
    new Date(a.timestamp) - new Date(b.timestamp));

  return sortedActivities.reduce((sessions, activity) => {
    const currentTime = new Date(activity.timestamp);
    const lastSession = sessions[sessions.length - 1];

    if (!lastSession || (currentTime - lastSession.endTime) > sessionTimeout) {
      sessions.push({
        startTime: currentTime,
        endTime: currentTime,
        activities: [activity]
      });
    } else {
      lastSession.endTime = currentTime;
      lastSession.activities.push(activity);
    }
    return sessions;
  }, []);
}

function getPriceRange(price) {
  if (price < 100) return 'budget';
  if (price < 500) return 'mid_range';
  if (price < 1000) return 'premium';
  return 'luxury';
}

function calculateRetentionScore(activities, daysSinceFirstActivity) {
  if (daysSinceFirstActivity < 1) return 1;

  const activityDays = new Set(
    activities.map(a => new Date(a.timestamp).toDateString())
  ).size;

  return activityDays / daysSinceFirstActivity;
}
