export class ResourceManager {
  constructor() {
    this.resources = new Map();
    this.dependencies = new Map();
    this.loadOrder = [];
  }

  // Register a resource with its dependencies
  register(name, resource, dependencies = []) {
    this.resources.set(name, resource);
    this.dependencies.set(name, dependencies);
    return this;
  }

  // Calculate load order based on dependencies
  calculateLoadOrder() {
    const visited = new Set();
    const temp = new Set();
    this.loadOrder = [];

    const visit = (name) => {
      if (temp.has(name)) {
        throw new Error(`Circular dependency detected: ${name}`);
      }
      if (visited.has(name)) return;

      temp.add(name);
      const deps = this.dependencies.get(name) || [];
      deps.forEach(visit);
      temp.delete(name);
      visited.add(name);
      this.loadOrder.push(name);
    };

    this.resources.forEach((_, name) => {
      if (!visited.has(name)) {
        visit(name);
      }
    });
  }

  // Load all resources in correct order
  async loadAll() {
    try {
      this.calculateLoadOrder();
      
      for (const name of this.loadOrder) {
        const resource = this.resources.get(name);
        if (typeof resource.load === 'function') {
          await resource.load();
        }
      }
    } catch (error) {
      console.error('Failed to load resources:', error);
      throw error;
    }
  }

  // Get a loaded resource
  get(name) {
    return this.resources.get(name);
  }

  // Check if all required resources are loaded
  validateResources(required) {
    const missing = required.filter(name => !this.resources.has(name));
    if (missing.length > 0) {
      throw new Error(`Missing required resources: ${missing.join(', ')}`);
    }
  }
}

// Resource types
export class DatabaseResource {
  constructor(config) {
    this.config = config;
    this.connection = null;
  }

  async load() {
    // Implement database connection
  }

  async cleanup() {
    if (this.connection) {
      await this.connection.close();
    }
  }
}

export class APIResource {
  constructor(config) {
    this.config = config;
    this.endpoints = new Map();
  }

  register(path, handler, method = 'GET') {
    if (!this.endpoints.has(path)) {
      this.endpoints.set(path, new Map());
    }
    this.endpoints.get(path).set(method, handler);
  }

  async load() {
    // Implement API setup
  }
}

export class UIResource {
  constructor(config) {
    this.config = config;
    this.components = new Map();
  }

  register(name, component) {
    this.components.set(name, component);
  }

  async load() {
    // Implement UI setup
  }
}

export class AuthResource {
  constructor(config) {
    this.config = config;
    this.providers = new Map();
  }

  register(name, provider) {
    this.providers.set(name, provider);
  }

  async load() {
    // Implement auth setup
  }
}

export class CacheResource {
  constructor(config) {
    this.config = config;
    this.store = new Map();
  }

  async load() {
    // Implement cache setup
  }

  set(key, value, ttl) {
    this.store.set(key, {
      value,
      expires: Date.now() + ttl
    });
  }

  get(key) {
    const item = this.store.get(key);
    if (!item) return null;
    if (item.expires < Date.now()) {
      this.store.delete(key);
      return null;
    }
    return item.value;
  }
}

export class FileSystemResource {
  constructor(config) {
    this.config = config;
    this.watchers = new Map();
  }

  async load() {
    // Implement file system setup
  }

  watch(path, callback) {
    // Implement file watching
  }

  async cleanup() {
    this.watchers.forEach(watcher => watcher.close());
  }
}
