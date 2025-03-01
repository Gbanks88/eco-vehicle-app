import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ChevronRightIcon, BoltIcon, ClockIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';

const vehicles = [
  {
    id: 'ev-sedan',
    name: 'EcoLuxe Sedan',
    category: 'Luxury',
    price: 'From $39,900',
    range: '350 miles',
    acceleration: '0-60 in 4.5s',
    description: 'Experience luxury and sustainability in perfect harmony. The EcoLuxe Sedan combines premium comfort with zero-emission performance.',
    features: ['Premium Interior', 'Advanced Autopilot', 'Glass Roof'],
    image: '/images/vehicles/eco-sedan.jpg'
  },
  {
    id: 'ev-suv',
    name: 'EcoXplorer SUV',
    category: 'SUV',
    price: 'From $45,900',
    range: '320 miles',
    acceleration: '0-60 in 5.2s',
    description: 'Adventure meets eco-consciousness. The EcoXplorer SUV offers versatility and capability without compromising environmental responsibility.',
    features: ['All-Wheel Drive', 'Adaptive Suspension', 'Towing Package'],
    image: '/images/vehicles/eco-suv.jpg'
  },
  {
    id: 'ev-sport',
    name: 'EcoSprint GT',
    category: 'Performance',
    price: 'From $59,900',
    range: '300 miles',
    acceleration: '0-60 in 3.1s',
    description: 'Pure performance with zero emissions. The EcoSprint GT delivers exhilarating acceleration and handling in an eco-friendly package.',
    features: ['Track Mode', 'Carbon Fiber Body', 'Active Aero'],
    image: '/images/vehicles/eco-sport.jpg'
  }
];

const categories = ['All', 'Luxury', 'SUV', 'Performance'];

export default function VehicleList() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>Our Vehicles - CG4L</title>
        <meta name="description" content="Explore our range of eco-friendly vehicles" />
      </Head>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl font-bold text-green-800 mb-6"
          >
            Our Vehicle Lineup
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Discover our range of sustainable vehicles, each designed to deliver exceptional performance while protecting our environment.
          </motion.p>
        </div>

        {/* Category Filter */}
        <div className="flex justify-center gap-4 mb-12">
          {categories.map((category, index) => (
            <motion.button
              key={category}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="px-6 py-2 rounded-full bg-white shadow-sm hover:shadow-md transition text-green-700 hover:bg-green-50"
            >
              {category}
            </motion.button>
          ))}
        </div>

        {/* Vehicle Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {vehicles.map((vehicle, index) => (
            <motion.div
              key={vehicle.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
              className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition"
            >
              <div className="aspect-video bg-gray-100 relative">
                {/* Replace with actual image */}
                <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                  {vehicle.name} Preview
                </div>
              </div>
              <div className="p-8">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-3xl font-bold text-green-800 mb-2">{vehicle.name}</h2>
                    <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      {vehicle.category}
                    </span>
                  </div>
                  <div className="text-2xl font-semibold text-green-700">{vehicle.price}</div>
                </div>

                <p className="text-gray-600 mb-6">{vehicle.description}</p>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center">
                    <BoltIcon className="h-6 w-6 mx-auto text-green-600 mb-2" />
                    <div className="text-sm text-gray-500">Range</div>
                    <div className="font-semibold">{vehicle.range}</div>
                  </div>
                  <div className="text-center">
                    <ClockIcon className="h-6 w-6 mx-auto text-green-600 mb-2" />
                    <div className="text-sm text-gray-500">Acceleration</div>
                    <div className="font-semibold">{vehicle.acceleration}</div>
                  </div>
                  <div className="text-center">
                    <CurrencyDollarIcon className="h-6 w-6 mx-auto text-green-600 mb-2" />
                    <div className="text-sm text-gray-500">Tax Credit</div>
                    <div className="font-semibold">Up to $7,500</div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-6">
                  {vehicle.features.map((feature, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {feature}
                    </span>
                  ))}
                </div>

                <div className="flex gap-4">
                  <Link
                    href={`/ev/vehicles/${vehicle.id}`}
                    className="flex items-center text-green-600 hover:text-green-800 font-semibold"
                  >
                    Learn More <ChevronRightIcon className="h-5 w-5 ml-1" />
                  </Link>
                  <Link
                    href={`/ev/vehicles/${vehicle.id}#configure`}
                    className="flex items-center text-green-600 hover:text-green-800 font-semibold"
                  >
                    Configure
                  </Link>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* CTA Section */}
        <section className="bg-green-900 text-white rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">Find Your Perfect Eco Vehicle</h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto">
            Not sure which model is right for you? Schedule a consultation with our experts or visit a showroom for a test drive.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/contact"
              className="bg-white text-green-900 px-8 py-3 rounded-full hover:bg-green-100 transition"
            >
              Schedule Consultation
            </Link>
            <Link
              href="/locations"
              className="bg-green-800 text-white px-8 py-3 rounded-full hover:bg-green-700 transition"
            >
              Find Showroom
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
