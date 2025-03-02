import { connectToDatabase } from './mongodb';
import bcrypt from 'bcryptjs';

export async function verifyPassword(password, hashedPassword) {
  return bcrypt.compare(password, hashedPassword);
}

export async function verifyCredentials(email, password) {
  const { db } = await connectToDatabase();
  
  const user = await db.collection('users').findOne({ email });
  
  if (!user) {
    return null;
  }

  const isValid = await bcrypt.compare(password, user.password);
  
  if (!isValid) {
    return null;
  }

  return {
    id: user._id.toString(),
    name: user.name,
    email: user.email,
    role: user.role
  };
}

export async function createUser(userData) {
  const { db } = await connectToDatabase();
  
  const existingUser = await db.collection('users').findOne({ email: userData.email });
  
  if (existingUser) {
    throw new Error('User already exists');
  }

  const hashedPassword = await bcrypt.hash(userData.password, 12);
  
  const result = await db.collection('users').insertOne({
    ...userData,
    password: hashedPassword,
    createdAt: new Date()
  });

  return {
    id: result.insertedId.toString(),
    name: userData.name,
    email: userData.email,
    role: userData.role
  };
}

export async function getUserById(userId) {
  const { db } = await connectToDatabase();
  
  const user = await db.collection('users').findOne({ _id: userId });
  
  if (!user) {
    return null;
  }

  return {
    id: user._id.toString(),
    name: user.name,
    email: user.email,
    role: user.role
  };
}
