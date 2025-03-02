import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import Head from 'next/head';

// Chart components (using Chart.js)
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export async function getServerSideProps(context) {
  const { requireAuth } = require('../../lib/auth-helpers');
  const authResult = await requireAuth(context);
  
  if (authResult.redirect) {
    return authResult;
  }

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/dashboard`);
    if (!res.ok) throw new Error('Failed to fetch dashboard data');
    const dashboardData = await res.json();
    
    return {
      props: {
        ...authResult.props,
        dashboardData
      }
    };
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return {
      props: {
        ...authResult.props,
        dashboardData: null
      }
    };
  }
}

export default function AdminDashboard({ dashboardData, session }) {
  if (!dashboardData) {
    return (
      <Layout session={session}>
        <div className="text-center py-10 text-red-600">
          Failed to load dashboard data
        </div>
      </Layout>
    );
  }

  const {
    totalOrders,
    recentOrders,
    totalRevenue,
    productStats,
    userStats
  } = dashboardData;

  return (
    <Layout session={session}>
      <Head>
        <title>Admin Dashboard | Eco Vehicle</title>
      </Head>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>

        {/* Summary Cards */}
        <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Orders</dt>
                    <dd className="text-lg font-medium text-gray-900">{totalOrders}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Revenue</dt>
                    <dd className="text-lg font-medium text-gray-900">${totalRevenue.toLocaleString()}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Orders */}
        <div className="mt-8">
          <h2 className="text-lg font-medium text-gray-900">Recent Orders</h2>
          <div className="mt-4 flex flex-col">
            <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Order ID
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Customer
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Amount
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {recentOrders.map((order) => (
                        <tr key={order._id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {order._id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {order.customerEmail}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${order.amount.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              order.status === 'paid' ? 'bg-green-100 text-green-800' :
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(order.createdAt).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Product Performance Chart */}
        <div className="mt-8">
          <h2 className="text-lg font-medium text-gray-900">Product Performance</h2>
          <div className="mt-4">
            <Bar
              data={{
                labels: productStats.map(p => p.name),
                datasets: [
                  {
                    label: 'Total Orders',
                    data: productStats.map(p => p.totalOrders),
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                  },
                  {
                    label: 'Revenue',
                    data: productStats.map(p => p.revenue),
                    backgroundColor: 'rgba(16, 185, 129, 0.5)',
                  }
                ]
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Product Performance'
                  }
                }
              }}
            />
          </div>
        </div>

        {/* User Statistics */}
        <div className="mt-8">
          <h2 className="text-lg font-medium text-gray-900">Top Customers</h2>
          <div className="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {userStats.slice(0, 6).map((user) => (
              <div key={user._id} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">{user.email}</dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">${user.totalSpent.toLocaleString()}</dd>
                        <dd className="mt-1 text-sm text-gray-500">{user.totalOrders} orders</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
