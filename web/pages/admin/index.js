import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useSession } from 'next-auth/react';
import AdminLayout from '../../components/admin/Layout';
import {
  ChartBarIcon,
  UsersIcon,
  CurrencyDollarIcon,
  ShoppingCartIcon,
} from '@heroicons/react/24/outline';

const stats = [
  { name: 'Total Vehicles', value: '12', icon: ChartBarIcon, change: '+2.5%', changeType: 'positive' },
  { name: 'Active Users', value: '2.7k', icon: UsersIcon, change: '+10.2%', changeType: 'positive' },
  { name: 'Test Drives', value: '42', icon: ShoppingCartIcon, change: '+28.1%', changeType: 'positive' },
  { name: 'Revenue', value: '$4.2M', icon: CurrencyDollarIcon, change: '+15.3%', changeType: 'positive' },
];

export default function AdminDashboard() {
  const { data: session } = useSession();
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, fetch this data from your API
    setRecentActivity([
      {
        id: 1,
        type: 'test_drive',
        user: 'John Smith',
        vehicle: 'EcoLuxe Sedan',
        date: '2025-02-28T10:00:00',
        status: 'scheduled'
      },
      {
        id: 2,
        type: 'vehicle_update',
        user: 'Admin',
        vehicle: 'EcoXplorer SUV',
        date: '2025-02-28T09:30:00',
        status: 'completed'
      },
      {
        id: 3,
        type: 'user_registration',
        user: 'Sarah Johnson',
        date: '2025-02-28T09:00:00',
        status: 'completed'
      }
    ]);
    setLoading(false);
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    });
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'test_drive':
        return <ShoppingCartIcon className="h-5 w-5 text-green-500" />;
      case 'vehicle_update':
        return <ChartBarIcon className="h-5 w-5 text-blue-500" />;
      case 'user_registration':
        return <UsersIcon className="h-5 w-5 text-purple-500" />;
      default:
        return null;
    }
  };

  return (
    <AdminLayout>
      <Head>
        <title>Admin Dashboard - Eco Vehicle</title>
      </Head>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>

        {/* Welcome message */}
        <div className="mt-4">
          <div className="overflow-hidden rounded-lg bg-white shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Welcome back, {session?.user?.name}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Here's what's happening with your vehicles today.
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-8">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((item) => (
              <div
                key={item.name}
                className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6"
              >
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <item.icon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="truncate text-sm font-medium text-gray-500">{item.name}</dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">{item.value}</div>
                        <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                          item.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {item.change}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8">
          <div className="overflow-hidden bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg font-medium leading-6 text-gray-900">Recent Activity</h3>
            </div>
            <div className="border-t border-gray-200">
              <ul role="list" className="divide-y divide-gray-200">
                {loading ? (
                  <li className="px-4 py-4">Loading...</li>
                ) : (
                  recentActivity.map((activity) => (
                    <li key={activity.id} className="px-4 py-4 sm:px-6">
                      <div className="flex items-center">
                        {getActivityIcon(activity.type)}
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">
                            {activity.user}
                            {activity.vehicle && ` - ${activity.vehicle}`}
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatDate(activity.date)}
                          </div>
                        </div>
                        <div className="ml-auto">
                          <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                            activity.status === 'completed' 
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {activity.status}
                          </span>
                        </div>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
