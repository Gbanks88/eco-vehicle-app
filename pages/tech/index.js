import Head from 'next/head';
import Link from 'next/link';

export default function TechnologyHub() {
  const technologies = [
    {
      id: 'battery',
      title: 'Battery Technology',
      description: 'Advanced battery systems with improved range and longevity',
      icon: '🔋',
      link: '/tech/battery'
    },
    {
      id: 'motor',
      title: 'Motor Innovation',
      description: 'High-efficiency electric motors with superior performance',
      icon: '⚡',
      link: '/tech/motor'
    },
    {
      id: 'charging',
      title: 'Charging Solutions',
      description: 'Fast charging technology and infrastructure',
      icon: '🔌',
      link: '/tech/charging'
    },
    {
      id: 'autonomous',
      title: 'Autonomous Systems',
      description: 'Self-driving capabilities and driver assistance',
      icon: '🤖',
      link: '/tech/autonomous'
    }
  ];

  const innovations = [
    {
      title: 'Extended Range Technology',
      description: 'Our latest battery technology extends vehicle range by up to 30%',
      status: 'In Development'
    },
    {
      title: 'Smart Charging Network',
      description: 'AI-powered charging optimization across our network',
      status: 'Deployed'
    },
    {
      title: 'Regenerative Braking 2.0',
      description: 'Enhanced energy recovery system for improved efficiency',
      status: 'Testing'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>Technology Hub - CG4L</title>
        <meta name="description" content="Explore our eco vehicle technology innovations" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-green-800 mb-8">
          Technology Hub
        </h1>

        {/* Featured Innovation */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-3xl font-bold text-green-700 mb-4">
                Next-Generation EV Technology
              </h2>
              <p className="text-gray-600 mb-6">
                Discover our latest innovations in eco vehicle technology, from advanced battery systems to autonomous driving capabilities.
              </p>
              <Link href="/tech/innovations" className="bg-green-600 text-white py-2 px-6 rounded hover:bg-green-700">
                Learn More
              </Link>
            </div>
            <div className="bg-gray-100 rounded-lg flex items-center justify-center">
              {/* Placeholder for technology illustration */}
              <p className="text-gray-500">Technology Preview</p>
            </div>
          </div>
        </div>

        {/* Technology Categories */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {technologies.map(tech => (
            <Link key={tech.id} href={tech.link}>
              <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
                <div className="text-4xl mb-4">{tech.icon}</div>
                <h3 className="text-xl font-semibold text-green-700 mb-2">{tech.title}</h3>
                <p className="text-gray-600">{tech.description}</p>
              </div>
            </Link>
          ))}
        </div>

        {/* Latest Innovations */}
        <h2 className="text-3xl font-bold text-green-800 mb-6">Latest Innovations</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {innovations.map((innovation, index) => (
            <div key={index} className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold text-green-700 mb-2">{innovation.title}</h3>
              <p className="text-gray-600 mb-4">{innovation.description}</p>
              <span className={`inline-block px-3 py-1 rounded-full text-sm ${
                innovation.status === 'Deployed' ? 'bg-green-100 text-green-800' :
                innovation.status === 'Testing' ? 'bg-yellow-100 text-yellow-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {innovation.status}
              </span>
            </div>
          ))}
        </div>

        {/* Research & Development */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-3xl font-bold text-green-800 mb-6">Research & Development</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold text-green-700 mb-4">Our Commitment</h3>
              <p className="text-gray-600 mb-4">
                We're dedicated to advancing eco vehicle technology through continuous research and development.
                Our team of engineers and scientists work tirelessly to create sustainable transportation solutions.
              </p>
              <Link href="/tech/research" className="text-green-600 hover:text-green-800">
                View Research Papers →
              </Link>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-green-700 mb-4">Partnerships</h3>
              <p className="text-gray-600 mb-4">
                Collaborating with leading institutions and companies to accelerate innovation in eco vehicle technology.
              </p>
              <Link href="/tech/partners" className="text-green-600 hover:text-green-800">
                Meet Our Partners →
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
