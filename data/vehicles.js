export const vehicles = [
  {
    id: 'ev-sedan',
    name: 'EcoLuxe Sedan',
    category: 'Luxury',
    price: 39900,
    specs: {
      range: 350,
      acceleration: 4.5,
      topSpeed: 155,
      chargingTime: 30,
      power: 450,
      batteryCapacity: 100
    },
    features: [
      'Advanced Driver Assistance',
      'Premium Sound System',
      'Panoramic Glass Roof',
      'Wireless Phone Charging',
      'Over-the-air Updates',
      'Smart Climate Control'
    ],
    colors: [
      { name: 'Arctic White', hex: '#FFFFFF', price: 0 },
      { name: 'Midnight Black', hex: '#000000', price: 0 },
      { name: 'Ocean Blue', hex: '#1E3D59', price: 500 },
      { name: 'Forest Green', hex: '#2D5A27', price: 500 }
    ],
    availability: {
      inStock: true,
      estimatedDelivery: '2-4 weeks'
    },
    image: '/images/vehicles/eco-sedan.jpg'
  },
  {
    id: 'ev-suv',
    name: 'EcoXplorer SUV',
    category: 'SUV',
    price: 45900,
    specs: {
      range: 320,
      acceleration: 5.2,
      topSpeed: 135,
      chargingTime: 35,
      power: 400,
      batteryCapacity: 95
    },
    features: [
      'All-Wheel Drive',
      'Adaptive Air Suspension',
      'Third Row Seating',
      'Towing Package',
      'Adventure Mode',
      'Cargo Management System'
    ],
    colors: [
      { name: 'Summit White', hex: '#FFFFFF', price: 0 },
      { name: 'Granite Black', hex: '#000000', price: 0 },
      { name: 'Desert Sand', hex: '#C2B280', price: 500 },
      { name: 'Mountain Gray', hex: '#534B4F', price: 500 }
    ],
    availability: {
      inStock: true,
      estimatedDelivery: '3-5 weeks'
    },
    image: '/images/vehicles/eco-suv.jpg'
  },
  {
    id: 'ev-sport',
    name: 'EcoSprint GT',
    category: 'Performance',
    price: 59900,
    specs: {
      range: 300,
      acceleration: 3.1,
      topSpeed: 175,
      chargingTime: 25,
      power: 600,
      batteryCapacity: 85
    },
    features: [
      'Sport-tuned Suspension',
      'Carbon Fiber Components',
      'Track Mode',
      'Performance Brakes',
      'Active Aerodynamics',
      'Launch Control'
    ],
    colors: [
      { name: 'Racing Red', hex: '#FF0000', price: 0 },
      { name: 'Stealth Black', hex: '#000000', price: 0 },
      { name: 'Silver Arrow', hex: '#C0C0C0', price: 500 },
      { name: 'Electric Blue', hex: '#0047AB', price: 500 }
    ],
    availability: {
      inStock: false,
      estimatedDelivery: '8-10 weeks'
    },
    image: '/images/vehicles/eco-sport.jpg'
  }
];
