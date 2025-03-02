import { useState } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import AmazonProductCard from '../components/AmazonProductCard';
import { generateSearchLink } from '../utils/amazon';

// This would typically come from your backend or CMS
const featuredProducts = [
  {
    title: "LECTRON Level 2 EV Charger",
    asin: "B09BBLJ8LF",
    imageUrl: "https://m.media-amazon.com/images/I/71YqfU4d8LL._AC_SL1500_.jpg",
    price: "199.99",
    rating: 4.5,
    description: "240V 40 Amp Level 2 EV Charger, Electric Vehicle Charger",
    prime: true
  },
  {
    title: "JuiceBox 40 Smart EV Charger",
    asin: "B07WNMK7CH",
    imageUrl: "https://m.media-amazon.com/images/I/71FnNwxKBqL._AC_SL1500_.jpg",
    price: "549.00",
    rating: 4.7,
    description: "40 Amp Level 2 Electric Vehicle Charger with WiFi",
    prime: true
  },
  {
    title: "Chemical Guys Eco-Friendly Car Wash Kit",
    asin: "B07CTK4TH8",
    imageUrl: "https://m.media-amazon.com/images/I/91jHFGvzj0L._AC_SL1500_.jpg",
    price: "69.99",
    rating: 4.8,
    description: "Eco-Smart Waterless Car Wash & Wax System",
    prime: true
  }
];

export default function Products() {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      window.open(generateSearchLink(searchTerm), '_blank');
    }
  };

  return (
    <Layout>
      <Head>
        <title>Eco Vehicle Products - Amazon Store</title>
        <meta name="description" content="Browse our curated selection of eco-friendly vehicle products" />
      </Head>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Amazon Affiliate Disclosure */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-8">
          <p className="text-sm text-blue-700">
            As an Amazon Associate I earn from qualifying purchases. This helps support our mission of promoting eco-friendly transportation solutions.
          </p>
        </div>

        {/* Search Section */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="max-w-xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search eco-friendly vehicle products..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                Search
              </button>
            </div>
          </form>
        </div>

        {/* Featured Products */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {featuredProducts.map((product, index) => (
              <AmazonProductCard key={index} product={product} />
            ))}
          </div>
        </section>

        {/* Categories */}
        <section className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Product Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              'Maintenance Tools',
              'Cleaning Supplies',
              'Performance Parts',
              'Charging Equipment',
              'Interior Accessories',
              'Exterior Accessories'
            ].map((category) => (
              <a
                key={category}
                href={generateSearchLink(category + ' eco vehicle')}
                target="_blank"
                rel="noopener noreferrer sponsored"
                className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-300 text-center"
              >
                <h3 className="text-lg font-semibold text-gray-800">{category}</h3>
              </a>
            ))}
          </div>
        </section>
      </div>
    </Layout>
  );
}
