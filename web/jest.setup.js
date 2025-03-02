import '@testing-library/jest-dom';
import { jest } from '@jest/globals';

// Mock next/router
jest.unstable_mockModule('next/router', () => ({
  useRouter: () => ({
    route: '/',
    pathname: '',
    query: '',
    asPath: '',
    push: jest.fn(),
    replace: jest.fn(),
  }),
}));

// Mock next-auth
jest.unstable_mockModule('next-auth/react', () => ({
  useSession: () => ({
    data: null,
    status: 'unauthenticated',
  }),
  signIn: jest.fn(),
  signOut: jest.fn(),
  getSession: jest.fn(),
}));

// Mock MongoDB connection
jest.unstable_mockModule('lib/mongodb', () => ({
  connectToDatabase: () => ({
    db: {
      collection: () => ({
        find: jest.fn(),
        findOne: jest.fn(),
        insertOne: jest.fn(),
        updateOne: jest.fn(),
        deleteOne: jest.fn(),
      }),
    },
  }),
}));

// Mock environment variables
process.env = {
  ...process.env,
  MONGODB_URI: 'mongodb://localhost:27017/test',
  STRIPE_SECRET_KEY: 'test_stripe_key',
  NEXTAUTH_SECRET: 'test_secret',
  NEXTAUTH_URL: 'http://localhost:3000',
};
