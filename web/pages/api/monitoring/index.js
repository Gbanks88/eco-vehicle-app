import { monitorSystemHealth } from '../../../lib/monitoring';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { timeframe = '1h', system = 'all' } = req.query;
    const healthData = await monitorSystemHealth();

    // Process metrics based on timeframe
    const metrics = await processMetrics(healthData, timeframe, system);

    res.status(200).json({
      metrics,
      alerts: healthData.alerts || []
    });
  } catch (error) {
    console.error('Error in monitoring API:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

async function processMetrics(healthData, timeframe, system) {
  // Convert timeframe to milliseconds
  const timeframeMs = {
    '1h': 60 * 60 * 1000,
    '6h': 6 * 60 * 60 * 1000,
    '24h': 24 * 60 * 60 * 1000,
    '7d': 7 * 24 * 60 * 60 * 1000
  }[timeframe];

  const startTime = new Date(Date.now() - timeframeMs);

  // Filter metrics by timeframe and system
  const filteredMetrics = filterMetrics(healthData, startTime, system);

  // Generate chart data
  const charts = generateChartData(filteredMetrics, timeframe);

  return {
    system: processSystemMetrics(filteredMetrics),
    database: processDatabaseMetrics(filteredMetrics),
    api: processApiMetrics(filteredMetrics),
    security: processSecurityMetrics(filteredMetrics),
    charts
  };
}

function filterMetrics(healthData, startTime, system) {
  const metrics = { ...healthData };

  if (system !== 'all') {
    // Filter metrics for specific system
    metrics.metrics = metrics.metrics.filter(m => m.type === system);
  }

  // Filter by timeframe
  metrics.metrics = metrics.metrics.filter(m => 
    new Date(m.timestamp) >= startTime
  );

  return metrics;
}

function generateChartData(metrics, timeframe) {
  const intervals = getTimeIntervals(timeframe);
  
  return {
    systemLoad: {
      labels: intervals,
      datasets: [{
        label: 'CPU Usage',
        data: generateDataPoints(metrics, intervals, 'cpu'),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }, {
        label: 'Memory Usage',
        data: generateDataPoints(metrics, intervals, 'memory'),
        borderColor: 'rgb(153, 102, 255)',
        tension: 0.1
      }]
    },
    responseTimes: {
      labels: intervals,
      datasets: [{
        label: 'API Response Time',
        data: generateDataPoints(metrics, intervals, 'api_latency'),
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1
      }]
    },
    aiAccuracy: {
      labels: [
        'Recommendations',
        'Price Optimization',
        'Inventory Prediction',
        'Customer Segmentation',
        'Search'
      ],
      datasets: [{
        label: 'Accuracy',
        data: [
          getAverageMetric(metrics, 'recommendations_accuracy'),
          getAverageMetric(metrics, 'pricing_accuracy'),
          getAverageMetric(metrics, 'inventory_accuracy'),
          getAverageMetric(metrics, 'segmentation_accuracy'),
          getAverageMetric(metrics, 'search_accuracy')
        ],
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgb(75, 192, 192)',
        pointBackgroundColor: 'rgb(75, 192, 192)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(75, 192, 192)'
      }]
    },
    aiLatency: {
      labels: [
        'Recommendations',
        'Price Optimization',
        'Inventory Prediction',
        'Customer Segmentation',
        'Search'
      ],
      datasets: [{
        label: 'Latency (ms)',
        data: [
          getAverageMetric(metrics, 'recommendations_latency'),
          getAverageMetric(metrics, 'pricing_latency'),
          getAverageMetric(metrics, 'inventory_latency'),
          getAverageMetric(metrics, 'segmentation_latency'),
          getAverageMetric(metrics, 'search_latency')
        ],
        backgroundColor: 'rgba(153, 102, 255, 0.5)'
      }]
    }
  };
}

function getTimeIntervals(timeframe) {
  const now = new Date();
  const intervals = [];
  const intervalCount = {
    '1h': 12,  // 5-minute intervals
    '6h': 12,  // 30-minute intervals
    '24h': 24, // 1-hour intervals
    '7d': 7    // 1-day intervals
  }[timeframe];

  const intervalMs = {
    '1h': 5 * 60 * 1000,
    '6h': 30 * 60 * 1000,
    '24h': 60 * 60 * 1000,
    '7d': 24 * 60 * 60 * 1000
  }[timeframe];

  for (let i = intervalCount - 1; i >= 0; i--) {
    const time = new Date(now - i * intervalMs);
    intervals.push(formatTime(time, timeframe));
  }

  return intervals;
}

function formatTime(date, timeframe) {
  switch (timeframe) {
    case '1h':
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    case '6h':
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    case '24h':
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    case '7d':
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    default:
      return date.toLocaleString();
  }
}

function generateDataPoints(metrics, intervals, metricKey) {
  return intervals.map(interval => {
    const relevantMetrics = metrics.metrics.filter(m => 
      formatTime(new Date(m.timestamp), getTimeframeFromIntervals(intervals)) === interval
    );
    return getAverageMetric(relevantMetrics, metricKey);
  });
}

function getTimeframeFromIntervals(intervals) {
  const count = intervals.length;
  if (count <= 12) return '1h';
  if (count <= 24) return '24h';
  return '7d';
}

function getAverageMetric(metrics, key) {
  const values = metrics.metrics
    .filter(m => m[key] !== undefined)
    .map(m => m[key]);
  
  return values.length > 0
    ? values.reduce((a, b) => a + b, 0) / values.length
    : 0;
}

function processSystemMetrics(metrics) {
  const systemMetrics = metrics.metrics.filter(m => m.type === 'system');
  const latest = systemMetrics[systemMetrics.length - 1] || {};

  return {
    status: getSystemStatus(latest),
    metrics: {
      cpu: `${Math.round(latest.cpu?.usage || 0)}%`,
      memory: `${Math.round(latest.memory?.used || 0)}MB`,
      uptime: formatUptime(latest.uptime)
    }
  };
}

function processDatabaseMetrics(metrics) {
  const dbMetrics = metrics.metrics.filter(m => m.type === 'database');
  const latest = dbMetrics[dbMetrics.length - 1] || {};

  return {
    status: getDatabaseStatus(latest),
    metrics: {
      connections: latest.connections || 0,
      queryTime: `${Math.round(latest.queryTime || 0)}ms`,
      size: formatBytes(latest.size || 0)
    }
  };
}

function processApiMetrics(metrics) {
  const apiMetrics = metrics.metrics.filter(m => m.type === 'api');
  const latest = apiMetrics[apiMetrics.length - 1] || {};

  return {
    status: getApiStatus(latest),
    metrics: {
      requests: latest.requests || 0,
      responseTime: `${Math.round(latest.responseTime || 0)}ms`,
      errors: latest.errors || 0
    }
  };
}

function processSecurityMetrics(metrics) {
  const securityMetrics = metrics.metrics.filter(m => m.type === 'security');
  const latest = securityMetrics[securityMetrics.length - 1] || {};

  return {
    status: getSecurityStatus(latest),
    metrics: {
      threats: latest.threats || 0,
      failedLogins: latest.failedLogins || 0,
      suspicious: latest.suspicious || 0
    }
  };
}

// Helper functions
function getSystemStatus(metrics) {
  if (!metrics) return 'unknown';
  if (metrics.cpu?.usage > 90 || metrics.memory?.used > 90) return 'error';
  if (metrics.cpu?.usage > 70 || metrics.memory?.used > 70) return 'warning';
  return 'healthy';
}

function getDatabaseStatus(metrics) {
  if (!metrics) return 'unknown';
  if (metrics.errors > 0) return 'error';
  if (metrics.queryTime > 1000) return 'warning';
  return 'healthy';
}

function getApiStatus(metrics) {
  if (!metrics) return 'unknown';
  if (metrics.errors > 100) return 'error';
  if (metrics.responseTime > 1000) return 'warning';
  return 'healthy';
}

function getSecurityStatus(metrics) {
  if (!metrics) return 'unknown';
  if (metrics.threats > 0) return 'error';
  if (metrics.suspicious > 10) return 'warning';
  return 'healthy';
}

function formatUptime(seconds) {
  if (!seconds) return '0s';
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}
