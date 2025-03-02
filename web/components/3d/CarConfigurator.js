import React, { useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera, Html } from '@react-three/drei';
import Car from './Car';

const colorOptions = [
  { name: 'Electric Blue', hex: '#0077be' },
  { name: 'Eco Green', hex: '#50c878' },
  { name: 'Solar Silver', hex: '#c0c0c0' },
  { name: 'Midnight Black', hex: '#141414' },
  { name: 'Arctic White', hex: '#ffffff' },
];

const wheelOptions = [
  { name: 'Sport', model: '/models/wheels/sport.glb' },
  { name: 'Eco', model: '/models/wheels/eco.glb' },
  { name: 'Luxury', model: '/models/wheels/luxury.glb' },
];

export default function CarConfigurator() {
  const [selectedColor, setSelectedColor] = useState(colorOptions[0]);
  const [selectedWheels, setSelectedWheels] = useState(wheelOptions[0]);
  const [activeTab, setActiveTab] = useState('color');
  const [showSpecs, setShowSpecs] = useState(false);

  const specs = {
    range: '400 miles',
    acceleration: '0-60 mph in 3.5s',
    topSpeed: '155 mph',
    power: '450 hp',
    charging: '30 min (10-80%)',
  };

  return (
    <div className="w-full h-screen relative">
      {/* 3D Viewer */}
      <div className="w-full h-full">
        <Canvas shadows>
          <PerspectiveCamera makeDefault position={[8, 3, 8]} fov={50} />
          <Suspense fallback={null}>
            <Car
              model="/models/eco_car.glb"
              color={selectedColor.hex}
              wheels={selectedWheels.model}
            />
            <Environment preset="sunset" />
          </Suspense>
          <OrbitControls
            enablePan={false}
            enableZoom={true}
            minPolarAngle={Math.PI / 4}
            maxPolarAngle={Math.PI / 2}
          />
          <ambientLight intensity={0.5} />
          <spotLight
            position={[10, 10, 10]}
            angle={0.15}
            penumbra={1}
            intensity={1}
            castShadow
          />
        </Canvas>
      </div>

      {/* Configuration Panel */}
      <div className="absolute bottom-0 left-0 right-0 bg-white bg-opacity-90 p-6 rounded-t-xl">
        <div className="max-w-4xl mx-auto">
          {/* Tabs */}
          <div className="flex mb-6 border-b">
            <button
              className={`px-6 py-2 ${activeTab === 'color' ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('color')}
            >
              Color
            </button>
            <button
              className={`px-6 py-2 ${activeTab === 'wheels' ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setActiveTab('wheels')}
            >
              Wheels
            </button>
            <button
              className={`px-6 py-2 ${showSpecs ? 'border-b-2 border-blue-500' : ''}`}
              onClick={() => setShowSpecs(!showSpecs)}
            >
              Specifications
            </button>
          </div>

          {/* Color Selection */}
          {activeTab === 'color' && (
            <div className="grid grid-cols-5 gap-4">
              {colorOptions.map((color) => (
                <button
                  key={color.hex}
                  className={`p-2 rounded-lg ${selectedColor.hex === color.hex ? 'ring-2 ring-blue-500' : ''}`}
                  onClick={() => setSelectedColor(color)}
                >
                  <div
                    className="w-full h-12 rounded-md mb-2"
                    style={{ backgroundColor: color.hex }}
                  />
                  <span className="text-sm">{color.name}</span>
                </button>
              ))}
            </div>
          )}

          {/* Wheel Selection */}
          {activeTab === 'wheels' && (
            <div className="grid grid-cols-3 gap-4">
              {wheelOptions.map((wheel) => (
                <button
                  key={wheel.name}
                  className={`p-4 rounded-lg border ${selectedWheels.name === wheel.name ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                  onClick={() => setSelectedWheels(wheel)}
                >
                  <h3 className="font-semibold">{wheel.name}</h3>
                </button>
              ))}
            </div>
          )}

          {/* Specifications */}
          {showSpecs && (
            <div className="grid grid-cols-5 gap-4">
              {Object.entries(specs).map(([key, value]) => (
                <div key={key} className="text-center">
                  <h3 className="font-semibold capitalize">{key}</h3>
                  <p>{value}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
