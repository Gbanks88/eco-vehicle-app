import dbConnect from '../lib/mongodb';
import Vehicle from '../models/Vehicle';
import { vehicles } from '../data/vehicles';

async function seedDatabase() {
  try {
    await dbConnect();
    console.log('Connected to MongoDB...');

    // Clear existing vehicles
    await Vehicle.deleteMany({});
    console.log('Cleared existing vehicles...');

    // Insert new vehicles
    const result = await Vehicle.insertMany(vehicles);
    console.log(`Seeded ${result.length} vehicles successfully!`);

    process.exit(0);
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
}

seedDatabase();
