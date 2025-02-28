import Head from 'next/head';
import Link from 'next/link';

export default function EcoVehicleHome() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>CG4L - Eco Vehicle Solutions</title>
        <meta name="description" content="Sustainable transportation solutions for a greener future" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-green-800 mb-8">
          Eco Vehicle Solutions
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Featured Categories */}
          <Link href="/ev/vehicles" className="transform hover:scale-105 transition-transform">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-green-700 mb-4">Electric Vehicles</h2>
              <p className="text-gray-600">Explore our range of eco-friendly vehicles</p>
            </div>
          </Link>

          <Link href="/charging" className="transform hover:scale-105 transition-transform">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-green-700 mb-4">Charging Solutions</h2>
              <p className="text-gray-600">Find charging stations and infrastructure</p>
            </div>
          </Link>

          <Link href="/parts" className="transform hover:scale-105 transition-transform">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-green-700 mb-4">Parts & Accessories</h2>
              <p className="text-gray-600">Quality components for your eco vehicle</p>
            </div>
          </Link>

          <Link href="/service" className="transform hover:scale-105 transition-transform">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-green-700 mb-4">Service Center</h2>
              <p className="text-gray-600">Expert maintenance and support</p>
            </div>
          </Link>

          <Link href="/tech" className="transform hover:scale-105 transition-transform">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-green-700 mb-4">Technology</h2>
              <p className="text-gray-600">Latest eco vehicle innovations</p>
            </div>
          </Link>

          <Link href="/3d" className="transform hover:scale-105 transition-transform">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-green-700 mb-4">3D Models</h2>
              <p className="text-gray-600">Interactive vehicle visualizations</p>
            </div>
          </Link>
        </div>

        {/* Featured Content */}
        <section className="mt-16">
          <h2 className="text-3xl font-bold text-green-800 mb-6">Latest Updates</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold text-green-700 mb-4">Sustainability Report</h3>
              <p className="text-gray-600 mb-4">
                Discover how our eco vehicles are making a positive impact on the environment.
              </p>
              <Link href="/tech/sustainability" className="text-green-600 hover:text-green-800">
                Learn more →
              </Link>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold text-green-700 mb-4">Charging Network</h3>
              <p className="text-gray-600 mb-4">
                Explore our expanding network of charging stations across the country.
              </p>
              <Link href="/charging/network" className="text-green-600 hover:text-green-800">
                View network →
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
