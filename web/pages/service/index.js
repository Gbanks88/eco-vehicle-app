import Head from 'next/head';
import { useState } from 'react';

export default function ServiceCenter() {
  const [serviceType, setServiceType] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');
  const [preferredDate, setPreferredDate] = useState('');

  const services = [
    {
      id: 'maintenance',
      title: 'Regular Maintenance',
      description: 'Comprehensive inspection and maintenance of your eco vehicle',
      duration: '2-3 hours',
      price: 'From $149'
    },
    {
      id: 'battery',
      title: 'Battery Service',
      description: 'Battery health check, optimization, and replacement if needed',
      duration: '1-4 hours',
      price: 'From $99'
    },
    {
      id: 'diagnostic',
      title: 'Diagnostic Check',
      description: 'Complete system diagnostic and software updates',
      duration: '1 hour',
      price: 'From $79'
    },
    {
      id: 'charging',
      title: 'Charging System',
      description: 'Charging port repair and system optimization',
      duration: '1-2 hours',
      price: 'From $129'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>Service Center - CG4L</title>
        <meta name="description" content="Professional eco vehicle service and maintenance" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-green-800 mb-8">
          Service Center
        </h1>

        {/* Service Booking Form */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-green-700 mb-6">Schedule Service</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-gray-700 mb-2">Service Type</label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="">Select Service</option>
                {services.map(service => (
                  <option key={service.id} value={service.id}>{service.title}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 mb-2">Vehicle Model</label>
              <input
                type="text"
                value={vehicleModel}
                onChange={(e) => setVehicleModel(e.target.value)}
                placeholder="Enter your vehicle model"
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-2">Preferred Date</label>
              <input
                type="date"
                value={preferredDate}
                onChange={(e) => setPreferredDate(e.target.value)}
                className="w-full p-2 border rounded"
              />
            </div>
          </div>
          <button className="mt-6 bg-green-600 text-white py-2 px-6 rounded hover:bg-green-700">
            Book Service
          </button>
        </div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {services.map(service => (
            <div key={service.id} className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold text-green-700 mb-2">{service.title}</h3>
              <p className="text-gray-600 mb-4">{service.description}</p>
              <div className="flex justify-between text-sm text-gray-500">
                <span>Duration: {service.duration}</span>
                <span>{service.price}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Information */}
        <div className="mt-12 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-green-700 mb-6">Why Choose Our Service Center?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-green-600 mb-2">Certified Technicians</h3>
              <p className="text-gray-600">Expert technicians specialized in eco vehicles</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-green-600 mb-2">State-of-the-art Facility</h3>
              <p className="text-gray-600">Advanced diagnostic and repair equipment</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-green-600 mb-2">Warranty Protection</h3>
              <p className="text-gray-600">All services backed by our comprehensive warranty</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
