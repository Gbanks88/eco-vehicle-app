import { connectToDatabase } from '../mongodb';

export async function monitorSystemHealth() {
  const { db } = await connectToDatabase();

  try {
    const metrics = await Promise.all([
      checkDatabaseHealth(db),
      checkAPIHealth(),
      checkSystemMetrics(),
      checkAISystemsHealth(db),
      checkSecurityMetrics(db)
    ]);

    const alerts = generateAlerts(metrics);
    await storeMetrics(db, metrics);
    await processAlerts(alerts);

    return {
      status: alerts.length === 0 ? 'healthy' : 'warning',
      metrics,
      alerts
    };
  } catch (error) {
    console.error('Error monitoring system health:', error);
    await logError(db, error);
    return {
      status: 'error',
      error: error.message
    };
  }
}

async function checkDatabaseHealth(db) {
  const metrics = {
    type: 'database',
    timestamp: new Date(),
    checks: {}
  };

  // Check connection status
  try {
    await db.admin().ping();
    metrics.checks.connection = 'ok';
  } catch (error) {
    metrics.checks.connection = 'failed';
  }

  // Check collection stats
  const collections = [
    'users', 'products', 'orders', 'experiments',
    'customer_segments', 'user_activity'
  ];

  for (const collection of collections) {
    try {
      const stats = await db.collection(collection).stats();
      metrics.checks[collection] = {
        size: stats.size,
        count: stats.count,
        avgObjSize: stats.avgObjSize
      };
    } catch (error) {
      metrics.checks[collection] = 'error';
    }
  }

  // Check index usage
  metrics.checks.indexes = await db.command({ serverStatus: 1 })
    .then(status => status.metrics.queryExecutor.scanned);

  return metrics;
}

