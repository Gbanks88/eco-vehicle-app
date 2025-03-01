import Head from 'next/head';
import Link from 'next/link';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRightIcon, BoltIcon, GlobeAmericasIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';

export default function EcoVehicleHome() {
  const [activeVehicle, setActiveVehicle] = useState(0);

  const vehicles = [
    {
      id: 'ev-sedan',
      name: 'EcoLuxe Sedan',
      price: 'From $39,900',
      range: '350 miles',
      acceleration: '0-60 in 4.5s',
      image: '/images/vehicles/eco-sedan.jpg'
    },
    {
      id: 'ev-suv',
      name: 'EcoXplorer SUV',
      price: 'From $45,900',
      range: '320 miles',
      acceleration: '0-60 in 5.2s',
      image: '/images/vehicles/eco-suv.jpg'
    },
    {
      id: 'ev-sport',
      name: 'EcoSprint GT',
      price: 'From $59,900',
      range: '300 miles',
      acceleration: '0-60 in 3.1s',
      image: '/images/vehicles/eco-sport.jpg'
    }
  ];

  const features = [
    {
      icon: <BoltIcon className="h-6 w-6" />,
      title: 'Advanced Battery Tech',
      description: 'Industry-leading range with rapid charging capability'
    },
    {
      icon: <GlobeAmericasIcon className="h-6 w-6" />,
      title: 'Eco-Friendly',
      description: 'Zero emissions with sustainable manufacturing'
    },
    {
      icon: <CurrencyDollarIcon className="h-6 w-6" />,
      title: 'Cost Effective',
      description: 'Lower maintenance and operating costs'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>CG4L - Eco Vehicle Solutions</title>
        <meta name="description" content="Sustainable transportation solutions for a greener future" />
      </Head>

      <main className="relative">
        {/* Hero Section */}
        <div className="relative h-[80vh] bg-gradient-to-r from-green-900 to-green-700 overflow-hidden">
          <div className="absolute inset-0 bg-black/40" />
          <div className="container mx-auto px-4 h-full flex items-center relative z-10">
            <div className="max-w-2xl text-white">
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-5xl font-bold mb-6"
              >
                The Future of
                <span className="block text-green-400">Sustainable Mobility</span>
              </motion.h1>
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-xl mb-8"
              >
                Experience the perfect blend of performance, luxury, and environmental responsibility.
              </motion.p>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="flex gap-4"
              >
                <Link href="/ev/vehicles" className="bg-green-500 text-white px-8 py-3 rounded-full hover:bg-green-600 transition">
                  Explore Vehicles
                </Link>
                <Link href="/3d" className="bg-white/10 text-white px-8 py-3 rounded-full hover:bg-white/20 transition">
                  View in 3D
                </Link>
              </motion.div>
            </div>
          </div>
        </div>

        {/* Featured Vehicles */}
        <section className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <h2 className="text-4xl font-bold text-green-800 mb-12 text-center">Featured Models</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {vehicles.map((vehicle, index) => (
                <motion.div
                  key={vehicle.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.2 }}
                  className="bg-gray-50 rounded-lg overflow-hidden hover:shadow-xl transition"
                  onMouseEnter={() => setActiveVehicle(index)}
                >
                  <div className="h-48 bg-gray-200 relative">
                    {/* Replace with actual image */}
                    <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                      {vehicle.name} Preview
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-2xl font-semibold text-green-700 mb-2">{vehicle.name}</h3>
                    <div className="space-y-2 text-gray-600 mb-4">
                      <p>Range: {vehicle.range}</p>
                      <p>Acceleration: {vehicle.acceleration}</p>
                      <p className="font-semibold">{vehicle.price}</p>
                    </div>
                    <Link href={`/ev/vehicles/${vehicle.id}`} className="inline-flex items-center text-green-600 hover:text-green-800">
                      Learn more <ChevronRightIcon className="h-4 w-4 ml-1" />
                    </Link>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="py-20 bg-green-50">
          <div className="container mx-auto px-4">
            <h2 className="text-4xl font-bold text-green-800 mb-12 text-center">Why Choose Electric?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.2 }}
                  className="bg-white rounded-lg p-6 text-center"
                >
                  <div className="inline-block p-3 bg-green-100 rounded-full text-green-600 mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-green-700 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-green-900 text-white">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-4xl font-bold mb-6">Ready to Go Electric?</h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto">
              Schedule a test drive today and experience the future of sustainable mobility.
            </p>
            <Link href="/contact" className="inline-block bg-white text-green-900 px-8 py-3 rounded-full hover:bg-green-100 transition">
              Schedule Test Drive
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
