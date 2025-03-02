import { Vehicle } from '../mongodb/models/vehicle';

export class DatabaseCache {
  constructor() {
    this.cache = new Map();
    this.stats = {
      hits: 0,
      misses: 0,
      size: 0
    };
  }

  // Get item from cache
  get(key) {
    const item = this.cache.get(key);
    
    if (!item) {
      this.stats.misses++;
      return null;
    }

    // Check if item is expired
    if (item.expiresAt && item.expiresAt < Date.now()) {
      this.cache.delete(key);
      this.stats.size--;
      this.stats.misses++;
      return null;
    }

    this.stats.hits++;
    return item.value;
  }

  // Set item in cache
  set(key, value, ttlMs = 300000) { // Default TTL: 5 minutes
    this.cache.set(key, {
      value,
      expiresAt: ttlMs ? Date.now() + ttlMs : null
    });
    this.stats.size++;
  }

  // Delete item from cache
  delete(key) {
    this.cache.delete(key);
    this.stats.size--;
  }

  // Clear entire cache
  clear() {
    this.cache.clear();
    this.stats.size = 0;
  }

  // Get cache statistics
  getStats() {
    return {
      ...this.stats,
      hitRate: this.stats.hits / (this.stats.hits + this.stats.misses) || 0
    };
  }
}

// Cache decorator for MongoDB models
export function cacheable(ttlMs) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value;
    const cache = new DatabaseCache();

    descriptor.value = async function(...args) {
      const key = `${propertyKey}:${JSON.stringify(args)}`;
      const cached = cache.get(key);

      if (cached) {
        return cached;
      }

      const result = await originalMethod.apply(this, args);
      cache.set(key, result, ttlMs);
      return result;
    };

    return descriptor;
  };
}

// Example usage with Vehicle model
export class CachedVehicleModel {
  constructor() {
    this.cache = new DatabaseCache();
  }

  @cacheable(300000) // 5 minutes
  async findById(id) {
    return Vehicle.findById(id);
  }

  @cacheable(300000)
  async findByPriceRange(min, max) {
    return Vehicle.findByPriceRange(min, max);
  }

  @cacheable(60000) // 1 minute
  async findPopular(limit) {
    return Vehicle.findPopular(limit);
  }

  // Invalidate cache when vehicle is updated
  async updateVehicle(id, data) {
    const result = await Vehicle.findByIdAndUpdate(id, data, { new: true });
    this.cache.clear(); // Clear entire cache since updates might affect multiple queries
    return result;
  }
}
