import { useState, useEffect } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import Layout from '../../../components/admin/Layout';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function Analytics() {
  const [metrics, setMetrics] = useState(null);
  const [timeframe, setTimeframe] = useState('30d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [timeframe]);

  async function fetchAnalytics() {
    try {
      setLoading(true);
      const response = await fetch(`/api/analytics?timeframe=${timeframe}`);
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
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
          <h1 className="text-3xl font-bold text-gray-800">Analytics Dashboard</h1>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="px-4 py-2 border rounded-lg shadow-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Revenue"
            value={formatCurrency(metrics?.revenue?.total)}
            trend={metrics?.revenue?.trend}
          />
          <MetricCard
            title="Active Users"
            value={metrics?.users?.active}
            trend={metrics?.users?.trend}
          />
          <MetricCard
            title="Conversion Rate"
            value={formatPercentage(metrics?.conversion?.rate)}
            trend={metrics?.conversion?.trend}
          />
          <MetricCard
            title="Average Order Value"
            value={formatCurrency(metrics?.orders?.averageValue)}
            trend={metrics?.orders?.trend}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartCard title="Revenue Trend">
            <Line data={metrics?.charts?.revenue} options={lineChartOptions} />
          </ChartCard>
          <ChartCard title="User Activity">
            <Bar data={metrics?.charts?.activity} options={barChartOptions} />
          </ChartCard>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <ChartCard title="Customer Segments">
            <Pie data={metrics?.charts?.segments} options={pieChartOptions} />
          </ChartCard>
          <ChartCard title="Top Products">
            <Bar
              data={metrics?.charts?.products}
              options={{ ...barChartOptions, indexAxis: 'y' }}
            />
          </ChartCard>
          <ChartCard title="Conversion Funnel">
            <Bar data={metrics?.charts?.funnel} options={funnelChartOptions} />
          </ChartCard>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
            <ActivityList activities={metrics?.recentActivity} />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Insights</h2>
            <InsightsList insights={metrics?.insights} />
          </div>
        </div>
      </div>
    </Layout>
  );
}

function MetricCard({ title, value, trend }) {
  const trendColor = trend > 0 ? 'text-green-500' : 'text-red-500';
  const trendIcon = trend > 0 ? '↑' : '↓';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
      <div className="mt-2 flex items-baseline">
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
        <span className={`ml-2 text-sm font-medium ${trendColor}`}>
          {trendIcon} {Math.abs(trend)}%
        </span>
      </div>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      {children}
    </div>
  );
}

function ActivityList({ activities }) {
  return (
    <div className="space-y-4">
      {activities?.map((activity, index) => (
        <div key={index} className="flex items-start">
          <div className="flex-shrink-0">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-100">
              {activity.icon}
            </span>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-900">{activity.title}</p>
            <p className="text-sm text-gray-500">{activity.description}</p>
            <p className="text-xs text-gray-400">{activity.time}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function InsightsList({ insights }) {
  return (
    <div className="space-y-4">
      {insights?.map((insight, index) => (
        <div
          key={index}
          className={`p-4 rounded-lg ${
            insight.type === 'positive'
              ? 'bg-green-50'
              : insight.type === 'negative'
              ? 'bg-red-50'
              : 'bg-blue-50'
          }`}
        >
          <h3 className="font-medium text-gray-900">{insight.title}</h3>
          <p className="mt-1 text-sm text-gray-500">{insight.description}</p>
          {insight.recommendation && (
            <p className="mt-2 text-sm font-medium text-gray-900">
              Recommendation: {insight.recommendation}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

// Chart options
const lineChartOptions = {
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

const barChartOptions = {
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

const pieChartOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'right',
    },
  },
};

const funnelChartOptions = {
  responsive: true,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};

// Helper functions
function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value || 0);
}

function formatPercentage(value) {
  return `${((value || 0) * 100).toFixed(1)}%`;
}
