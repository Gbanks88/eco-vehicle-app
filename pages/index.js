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
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Eco Vehicle Project
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Promoting sustainable transportation solutions for a greener future
          </p>
          
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
