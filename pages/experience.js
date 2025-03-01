import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import CarConfigurator from '../components/3d/CarConfigurator';
import RacingGame from '../components/games/RacingGame';
import CarViewer from '../components/3d/CarViewer';

export default function ExperiencePage() {
  const router = useRouter();
  const [activeExperience, setActiveExperience] = useState('configurator');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (router.query.mode) {
      setActiveExperience(router.query.mode);
    }
    setLoading(false);
  }, [router.query.mode]);

  const experiences = {
    configurator: {
      title: '3D Car Configurator',
      description: 'Customize your eco-friendly vehicle with our interactive 3D configurator.',
      features: [
        'Choose from multiple color options',
        'Customize wheel designs',
        'View vehicle specifications',
        'Interactive 3D preview'
      ],
      component: <CarConfigurator />
    },
    game: {
      title: 'Eco Racing Game',
      description: 'Experience the thrill of eco-friendly racing in our 3D game environment.',
      features: [
        'Dynamic physics-based gameplay',
        'Score tracking system',
        'Multiple obstacles',
        'Keyboard controls (Arrow keys / WASD)'
      ],
      component: <RacingGame />
    },
    viewer: {
      title: '3D Car Showroom',
      description: 'Explore our eco-friendly vehicles in stunning 3D detail.',
      features: [
        'High-quality 3D models',
        'Orbit controls for 360° viewing',
        'Detailed vehicle inspection',
        'Realistic lighting and materials'
      ],
      component: <CarViewer model="/models/eco_car.glb" />
    }
  };

  const handleExperienceChange = (key) => {
    setActiveExperience(key);
    router.push(`/experience?mode=${key}`, undefined, { shallow: true });
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-green-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
        {/* Experience Selector */}
        <div className="bg-white shadow-lg sticky top-16 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-8 py-4">
              {Object.entries(experiences).map(([key, { title }]) => (
                <button
                  key={key}
                  onClick={() => handleExperienceChange(key)}
                  className={`px-6 py-3 rounded-lg transition-all transform hover:scale-105 
                    ${activeExperience === key
                      ? 'bg-green-600 text-white shadow-lg'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-800'}`}
                >
                  {title}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Experience Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Info Panel */}
            <div className="lg:col-span-3 space-y-6">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  {experiences[activeExperience].title}
                </h2>
                <p className="text-gray-600 mb-6">
                  {experiences[activeExperience].description}
                </p>
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800">Features</h3>
                  <ul className="space-y-2">
                    {experiences[activeExperience].features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <svg
                          className="h-6 w-6 text-green-500 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        <span className="text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Help Section */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Need Help?</h3>
                <p className="text-gray-600 mb-4">
                  Having trouble with the {experiences[activeExperience].title.toLowerCase()}?
                  Check out our guide or contact support.
                </p>
                <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded-lg transition-colors">
                  View Guide
                </button>
              </div>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-9">
              <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                {experiences[activeExperience].component}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
}
