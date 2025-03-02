import { DatabaseManager } from '../db';
import { DataSynchronizer } from '../db/sync';
import { CachedVehicleModel } from '../db/cache';
import { QueryBuilder } from '../sql/queryBuilder';

export class AppBuilder {
  constructor() {
    this.components = new Map();
    this.routes = new Map();
    this.middlewares = [];
    this.db = new DatabaseManager();
    this.sync = null;
    this.models = new Map();
    this.config = {
      theme: null,
      api: {
        version: 'v1',
        prefix: '/api'
      },
      auth: {
        providers: [],
        sessionDuration: '24h'
      },
      cache: {
        enabled: true,
        ttl: 300000 // 5 minutes
      }
    };
  }

  // Initialize the application
  async initialize() {
    try {
      // Connect to databases
      await this.db.connect();
      this.sync = new DataSynchronizer(this.db);

      // Initialize models
      this.models.set('vehicle', new CachedVehicleModel());

      // Register default components
      this.registerCoreComponents();

      return this;
    } catch (error) {
      console.error('Failed to initialize AppBuilder:', error);
      throw error;
    }
  }

  // Register core UI components
  registerCoreComponents() {
    const coreComponents = [
      { name: 'ErrorBoundary', path: '../components/ui/ErrorBoundary' },
      { name: 'CustomTheme', path: '../components/ui/CustomTheme' },
      { name: 'ThemeCustomizer', path: '../components/ui/ThemeCustomizer' },
      { name: 'DataTable', path: '../components/ui/DataTable' },
      { name: 'Modal', path: '../components/ui/Modal' },
      { name: '404', path: '../components/ui/404' }
    ];

    coreComponents.forEach(({ name, path }) => {
      this.registerComponent(name, require(path).default);
    });
  }

  // Component Management
  registerComponent(name, component, options = {}) {
    this.components.set(name, { component, options });
    return this;
  }

  getComponent(name) {
    return this.components.get(name);
  }

  // Route Management
  registerRoute(path, handler, method = 'GET') {
    if (!this.routes.has(path)) {
      this.routes.set(path, new Map());
    }
    this.routes.get(path).set(method, handler);
    return this;
  }

  getRoute(path, method = 'GET') {
    return this.routes.get(path)?.get(method);
  }

  // Middleware Management
  use(middleware) {
    this.middlewares.push(middleware);
    return this;
  }

  // Database Operations
  async syncData(options = { batchSize: 100, delay: 1000 }) {
    try {
      await this.sync.syncVehicles(options.batchSize, options.delay);
      return this;
    } catch (error) {
      console.error('Failed to sync data:', error);
      throw error;
    }
  }

  // Configuration Management
  configure(options) {
    this.config = {
      ...this.config,
      ...options
    };
    return this;
  }

  // Theme Management
  setTheme(theme) {
    this.config.theme = theme;
    return this;
  }

  // API Management
  registerAPI(path, handlers) {
    const apiPath = `${this.config.api.prefix}/${this.config.api.version}${path}`;
    Object.entries(handlers).forEach(([method, handler]) => {
      this.registerRoute(apiPath, handler, method.toUpperCase());
    });
    return this;
  }

  // Authentication Management
  configureAuth(providers) {
    this.config.auth.providers = providers;
    return this;
  }

  // Cache Management
  configureCache(options) {
    this.config.cache = {
      ...this.config.cache,
      ...options
    };
    return this;
  }

  // Build Application
  async build() {
    try {
      // Verify database consistency
      const inconsistencies = await this.sync.verifyConsistency();
      if (inconsistencies.details.length > 0) {
        await this.sync.repairInconsistencies();
      }

      // Configure components with theme
      if (this.config.theme) {
        this.components.forEach(({ component }) => {
          if (component.configureTheme) {
            component.configureTheme(this.config.theme);
          }
        });
      }

      // Apply middlewares
      const app = this.createExpressApp();
      this.middlewares.forEach(middleware => app.use(middleware));

      // Register routes
      this.routes.forEach((methodHandlers, path) => {
        methodHandlers.forEach((handler, method) => {
          app[method.toLowerCase()](path, handler);
        });
      });

      return app;
    } catch (error) {
      console.error('Failed to build application:', error);
      throw error;
    }
  }

  // Create Express App
  createExpressApp() {
    const express = require('express');
    const app = express();

    // Basic middleware
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));

    return app;
  }

  // Cleanup
  async cleanup() {
    await this.db.close();
  }
}
