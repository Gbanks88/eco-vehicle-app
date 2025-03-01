import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BoltIcon,
  ClockIcon,
  CurrencyDollarIcon,
  BatteryFullIcon,
  SparklesIcon,
  ShieldCheckIcon,
  ChevronLeftIcon
} from '@heroicons/react/24/outline';

const vehicles = {
  'ev-sedan': {
    name: 'EcoLuxe Sedan',
    tagline: 'Luxury meets sustainability',
    price: 'From $39,900',
    specs: {
      range: '350 miles',
      acceleration: '0-60 in 4.5s',
      topSpeed: '155 mph',
      charging: '10-80% in 30 min',
      power: '450 hp',
      battery: '100 kWh'
    },
    features: [
      'Advanced Driver Assistance',
      'Premium Sound System',
      'Panoramic Glass Roof',
      'Wireless Phone Charging',
      'Over-the-air Updates',
      'Smart Climate Control'
    ],
    colors: [
      { name: 'Arctic White', hex: '#FFFFFF' },
      { name: 'Midnight Black', hex: '#000000' },
      { name: 'Ocean Blue', hex: '#1E3D59' },
      { name: 'Forest Green', hex: '#2D5A27' }
    ],
    image: '/images/vehicles/eco-sedan.jpg'
  },
  'ev-suv': {
    name: 'EcoXplorer SUV',
    tagline: 'Adventure without compromise',
    price: 'From $45,900',
    specs: {
      range: '320 miles',
      acceleration: '0-60 in 5.2s',
      topSpeed: '135 mph',
      charging: '10-80% in 35 min',
      power: '400 hp',
      battery: '95 kWh'
    },
    features: [
      'All-Wheel Drive',
      'Adaptive Air Suspension',
      'Third Row Seating',
      'Towing Package',
      'Adventure Mode',
      'Cargo Management System'
    ],
    colors: [
      { name: 'Summit White', hex: '#FFFFFF' },
      { name: 'Granite Black', hex: '#000000' },
      { name: 'Desert Sand', hex: '#C2B280' },
      { name: 'Mountain Gray', hex: '#534B4F' }
    ],
    image: '/images/vehicles/eco-suv.jpg'
  },
  'ev-sport': {
    name: 'EcoSprint GT',
    tagline: 'Performance redefined',
    price: 'From $59,900',
    specs: {
      range: '300 miles',
      acceleration: '0-60 in 3.1s',
      topSpeed: '175 mph',
      charging: '10-80% in 25 min',
      power: '600 hp',
      battery: '85 kWh'
    },
    features: [
      'Sport-tuned Suspension',
      'Carbon Fiber Components',
      'Track Mode',
      'Performance Brakes',
      'Active Aerodynamics',
      'Launch Control'
    ],
    colors: [
      { name: 'Racing Red', hex: '#FF0000' },
      { name: 'Stealth Black', hex: '#000000' },
      { name: 'Silver Arrow', hex: '#C0C0C0' },
      { name: 'Electric Blue', hex: '#0047AB' }
    ],
    image: '/images/vehicles/eco-sport.jpg'
  }
};

export default function VehicleDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [selectedColor, setSelectedColor] = useState(0);
  const [activeTab, setActiveTab] = useState('specs');

  const vehicle = vehicles[id];

  if (!vehicle) {
    return null; // Or a loading state
  }

  const specIcons = {
    range: <BoltIcon className="h-6 w-6" />,
    acceleration: <ClockIcon className="h-6 w-6" />,
    topSpeed: <SparklesIcon className="h-6 w-6" />,
    charging: <BatteryFullIcon className="h-6 w-6" />,
    power: <BoltIcon className="h-6 w-6" />,
    battery: <BatteryFullIcon className="h-6 w-6" />
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>{vehicle.name} - CG4L</title>
        <meta name="description" content={`Learn more about the ${vehicle.name} - ${vehicle.tagline}`} />
      </Head>

      <main className="container mx-auto px-4 py-8">
        {/* Back Button */}
        <Link 
          href="/ev"
          className="inline-flex items-center text-green-700 hover:text-green-900 mb-8"
        >
          <ChevronLeftIcon className="h-5 w-5 mr-1" />
          Back to Vehicles
        </Link>

        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <h1 className="text-5xl font-bold text-green-800">{vehicle.name}</h1>
            <p className="text-2xl text-gray-600">{vehicle.tagline}</p>
            <div className="text-3xl font-semibold text-green-700">{vehicle.price}</div>
            <div className="flex gap-4">
              <button className="bg-green-600 text-white px-8 py-3 rounded-full hover:bg-green-700 transition">
                Order Now
              </button>
              <button className="bg-white border-2 border-green-600 text-green-600 px-8 py-3 rounded-full hover:bg-green-50 transition">
                Schedule Test Drive
              </button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gray-100 rounded-lg aspect-video flex items-center justify-center"
          >
            {/* Replace with actual vehicle image */}
            <div className="text-gray-400 text-center">
              <p>{vehicle.name}</p>
              <p className="text-sm">Vehicle Preview</p>
            </div>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="flex gap-8">
            <button
              onClick={() => setActiveTab('specs')}
              className={`pb-4 px-2 ${
                activeTab === 'specs'
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-500 hover:text-green-600'
              }`}
            >
              Specifications
            </button>
            <button
              onClick={() => setActiveTab('features')}
              className={`pb-4 px-2 ${
                activeTab === 'features'
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-500 hover:text-green-600'
              }`}
            >
              Features
            </button>
            <button
              onClick={() => setActiveTab('colors')}
              className={`pb-4 px-2 ${
                activeTab === 'colors'
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-500 hover:text-green-600'
              }`}
            >
              Colors
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mb-16">
          {activeTab === 'specs' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            >
              {Object.entries(vehicle.specs).map(([key, value]) => (
                <div key={key} className="bg-white rounded-lg p-6 shadow-sm">
                  <div className="text-green-600 mb-2">
                    {specIcons[key]}
                  </div>
                  <div className="text-gray-600 capitalize">{key}</div>
                  <div className="text-xl font-semibold text-green-800">{value}</div>
                </div>
              ))}
            </motion.div>
          )}

          {activeTab === 'features' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {vehicle.features.map((feature, index) => (
                <div key={index} className="flex items-center bg-white rounded-lg p-4 shadow-sm">
                  <ShieldCheckIcon className="h-5 w-5 text-green-600 mr-3" />
                  <span>{feature}</span>
                </div>
              ))}
            </motion.div>
          )}

          {activeTab === 'colors' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              <div className="flex gap-4">
                {vehicle.colors.map((color, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedColor(index)}
                    className={`w-12 h-12 rounded-full border-2 ${
                      selectedColor === index ? 'border-green-600' : 'border-gray-200'
                    }`}
                    style={{ backgroundColor: color.hex }}
                  />
                ))}
              </div>
              <div className="text-xl font-semibold text-green-800">
                {vehicle.colors[selectedColor].name}
              </div>
            </motion.div>
          )}
        </div>

        {/* CTA Section */}
        <section className="bg-green-900 text-white rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Experience the {vehicle.name}?</h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto">
            Schedule a test drive today and discover why the {vehicle.name} is the perfect choice for your sustainable journey.
          </p>
          <div className="flex gap-4 justify-center">
            <button className="bg-white text-green-900 px-8 py-3 rounded-full hover:bg-green-100 transition">
              Schedule Test Drive
            </button>
            <button className="bg-green-800 text-white px-8 py-3 rounded-full hover:bg-green-700 transition">
              Build Your Own
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
