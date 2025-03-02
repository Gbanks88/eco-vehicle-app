import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { fetchVehicles, compareVehicles } from '../../utils/api';
import { ChevronDownIcon, XMarkIcon } from '@heroicons/react/24/outline';

export default function CompareVehicles() {
  const [vehicles, setVehicles] = useState([]);
  const [selectedVehicles, setSelectedVehicles] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadVehicles();
  }, []);

  useEffect(() => {
    if (selectedVehicles.length >= 2) {
      loadComparison();
    }
  }, [selectedVehicles]);

  const loadVehicles = async () => {
    try {
      const data = await fetchVehicles();
      setVehicles(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load vehicles');
      setLoading(false);
    }
  };

  const loadComparison = async () => {
    if (selectedVehicles.length < 2) return;
    
    try {
      const data = await compareVehicles(selectedVehicles.map(v => v.id));
      setComparisonData(data);
    } catch (err) {
      setError('Failed to load comparison');
    }
  };

  const handleVehicleSelect = (vehicle) => {
    if (selectedVehicles.length >= 3) return;
    if (selectedVehicles.find(v => v.id === vehicle.id)) return;
    setSelectedVehicles([...selectedVehicles, vehicle]);
  };

  const removeVehicle = (vehicleId) => {
    setSelectedVehicles(selectedVehicles.filter(v => v.id !== vehicleId));
  };

  const ComparisonTable = () => {
    if (!selectedVehicles.length) return null;

    const specs = [
      { key: 'price', label: 'Starting Price', format: price => `$${price.toLocaleString()}` },
      { key: 'specs.range', label: 'Range', format: range => `${range} miles` },
      { key: 'specs.acceleration', label: '0-60 mph', format: acc => `${acc}s` },
      { key: 'specs.topSpeed', label: 'Top Speed', format: speed => `${speed} mph` },
      { key: 'specs.power', label: 'Power', format: power => `${power} hp` },
      { key: 'specs.batteryCapacity', label: 'Battery', format: cap => `${cap} kWh` },
      { key: 'specs.chargingTime', label: 'Charging (10-80%)', format: time => `${time} min` },
    ];

    return (
      <div className="mt-8 bg-white rounded-xl shadow-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-green-50">
              <th className="py-4 px-6 text-left text-green-800">Specification</th>
              {selectedVehicles.map(vehicle => (
                <th key={vehicle.id} className="py-4 px-6 text-center text-green-800">
                  <div className="flex items-center justify-between">
                    <span>{vehicle.name}</span>
                    <button
                      onClick={() => removeVehicle(vehicle.id)}
                      className="text-green-600 hover:text-green-800"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {specs.map((spec, index) => (
              <tr key={spec.key} className={index % 2 ? 'bg-gray-50' : ''}>
                <td className="py-4 px-6 font-medium text-gray-700">{spec.label}</td>
                {selectedVehicles.map(vehicle => {
                  const value = spec.key.split('.').reduce((obj, key) => obj[key], vehicle);
                  return (
                    <td key={vehicle.id} className="py-4 px-6 text-center text-gray-800">
                      {spec.format(value)}
                    </td>
                  );
                })}
              </tr>
            ))}
            <tr>
              <td className="py-4 px-6 font-medium text-gray-700">Features</td>
              {selectedVehicles.map(vehicle => (
                <td key={vehicle.id} className="py-4 px-6 text-center text-gray-800">
                  <ul className="text-left list-disc pl-4">
                    {vehicle.features.map((feature, index) => (
                      <li key={index} className="mb-1">{feature}</li>
                    ))}
                  </ul>
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-4 px-6 font-medium text-gray-700">Available Colors</td>
              {selectedVehicles.map(vehicle => (
                <td key={vehicle.id} className="py-4 px-6 text-center">
                  <div className="flex flex-wrap gap-2 justify-center">
                    {vehicle.colors.map(color => (
                      <div
                        key={color.name}
                        className="w-6 h-6 rounded-full border border-gray-200"
                        style={{ backgroundColor: color.hex }}
                        title={`${color.name}${color.price ? ` (+$${color.price})` : ''}`}
                      />
                    ))}
                  </div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white py-12">
      <Head>
        <title>Compare Vehicles - Eco Vehicle Project</title>
        <meta name="description" content="Compare our eco-friendly vehicles side by side" />
      </Head>

      <main className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-green-800 mb-4">Compare Vehicles</h1>
          <p className="text-xl text-gray-600">
            Select up to three vehicles to compare their specifications side by side
          </p>
        </motion.div>

        {loading ? (
          <div className="text-center py-12">Loading vehicles...</div>
        ) : error ? (
          <div className="text-center text-red-600 py-12">{error}</div>
        ) : (
          <>
            {selectedVehicles.length < 3 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Select Vehicles to Compare</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {vehicles
                    .filter(v => !selectedVehicles.find(sv => sv.id === v.id))
                    .map(vehicle => (
                      <motion.div
                        key={vehicle.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.02 }}
                        className="bg-white rounded-xl shadow-md overflow-hidden cursor-pointer"
                        onClick={() => handleVehicleSelect(vehicle)}
                      >
                        <div className="aspect-video bg-gray-100 relative">
                          {/* Replace with actual image */}
                          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                            {vehicle.name} Preview
                          </div>
                        </div>
                        <div className="p-6">
                          <h3 className="text-xl font-semibold text-green-800 mb-2">{vehicle.name}</h3>
                          <p className="text-gray-600 mb-4">{vehicle.category}</p>
                          <div className="text-2xl font-bold text-green-700">
                            ${vehicle.price.toLocaleString()}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                </div>
              </div>
            )}

            <ComparisonTable />

            {selectedVehicles.length >= 2 && (
              <div className="mt-12 text-center">
                <Link
                  href="/contact"
                  className="inline-block bg-green-600 text-white px-8 py-3 rounded-full hover:bg-green-700 transition"
                >
                  Schedule a Test Drive
                </Link>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
