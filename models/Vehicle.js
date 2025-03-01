import mongoose from 'mongoose';

const ColorSchema = new mongoose.Schema({
  name: { type: String, required: true },
  hex: { type: String, required: true },
  price: { type: Number, default: 0 }
});

const SpecsSchema = new mongoose.Schema({
  range: { type: Number, required: true },
  acceleration: { type: Number, required: true },
  topSpeed: { type: Number, required: true },
  chargingTime: { type: Number, required: true },
  power: { type: Number, required: true },
  batteryCapacity: { type: Number, required: true }
});

const AvailabilitySchema = new mongoose.Schema({
  inStock: { type: Boolean, default: true },
  estimatedDelivery: { type: String, required: true }
});

const VehicleSchema = new mongoose.Schema({
  id: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  category: { type: String, required: true },
  price: { type: Number, required: true },
  specs: { type: SpecsSchema, required: true },
  features: [{ type: String }],
  colors: [ColorSchema],
  availability: { type: AvailabilitySchema, required: true },
  image: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Add text index for search
VehicleSchema.index({
  name: 'text',
  category: 'text',
  'features': 'text'
});

// Virtual for formatted price
VehicleSchema.virtual('formattedPrice').get(function() {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(this.price);
});

// Middleware to handle ID generation
VehicleSchema.pre('save', function(next) {
  if (this.isNew && !this.id) {
    // Generate ID based on name and category
    this.id = `${this.category.toLowerCase()}-${this.name.toLowerCase().replace(/\s+/g, '-')}`;
  }
  next();
});

export default mongoose.models.Vehicle || mongoose.model('Vehicle', VehicleSchema);
