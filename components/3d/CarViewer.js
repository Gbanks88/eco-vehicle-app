import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera } from '@react-three/drei';
import Car from './Car';

export default function CarViewer({ model, color = '#ffffff' }) {
  return (
    <div className="w-full h-[600px] relative">
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[8, 3, 8]} fov={50} />
        <Suspense fallback={null}>
          <Car model={model} color={color} />
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
  );
}
