import Head from 'next/head';
import { useState } from 'react';

export default function PartsAndAccessories() {
  const [category, setCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const categories = [
    { id: 'all', name: 'All Parts' },
    { id: 'batteries', name: 'Batteries & Power' },
    { id: 'charging', name: 'Charging Components' },
    { id: 'motors', name: 'Motors & Drive Units' },
    { id: 'suspension', name: 'Suspension & Handling' },
    { id: 'interior', name: 'Interior Accessories' },
    { id: 'exterior', name: 'Exterior Parts' }
  ];

  const parts = [
    {
      id: 1,
      name: 'High-Capacity EV Battery',
      category: 'batteries',
      price: 4999.99,
      image: '/parts/battery.jpg',
      description: 'Long-range battery with advanced thermal management'
    },
    {
      id: 2,
      name: 'Fast Charging Port',
      category: 'charging',
      price: 299.99,
      image: '/parts/charging-port.jpg',
      description: 'Compatible with all standard charging stations'
    },
    // Add more parts here
  ];

  const filteredParts = parts.filter(part => 
    (category === 'all' || part.category === category) &&
    part.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>Parts & Accessories - CG4L</title>
        <meta name="description" content="Quality parts and accessories for eco vehicles" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-green-800 mb-8">
          Parts & Accessories
        </h1>

        {/* Search and Filter */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search parts..."
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-2 border rounded"
              >
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Categories */}
        <div className="flex overflow-x-auto space-x-4 mb-8 pb-4">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`px-4 py-2 rounded-full whitespace-nowrap ${
                category === cat.id
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-green-100'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* Parts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredParts.map(part => (
            <div key={part.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="h-48 bg-gray-200">
                {/* Image placeholder */}
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  Part Image
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold text-green-700 mb-2">{part.name}</h3>
                <p className="text-gray-600 mb-4">{part.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-green-600">${part.price}</span>
                  <button className="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700">
                    Add to Cart
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
