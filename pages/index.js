import Head from 'next/head';
import Layout from '../components/Layout';
import Link from 'next/link';

export default function Home() {
  return (
    <Layout>
      <Head>
        <title>Eco Vehicle Project - Home</title>
        <meta name="description" content="Welcome to the Eco Vehicle Project - Promoting sustainable transportation solutions" />
      </Head>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 mb-4">
            Drive the Future of <span className="text-green-600">Sustainable Transportation</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Join our community of eco-conscious drivers making a difference, one mile at a time
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            <div className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Eco Products</h2>
              <p className="text-gray-600">Discover our curated selection of sustainable vehicle accessories and maintenance products.</p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Expert Blog</h2>
              <p className="text-gray-600">Stay informed with our latest articles on eco-friendly vehicle maintenance and tips.</p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Community</h2>
              <p className="text-gray-600">Connect with other eco-conscious drivers and share your sustainable journey.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-12">
            <Link href="/products" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Shop Eco Products</h2>
              <p className="text-gray-600">Browse our curated selection of eco-friendly vehicle products</p>
            </Link>

            <Link href="/about" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">About Us</h2>
              <p className="text-gray-600">Learn about our mission and commitment to sustainability</p>
            </Link>

            <Link href="/environmental" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Environmental Impact</h2>
              <p className="text-gray-600">Discover how we're making a difference</p>
            </Link>
          </div>
        </div>
      </main>
    </Layout>
  );
}
