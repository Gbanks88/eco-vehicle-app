import mongoose from 'mongoose';

const vehicleSchema = new mongoose.Schema({
  model: { type: String, required: true },
  year: { type: Number, required: true },
  type: { type: String, enum: ['electric', 'hybrid', 'plugin_hybrid'], required: true },
  manufacturer: { type: String, required: true },
  sqlId: { type: Number, unique: true },
  specs: {
    range: { type: Number }, // miles per charge/tank
    batteryCapacity: { type: Number }, // kWh
    chargingTime: { type: Number }, // hours
    acceleration: { type: Number }, // 0-60 mph in seconds
    topSpeed: { type: Number }, // mph
    power: { type: Number }, // hp
    torque: { type: Number } // lb-ft
  },
  features: [{
    name: String,
    category: String,
    description: String
  }],
  pricing: {
    base: { type: Number, required: true },
    options: [{
      name: String,
      price: Number
    }],
    currency: { type: String, default: 'USD' }
  },
  availability: {
    status: { type: String, enum: ['in_stock', 'pre_order', 'out_of_stock'] },
    quantity: Number,
    estimatedDelivery: Date
  },
  media: {
    images: [{
      url: String,
      type: { type: String, enum: ['exterior', 'interior', '360', 'detail'] },
      alt: String
    }],
    videos: [{
      url: String,
      type: String,
      title: String
    }]
  },
  performance: {
    efficiency: {
      city: Number, // MPGe or MPG
      highway: Number,
      combined: Number
    },
    emissions: {
      co2: Number, // g/km
      rating: String
    }
  },
  maintenance: [{
    type: String,
    intervalMiles: Number,
    estimatedCost: Number,
    description: String
  }],
  reviews: [{
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    rating: { type: Number, min: 1, max: 5 },
    title: String,
    content: String,
    pros: [String],
    cons: [String],
    verified: { type: Boolean, default: false },
    date: { type: Date, default: Date.now }
  }],
  analytics: {
    viewCount: { type: Number, default: 0 },
    favoriteCount: { type: Number, default: 0 },
    testDriveRequests: { type: Number, default: 0 },
    purchaseConversionRate: { type: Number, default: 0 }
  },
  metadata: {
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now },
    lastSync: { type: Date },
    version: { type: Number, default: 1 }
  }
});

// Indexes
vehicleSchema.index({ model: 1, year: 1 });
vehicleSchema.index({ type: 1 });
vehicleSchema.index({ 'pricing.base': 1 });
vehicleSchema.index({ 'availability.status': 1 });
vehicleSchema.index({ 'analytics.viewCount': -1 });

// Middleware
vehicleSchema.pre('save', function(next) {
  this.metadata.updatedAt = new Date();
  next();
});

// Virtual for full name
vehicleSchema.virtual('fullName').get(function() {
  return `${this.year} ${this.manufacturer} ${this.model}`;
});

// Methods
vehicleSchema.methods.updateAnalytics = async function(action) {
  const updates = {};
  switch (action) {
    case 'view':
      updates['analytics.viewCount'] = this.analytics.viewCount + 1;
      break;
    case 'favorite':
      updates['analytics.favoriteCount'] = this.analytics.favoriteCount + 1;
      break;
    case 'testDrive':
      updates['analytics.testDriveRequests'] = this.analytics.testDriveRequests + 1;
      break;
  }
  return this.model('Vehicle').updateOne({ _id: this._id }, { $set: updates });
};

// Statics
vehicleSchema.statics.findByPriceRange = function(min, max) {
  return this.find({
    'pricing.base': { $gte: min, $lte: max }
  }).sort('pricing.base');
};

vehicleSchema.statics.findPopular = function(limit = 10) {
  return this.find()
    .sort({ 'analytics.viewCount': -1 })
    .limit(limit);
};

export const Vehicle = mongoose.models.Vehicle || mongoose.model('Vehicle', vehicleSchema);
