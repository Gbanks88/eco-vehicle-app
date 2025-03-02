import Head from 'next/head';
import { useState } from 'react';

export default function ChargingStations() {
  const [location, setLocation] = useState('');
  const [radius, setRadius] = useState('10');

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>Charging Stations - CG4L</title>
        <meta name="description" content="Find eco vehicle charging stations near you" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-green-800 mb-8">
          Charging Stations
        </h1>

        {/* Search Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-gray-700 mb-2">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter city or zip code"
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-2">Radius (miles)</label>
              <select
                value={radius}
                onChange={(e) => setRadius(e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="5">5 miles</option>
                <option value="10">10 miles</option>
                <option value="25">25 miles</option>
                <option value="50">50 miles</option>
              </select>
            </div>
            <div className="flex items-end">
              <button className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700">
                Find Stations
              </button>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-green-700 mb-4">Fast Charging</h2>
            <p className="text-gray-600">Quick charging solutions for your eco vehicle</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-green-700 mb-4">Home Installation</h2>
            <p className="text-gray-600">Professional charging station installation services</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-green-700 mb-4">Network Access</h2>
            <p className="text-gray-600">Join our charging network membership program</p>
          </div>
        </div>

        {/* Map Placeholder */}
        <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
          <p className="text-gray-600">Interactive Map Coming Soon</p>
        </div>
      </main>
    </div>
  );
}
