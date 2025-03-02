import mongoose from 'mongoose';
import { config } from 'dotenv';

// Load environment variables
config();

const MONGODB_URI = process.env.MONGODB_URI;

if (!MONGODB_URI) {
  throw new Error('Please define the MONGODB_URI environment variable inside .env');
}

let cached = global.mongoose;

if (!cached) {
  cached = global.mongoose = { conn: null, promise: null };
}

// Connection options
const options = {
  bufferCommands: false,
  maxPoolSize: 10,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
  family: 4,
  retryWrites: true,
  retryReads: true
};

async function dbConnect() {
  if (cached.conn) {
    console.log('Using cached MongoDB connection');
    return cached.conn;
  }

  try {
    if (!cached.promise) {
      console.log('Creating new MongoDB connection...');
      cached.promise = mongoose.connect(MONGODB_URI, options);

      // Handle connection events
      mongoose.connection.on('connected', () => {
        console.log('MongoDB connected successfully');
      });

      mongoose.connection.on('error', (err) => {
        console.error('MongoDB connection error:', err);
        cached.promise = null;
      });

      mongoose.connection.on('disconnected', () => {
        console.log('MongoDB disconnected');
        cached.promise = null;
      });
    }

    cached.conn = await cached.promise;
    return cached.conn;
  } catch (error) {
    console.error('MongoDB connection failed:', error);
    cached.promise = null;
    throw error;
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  try {
    await mongoose.connection.close();
    console.log('MongoDB connection closed through app termination');
    process.exit(0);
  } catch (err) {
    console.error('Error closing MongoDB connection:', err);
    process.exit(1);
  }
});

export { dbConnect };

export async function connectToDatabase() {
  const conn = await dbConnect();
  return { db: conn.connection.db };
}
