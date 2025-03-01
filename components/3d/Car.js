import React, { useRef, useEffect } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export default function Car({ model, color, ...props }) {
  const group = useRef();
  const { scene, animations } = useGLTF(model);
  const { actions } = useAnimations(animations, group);

  // Clone the scene to avoid modifying the cached original
  const clonedScene = React.useMemo(() => {
    const clone = scene.clone(true);
    clone.traverse((node) => {
      if (node.isMesh) {
        // Apply color to car body materials
        if (node.name.toLowerCase().includes('body')) {
          node.material = new THREE.MeshPhysicalMaterial({
            color: new THREE.Color(color),
            metalness: 0.8,
            roughness: 0.2,
            clearcoat: 1.0,
            clearcoatRoughness: 0.2
          });
        }
        // Enhanced materials for other parts
        else if (node.name.toLowerCase().includes('glass')) {
          node.material = new THREE.MeshPhysicalMaterial({
            transparent: true,
            opacity: 0.4,
            color: '#ffffff',
            metalness: 0,
            roughness: 0,
            transmission: 1.0
          });
        }
        else if (node.name.toLowerCase().includes('wheel')) {
          node.material = new THREE.MeshStandardMaterial({
            color: '#1a1a1a',
            metalness: 0.8,
            roughness: 0.3
          });
        }
      }
    });
    return clone;
  }, [scene, color]);

  // Wheel rotation animation
  useFrame((state) => {
    clonedScene.traverse((node) => {
      if (node.name.toLowerCase().includes('wheel')) {
        node.rotation.x += 0.01;
      }
    });
  });

  return (
    <group ref={group} {...props}>
      <primitive object={clonedScene} />
    </group>
  );
}

// Preload the model
useGLTF.preload('/models/eco_car.glb');
