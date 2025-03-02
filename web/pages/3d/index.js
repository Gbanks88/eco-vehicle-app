import Head from 'next/head';
import { useState } from 'react';

export default function ThreeDModels() {
  const [selectedModel, setSelectedModel] = useState(null);

  const models = [
    {
      id: 'ev-sedan',
      name: 'Electric Sedan',
      description: 'Sleek and efficient electric sedan with advanced aerodynamics',
      thumbnail: '/models/sedan-thumb.jpg',
      modelUrl: '/models/sedan.glb'
    },
    {
      id: 'ev-suv',
      name: 'Electric SUV',
      description: 'Spacious and powerful electric SUV for family adventures',
      thumbnail: '/models/suv-thumb.jpg',
      modelUrl: '/models/suv.glb'
    },
    {
      id: 'ev-sports',
      name: 'Sports EV',
      description: 'High-performance electric sports car with cutting-edge technology',
      thumbnail: '/models/sports-thumb.jpg',
      modelUrl: '/models/sports.glb'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <Head>
        <title>3D Models - CG4L</title>
        <meta name="description" content="Interactive 3D models of our eco vehicles" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-green-800 mb-8">
          3D Vehicle Models
        </h1>

        {/* Model Viewer */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          {selectedModel ? (
            <div className="aspect-w-16 aspect-h-9">
              <div className="w-full h-full bg-gray-100 rounded flex items-center justify-center">
                {/* Replace with actual 3D viewer component */}
                <p className="text-gray-500">3D Model Viewer Coming Soon</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <h2 className="text-2xl font-semibold text-green-700 mb-4">
                Select a Model to View in 3D
              </h2>
              <p className="text-gray-600">
                Interact with our detailed 3D models to explore every angle
              </p>
            </div>
          )}
        </div>

        {/* Model Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {models.map(model => (
            <div
              key={model.id}
              onClick={() => setSelectedModel(model)}
              className={`bg-white rounded-lg shadow-lg overflow-hidden cursor-pointer transform transition-transform hover:scale-105 ${
                selectedModel?.id === model.id ? 'ring-2 ring-green-500' : ''
              }`}
            >
              <div className="h-48 bg-gray-200">
                {/* Thumbnail placeholder */}
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  {model.name} Thumbnail
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold text-green-700 mb-2">{model.name}</h3>
                <p className="text-gray-600">{model.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Features Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-green-700 mb-2">360° View</h3>
            <p className="text-gray-600">Explore vehicles from every angle</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-green-700 mb-2">Interior Tour</h3>
            <p className="text-gray-600">Step inside our vehicles virtually</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-green-700 mb-2">Color Options</h3>
            <p className="text-gray-600">Preview different color schemes</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-green-700 mb-2">Feature Highlights</h3>
            <p className="text-gray-600">Interactive feature demonstrations</p>
          </div>
        </div>
      </main>
    </div>
  );
}
