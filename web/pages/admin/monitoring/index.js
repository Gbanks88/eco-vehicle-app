import { useState, useEffect } from 'react';
import Layout from '../../../components/admin/Layout';
import ExportMetrics from '../../../components/admin/monitoring/ExportMetrics';
import CustomCharts from '../../../components/admin/monitoring/CustomCharts';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function Monitoring() {
  const [metrics, setMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [timeframe, setTimeframe] = useState('1h');
  const [loading, setLoading] = useState(true);
  const [selectedSystem, setSelectedSystem] = useState('all');

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [timeframe, selectedSystem]);

  async function fetchMetrics() {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/monitoring?timeframe=${timeframe}&system=${selectedSystem}`
      );
      const data = await response.json();
      setMetrics(data.metrics);
      setAlerts(data.alerts);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">System Monitoring</h1>
          <div className="flex space-x-4">
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="px-4 py-2 border rounded-lg shadow-sm"
            >
              <option value="1h">Last Hour</option>
              <option value="6h">Last 6 Hours</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
            </select>
            <select
              value={selectedSystem}
              onChange={(e) => setSelectedSystem(e.target.value)}
              className="px-4 py-2 border rounded-lg shadow-sm"
            >
              <option value="all">All Systems</option>
              <option value="database">Database</option>
              <option value="api">API</option>
              <option value="ai">AI Systems</option>
              <option value="security">Security</option>
            </select>
          </div>
        </div>

        {/* System Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="System Health"
            status={metrics?.system?.status}
            metrics={metrics?.system?.metrics}
          />
          <StatusCard
            title="Database Health"
            status={metrics?.database?.status}
            metrics={metrics?.database?.metrics}
          />
          <StatusCard
            title="API Health"
            status={metrics?.api?.status}
            metrics={metrics?.api?.metrics}
          />
          <StatusCard
            title="Security Status"
            status={metrics?.security?.status}
            metrics={metrics?.security?.metrics}
          />
        </div>

        {/* Active Alerts */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Active Alerts</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="divide-y divide-gray-200">
              {alerts.map((alert, index) => (
                <AlertItem key={index} alert={alert} />
              ))}
              {alerts.length === 0 && (
                <div className="p-4 text-center text-gray-500">
                  No active alerts
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <MetricChart
            title="System Load"
            type="line"
            data={metrics?.charts?.systemLoad}
            options={lineChartOptions}
          />
          <MetricChart
            title="Response Times"
            type="line"
            data={metrics?.charts?.responseTimes}
            options={lineChartOptions}
          />
        </div>

        {/* AI Systems Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <MetricChart
            title="AI Systems Accuracy"
            type="radar"
            data={metrics?.charts?.aiAccuracy}
            options={radarChartOptions}
          />
          <MetricChart
            title="AI Systems Latency"
            type="bar"
            data={metrics?.charts?.aiLatency}
            options={barChartOptions}
          />
        </div>

        {/* Detailed Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <DetailedMetrics
            title="Database Metrics"
            metrics={metrics?.database?.detailed}
          />
          <DetailedMetrics
            title="API Metrics"
            metrics={metrics?.api?.detailed}
          />
          <DetailedMetrics
            title="Security Metrics"
            metrics={metrics?.security?.detailed}
          />
        </div>
      </div>
    </Layout>
  );
}

function StatusCard({ title, status, metrics }) {
  const statusColors = {
    healthy: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800'
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
      <div className="mt-2">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
          {status}
        </span>
      </div>
      <div className="mt-4 space-y-2">
        {Object.entries(metrics || {}).map(([key, value]) => (
          <div key={key} className="flex justify-between text-sm">
            <span className="text-gray-500">{key}</span>
            <span className="font-medium">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AlertItem({ alert }) {
  const levelColors = {
    critical: 'bg-red-50 text-red-800',
    high: 'bg-orange-50 text-orange-800',
    medium: 'bg-yellow-50 text-yellow-800',
    low: 'bg-blue-50 text-blue-800'
  };

  return (
    <div className={`p-4 ${levelColors[alert.level]}`}>
      <div className="flex justify-between">
        <div>
          <h4 className="font-medium">{alert.type}</h4>
          <p className="text-sm mt-1">{alert.message}</p>
        </div>
        <span className="text-xs font-medium uppercase">
          {alert.level}
        </span>
      </div>
      {alert.timestamp && (
        <div className="mt-2 text-xs">
          {new Date(alert.timestamp).toLocaleString()}
        </div>
      )}
    </div>
  );
}

function MetricChart({ title, type, data, options }) {
  const ChartComponent = {
    line: Line,
    bar: Bar,
    radar: Radar
  }[type];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <div className="h-64">
        <ChartComponent data={data} options={options} />
      </div>
    </div>
  );
}

function DetailedMetrics({ title, metrics }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <div className="space-y-4">
        {Object.entries(metrics || {}).map(([key, value]) => (
          <div key={key}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-500">{key}</span>
              <span className="font-medium">{value.value}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  value.status === 'healthy'
                    ? 'bg-green-500'
                    : value.status === 'warning'
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${value.percentage}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Chart options
const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
};

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
};

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      max: 1
    }
  }
};
