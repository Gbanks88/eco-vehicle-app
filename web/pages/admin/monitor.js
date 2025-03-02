import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const STATUS_COLORS = {
  healthy: 'bg-green-500',
  warning: 'bg-yellow-500',
  critical: 'bg-red-500',
};

const MetricsCard = ({ title, value, status, trend }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <h3 className="text-gray-600 text-sm font-semibold mb-2">{title}</h3>
    <div className="flex items-center justify-between">
      <span className="text-2xl font-bold">{value}</span>
      <span className={`${STATUS_COLORS[status]} w-3 h-3 rounded-full`} />
    </div>
    {trend && (
      <div className="mt-2 text-sm">
        <span className={trend > 0 ? 'text-green-500' : 'text-red-500'}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </span>
        <span className="text-gray-500 ml-1">vs last hour</span>
      </div>
    )}
  </div>
);

const DomainStatus = ({ domain, metrics }) => (
  <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-xl font-bold">{domain}</h2>
      <span className={`${STATUS_COLORS[metrics.status]} px-3 py-1 rounded-full text-white text-sm`}>
        {metrics.status}
      </span>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <MetricsCard
        title="Response Time"
        value={`${metrics.responseTime}ms`}
        status={metrics.responseTimeStatus}
        trend={metrics.responseTimeTrend}
      />
      <MetricsCard
        title="SSL Days Remaining"
        value={metrics.sslDays}
        status={metrics.sslStatus}
      />
      <MetricsCard
        title="Security Score"
        value={`${metrics.securityScore}%`}
        status={metrics.securityStatus}
      />
    </div>
    {metrics.chart && (
      <div className="mt-6">
        <Line data={metrics.chart} options={chartOptions} />
      </div>
    )}
  </div>
);

const AlertLog = ({ alerts }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <h2 className="text-xl font-bold mb-4">Recent Alerts</h2>
    <div className="space-y-4">
      {alerts.map((alert, index) => (
        <div
          key={index}
          className={`p-4 rounded-lg ${
            alert.severity === 'critical' ? 'bg-red-100' :
            alert.severity === 'warning' ? 'bg-yellow-100' : 'bg-blue-100'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-semibold">{alert.domain}</span>
            <span className="text-sm text-gray-500">{alert.time}</span>
          </div>
          <p className="mt-1">{alert.message}</p>
        </div>
      ))}
    </div>
  </div>
);

const chartOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};

export default function MonitorDashboard() {
  const [domains, setDomains] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch metrics from your API
        const response = await fetch('/api/monitor/metrics');
        const data = await response.json();
        setDomains(data.domains);
        setAlerts(data.alerts);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Domain Monitor Dashboard</h1>
        
        <div className="grid grid-cols-1 gap-6 mb-8">
          {domains.map((domain) => (
            <DomainStatus key={domain.name} {...domain} />
          ))}
        </div>

        <AlertLog alerts={alerts} />
      </div>
    </div>
  );
}
