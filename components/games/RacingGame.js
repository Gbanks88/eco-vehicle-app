import React, { Suspense, useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Physics, useBox, usePlane } from '@react-three/cannon';
import { Environment, PerspectiveCamera, useKeyboardControls } from '@react-three/drei';
import * as THREE from 'three';

// Player Vehicle
function Vehicle({ position = [0, 1, 0] }) {
  const [ref, api] = useBox(() => ({
    mass: 1,
    position,
    args: [2, 1, 4],
    rotation: [0, Math.PI, 0],
  }));

  const [sub, get] = useKeyboardControls();
  const velocity = useRef([0, 0, 0]);

  useEffect(() => {
    const unsubscribe = api.velocity.subscribe((v) => (velocity.current = v));
    return unsubscribe;
  }, [api.velocity]);

  useFrame(() => {
    const { forward, backward, left, right } = get();
    const speed = 5;
    const turn = 2;

    // Forward/backward movement
    if (forward) {
      api.velocity.set(0, 0, -speed);
    } else if (backward) {
      api.velocity.set(0, 0, speed);
    } else {
      api.velocity.set(0, velocity.current[1], 0);
    }

    // Left/right rotation
    if (left) {
      api.angularVelocity.set(0, turn, 0);
    } else if (right) {
      api.angularVelocity.set(0, -turn, 0);
    } else {
      api.angularVelocity.set(0, 0, 0);
    }
  });

  return (
    <mesh ref={ref}>
      <boxGeometry args={[2, 1, 4]} />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}

// Track Ground
function Ground() {
  const [ref] = usePlane(() => ({
    rotation: [-Math.PI / 2, 0, 0],
    position: [0, 0, 0],
  }));

  return (
    <mesh ref={ref} receiveShadow>
      <planeGeometry args={[100, 100]} />
      <meshStandardMaterial color="#303030">
        <gridTexture args={[10, 10]} />
      </meshStandardMaterial>
    </mesh>
  );
}

// Obstacle
function Obstacle({ position }) {
  const [ref] = useBox(() => ({
    mass: 1,
    position,
    args: [2, 2, 2],
  }));

  return (
    <mesh ref={ref}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="red" />
    </mesh>
  );
}

// Main Game Component
export default function RacingGame() {
  const [started, setStarted] = useState(false);
  const [score, setScore] = useState(0);

  useEffect(() => {
    if (started) {
      const interval = setInterval(() => {
        setScore(prev => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [started]);

  return (
    <div className="w-full h-screen relative">
      {!started && (
        <div className="absolute inset-0 flex items-center justify-center z-10 bg-black bg-opacity-50">
          <button
            onClick={() => setStarted(true)}
            className="px-6 py-3 bg-green-600 text-white rounded-lg text-xl hover:bg-green-700"
          >
            Start Game
          </button>
        </div>
      )}

      <div className="absolute top-4 right-4 z-10 bg-black bg-opacity-50 p-4 rounded-lg">
        <p className="text-white text-xl">Score: {score}</p>
      </div>

      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[0, 10, 20]} />
        <Suspense fallback={null}>
          <Physics>
            <Vehicle />
            <Ground />
            {/* Add some obstacles */}
            <Obstacle position={[5, 1, -5]} />
            <Obstacle position={[-5, 1, -10]} />
            <Obstacle position={[3, 1, -15]} />
          </Physics>
          <Environment preset="sunset" />
        </Suspense>
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[10, 10, 10]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
      </Canvas>

      {/* Game Controls Help */}
      <div className="absolute bottom-4 left-4 z-10 bg-black bg-opacity-50 p-4 rounded-lg text-white">
        <h3 className="font-bold mb-2">Controls:</h3>
        <ul>
          <li>↑ or W: Forward</li>
          <li>↓ or S: Backward</li>
          <li>← or A: Turn Left</li>
          <li>→ or D: Turn Right</li>
        </ul>
      </div>
    </div>
  );
}
