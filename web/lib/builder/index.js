import { connectToDatabase } from '../mongodb';

export class ApplicationBuilder {
  constructor() {
    this.components = new Map();
    this.workflows = new Map();
    this.integrations = new Map();
    this.monitoring = null;
  }

  async initialize() {
    const { db } = await connectToDatabase();
    this.db = db;
    return this;
  }

  // Component Management
  registerComponent(name, config) {
    this.components.set(name, {
      ...config,
      metrics: {
        usage: 0,
        errors: 0,
        latency: []
      }
    });
    return this;
  }

  async getComponent(name) {
    const component = this.components.get(name);
    if (!component) {
      throw new Error(`Component ${name} not found`);
    }
    return component;
  }

  // Workflow Management
  registerWorkflow(name, steps) {
    this.workflows.set(name, {
      steps,
      metrics: {
        executions: 0,
        failures: 0,
        avgDuration: 0
      }
    });
    return this;
  }

  async executeWorkflow(name, context) {
    const workflow = this.workflows.get(name);
    if (!workflow) {
      throw new Error(`Workflow ${name} not found`);
    }

    const startTime = Date.now();
    const executionId = await this.logWorkflowStart(name);

    try {
      let result = context;
      for (const step of workflow.steps) {
        result = await this.executeStep(step, result);
      }

      await this.logWorkflowSuccess(executionId, Date.now() - startTime);
      return result;
    } catch (error) {
      await this.logWorkflowFailure(executionId, error);
      throw error;
    }
  }

  // Integration Management
  registerIntegration(name, config) {
    this.integrations.set(name, {
      ...config,
      metrics: {
        calls: 0,
        errors: 0,
        latency: []
      }
    });
    return this;
  }

  async executeIntegration(name, params) {
    const integration = this.integrations.get(name);
    if (!integration) {
      throw new Error(`Integration ${name} not found`);
    }

    const startTime = Date.now();
    try {
      const result = await integration.handler(params);
      await this.logIntegrationSuccess(name, Date.now() - startTime);
      return result;
    } catch (error) {
      await this.logIntegrationError(name, error);
      throw error;
    }
  }

  // Monitoring Integration
  enableMonitoring(config) {
    this.monitoring = {
      enabled: true,
      config,
      metrics: {
        components: new Map(),
        workflows: new Map(),
        integrations: new Map()
      }
    };
    return this;
  }

  // Metric Collection
  async collectMetrics() {
    if (!this.monitoring?.enabled) return null;

    const metrics = {
      timestamp: new Date(),
      components: {},
      workflows: {},
      integrations: {}
    };

    // Collect component metrics
    for (const [name, component] of this.components) {
      metrics.components[name] = component.metrics;
    }

    // Collect workflow metrics
    for (const [name, workflow] of this.workflows) {
      metrics.workflows[name] = workflow.metrics;
    }

    // Collect integration metrics
    for (const [name, integration] of this.integrations) {
      metrics.integrations[name] = integration.metrics;
    }

    await this.storeMetrics(metrics);
    return metrics;
  }

  // Database Operations
  async logWorkflowStart(name) {
    const execution = {
      workflow: name,
      status: 'running',
      startTime: new Date(),
      context: {}
    };

    const result = await this.db.collection('workflow_executions')
      .insertOne(execution);

    return result.insertedId;
  }

  async logWorkflowSuccess(executionId, duration) {
    await this.db.collection('workflow_executions')
      .updateOne(
        { _id: executionId },
        {
          $set: {
            status: 'completed',
            endTime: new Date(),
            duration
          }
        }
      );
  }

  async logWorkflowFailure(executionId, error) {
    await this.db.collection('workflow_executions')
      .updateOne(
        { _id: executionId },
        {
          $set: {
            status: 'failed',
            endTime: new Date(),
            error: error.message
          }
        }
      );
  }

  async logIntegrationSuccess(name, duration) {
    const integration = this.integrations.get(name);
    integration.metrics.calls++;
    integration.metrics.latency.push(duration);

    // Keep only last 100 latency measurements
    if (integration.metrics.latency.length > 100) {
      integration.metrics.latency.shift();
    }
  }

  async logIntegrationError(name, error) {
    const integration = this.integrations.get(name);
    integration.metrics.errors++;
    await this.db.collection('integration_errors').insertOne({
      integration: name,
      timestamp: new Date(),
      error: error.message
    });
  }

  async storeMetrics(metrics) {
    await this.db.collection('builder_metrics').insertOne(metrics);
  }

  // Helper Methods
  async executeStep(step, context) {
    const startTime = Date.now();
    try {
      const result = await step.handler(context);
      this.logStepSuccess(step.name, Date.now() - startTime);
      return result;
    } catch (error) {
      this.logStepError(step.name, error);
      throw error;
    }
  }

  async logStepSuccess(name, duration) {
    await this.db.collection('step_executions').insertOne({
      step: name,
      status: 'completed',
      timestamp: new Date(),
      duration
    });
  }

  async logStepError(name, error) {
    await this.db.collection('step_executions').insertOne({
      step: name,
      status: 'failed',
      timestamp: new Date(),
      error: error.message
    });
  }
}