async function checkAPIHealth() {
  const endpoints = [
    '/api/analytics',
    '/api/recommendations',
    '/api/search',
    '/api/inventory'
  ];

  const metrics = {
    type: 'api',
    timestamp: new Date(),
    endpoints: {}
  };

  for (const endpoint of endpoints) {
    try {
      const start = Date.now();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`);
      const duration = Date.now() - start;

      metrics.endpoints[endpoint] = {
        status: response.status,
        duration,
        healthy: response.status === 200 && duration < 1000
      };
    } catch (error) {
      metrics.endpoints[endpoint] = {
        status: 'error',
        error: error.message,
        healthy: false
      };
    }
  }

  return metrics;
}

async function checkSystemMetrics() {
  const metrics = {
    type: 'system',
    timestamp: new Date(),
    metrics: {}
  };

  // Memory usage
  const memory = process.memoryUsage();
  metrics.metrics.memory = {
    heapUsed: memory.heapUsed,
    heapTotal: memory.heapTotal,
    external: memory.external,
    healthy: memory.heapUsed / memory.heapTotal < 0.9
  };

  // CPU usage
  const cpuUsage = process.cpuUsage();
  metrics.metrics.cpu = {
    user: cpuUsage.user,
    system: cpuUsage.system,
    healthy: true // Add proper threshold
  };

  // Event loop lag
  const start = Date.now();
  await new Promise(resolve => setTimeout(resolve, 0));
  const lag = Date.now() - start;
  metrics.metrics.eventLoop = {
    lag,
    healthy: lag < 100
  };

  return metrics;
}

async function checkAISystemsHealth(db) {
  const metrics = {
    type: 'ai_systems',
    timestamp: new Date(),
    systems: {}
  };

  // Check recommendation system
  metrics.systems.recommendations = await checkRecommendationSystem(db);

  // Check price optimization
  metrics.systems.pricing = await checkPricingSystem(db);

  // Check inventory prediction
  metrics.systems.inventory = await checkInventorySystem(db);

  // Check customer segmentation
  metrics.systems.segmentation = await checkSegmentationSystem(db);

  return metrics;
}

async function checkSecurityMetrics(db) {
  const metrics = {
    type: 'security',
    timestamp: new Date(),
    metrics: {}
  };

  // Check failed login attempts
  const failedLogins = await db.collection('security_events')
    .countDocuments({
      type: 'login_failed',
      timestamp: {
        $gte: new Date(Date.now() - 24 * 60 * 60 * 1000)
      }
    });

  metrics.metrics.failedLogins = {
    count: failedLogins,
    healthy: failedLogins < 100
  };

  // Check API rate limiting
  const rateLimitEvents = await db.collection('security_events')
    .countDocuments({
      type: 'rate_limit_exceeded',
      timestamp: {
        $gte: new Date(Date.now() - 24 * 60 * 60 * 1000)
      }
    });

  metrics.metrics.rateLimiting = {
    count: rateLimitEvents,
    healthy: rateLimitEvents < 1000
  };

  // Check suspicious activities
  const suspiciousActivities = await db.collection('security_events')
    .countDocuments({
      type: 'suspicious_activity',
      timestamp: {
        $gte: new Date(Date.now() - 24 * 60 * 60 * 1000)
      }
    });

  metrics.metrics.suspiciousActivities = {
    count: suspiciousActivities,
    healthy: suspiciousActivities < 10
  };

  return metrics;
}

function generateAlerts(metrics) {
  const alerts = [];

  // Process database metrics
  if (metrics[0].checks.connection === 'failed') {
    alerts.push({
      level: 'critical',
      type: 'database',
      message: 'Database connection failed'
    });
  }

  // Process API metrics
  for (const [endpoint, data] of Object.entries(metrics[1].endpoints)) {
    if (!data.healthy) {
      alerts.push({
        level: 'high',
        type: 'api',
        message: `API endpoint ${endpoint} is unhealthy: ${data.status}`
      });
    }
  }

  // Process system metrics
  const systemMetrics = metrics[2].metrics;
  if (!systemMetrics.memory.healthy) {
    alerts.push({
      level: 'high',
      type: 'system',
      message: 'High memory usage detected'
    });
  }
  if (systemMetrics.eventLoop.lag > 100) {
    alerts.push({
      level: 'medium',
      type: 'system',
      message: 'Event loop lag detected'
    });
  }

  // Process security metrics
  const securityMetrics = metrics[4].metrics;
  if (!securityMetrics.failedLogins.healthy) {
    alerts.push({
      level: 'high',
      type: 'security',
      message: 'High number of failed login attempts detected'
    });
  }
  if (!securityMetrics.suspiciousActivities.healthy) {
    alerts.push({
      level: 'critical',
      type: 'security',
      message: 'Suspicious activities detected'
    });
  }

  return alerts;
}

async function processAlerts(alerts) {
  for (const alert of alerts) {
    // Log alert
    console.error('Alert:', alert);

    // Send notifications based on alert level
    switch (alert.level) {
      case 'critical':
        await sendEmergencyNotification(alert);
        break;
      case 'high':
        await sendHighPriorityNotification(alert);
        break;
      case 'medium':
        await sendNotification(alert);
        break;
      default:
        await logAlert(alert);
    }
  }
}

// Helper functions for checking AI systems
async function checkRecommendationSystem(db) {
  const lastDay = new Date(Date.now() - 24 * 60 * 60 * 1000);
  
  const metrics = {
    recommendations: await db.collection('recommendation_logs')
      .countDocuments({ timestamp: { $gte: lastDay } }),
    accuracy: await calculateRecommendationAccuracy(db),
    latency: await measureRecommendationLatency(db)
  };

  return {
    ...metrics,
    healthy: metrics.recommendations > 0 && metrics.accuracy > 0.7 && metrics.latency < 500
  };
}

async function checkPricingSystem(db) {
  const lastDay = new Date(Date.now() - 24 * 60 * 60 * 1000);
  
  const metrics = {
    optimizations: await db.collection('price_optimization_logs')
      .countDocuments({ timestamp: { $gte: lastDay } }),
    accuracy: await calculatePricingAccuracy(db),
    latency: await measurePricingLatency(db)
  };

  return {
    ...metrics,
    healthy: metrics.optimizations > 0 && metrics.accuracy > 0.8 && metrics.latency < 1000
  };
}

async function checkInventorySystem(db) {
  const lastDay = new Date(Date.now() - 24 * 60 * 60 * 1000);
  
  const metrics = {
    predictions: await db.collection('inventory_predictions')
      .countDocuments({ timestamp: { $gte: lastDay } }),
    accuracy: await calculateInventoryAccuracy(db),
    latency: await measureInventoryLatency(db)
  };

  return {
    ...metrics,
    healthy: metrics.predictions > 0 && metrics.accuracy > 0.8 && metrics.latency < 1000
  };
}

async function checkSegmentationSystem(db) {
  const lastDay = new Date(Date.now() - 24 * 60 * 60 * 1000);
  
  const metrics = {
    segments: await db.collection('customer_segments')
      .countDocuments({ timestamp: { $gte: lastDay } }),
    coverage: await calculateSegmentationCoverage(db),
    latency: await measureSegmentationLatency(db)
  };

  return {
    ...metrics,
    healthy: metrics.segments > 0 && metrics.coverage > 0.9 && metrics.latency < 2000
  };
}

// Notification functions
async function sendEmergencyNotification(alert) {
  // Implement emergency notification (e.g., SMS, phone call)
  console.error('EMERGENCY:', alert);
}

async function sendHighPriorityNotification(alert) {
  // Implement high priority notification (e.g., Slack, email)
  console.error('HIGH PRIORITY:', alert);
}

async function sendNotification(alert) {
  // Implement standard notification (e.g., email)
  console.log('NOTIFICATION:', alert);
}

async function logAlert(alert) {
  // Log alert to monitoring system
  console.log('ALERT:', alert);
}

// Error logging
async function logError(db, error) {
  await db.collection('error_logs').insertOne({
    timestamp: new Date(),
    error: {
      message: error.message,
      stack: error.stack
    }
  });
}

// Metrics storage
async function storeMetrics(db, metrics) {
  await db.collection('system_metrics').insertOne({
    timestamp: new Date(),
    metrics
  });
}
