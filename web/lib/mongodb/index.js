import { MongoClient } from 'mongodb';
import mongoose from 'mongoose';

// MongoDB connection URL from environment variable
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/eco_vehicle';

// Cached connection
let cachedConnection = null;
let cachedMongoose = null;

export async function connectToMongoDB() {
  if (cachedConnection) {
    return cachedConnection;
  }

  try {
    const client = await MongoClient.connect(MONGODB_URI);
    const db = client.db();
    
    cachedConnection = { client, db };
    return cachedConnection;
  } catch (error) {
    console.error('MongoDB Connection Error:', error);
    throw error;
  }
}

export async function connectToMongoose() {
  if (cachedMongoose) {
    return cachedMongoose;
  }

  try {
    await mongoose.connect(MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    
    cachedMongoose = mongoose.connection;
    return cachedMongoose;
  } catch (error) {
    console.error('Mongoose Connection Error:', error);
    throw error;
  }
}

// Graceful shutdown
['SIGINT', 'SIGTERM'].forEach(signal => {
  process.on(signal, async () => {
    try {
      if (cachedConnection) {
        await cachedConnection.client.close();
      }
      if (cachedMongoose) {
        await cachedMongoose.close();
      }
      process.exit(0);
    } catch (error) {
      console.error('Error during shutdown:', error);
      process.exit(1);
    }
  });
});
