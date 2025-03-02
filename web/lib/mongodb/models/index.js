import mongoose from 'mongoose';

// Product Schema
const productSchema = new mongoose.Schema({
  name: { type: String, required: true },
  description: String,
  price: { type: Number, required: true },
  category: { type: String, required: true },
  imageUrl: String,
  sqlId: { type: Number, unique: true }, // Reference to SQL database
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// User Schema
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  name: String,
  sqlId: { type: Number, unique: true }, // Reference to SQL database
  preferences: {
    theme: String,
    notifications: Boolean,
    language: String
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Order Schema
const orderSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  products: [{
    productId: { type: mongoose.Schema.Types.ObjectId, ref: 'Product' },
    quantity: Number,
    price: Number
  }],
  sqlId: { type: Number, unique: true }, // Reference to SQL database
  status: String,
  totalAmount: Number,
  shippingAddress: {
    street: String,
    city: String,
    state: String,
    zipCode: String,
    country: String
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Analytics Schema
const analyticsSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  event: String,
  metadata: mongoose.Schema.Types.Mixed,
  createdAt: { type: Date, default: Date.now }
});

// Create models
export const Product = mongoose.models.Product || mongoose.model('Product', productSchema);
export const User = mongoose.models.User || mongoose.model('User', userSchema);
export const Order = mongoose.models.Order || mongoose.model('Order', orderSchema);
export const Analytics = mongoose.models.Analytics || mongoose.model('Analytics', analyticsSchema);
