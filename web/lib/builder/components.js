// Pre-built components for common functionality
export const components = {
  // Data Input Components
  textInput: {
    type: 'input',
    render: ({ label, value, onChange }) => ({
      type: 'text',
      label,
      value,
      onChange
    }),
    validate: (value) => typeof value === 'string'
  },

  numberInput: {
    type: 'input',
    render: ({ label, value, onChange }) => ({
      type: 'number',
      label,
      value,
      onChange
    }),
    validate: (value) => !isNaN(value)
  },

  // Data Display Components
  dataTable: {
    type: 'display',
    render: ({ data, columns }) => ({
      type: 'table',
      data,
      columns
    }),
    validate: (data) => Array.isArray(data)
  },

  chart: {
    type: 'display',
    render: ({ type, data, options }) => ({
      type: 'chart',
      chartType: type,
      data,
      options
    }),
    validate: (data) => data && data.datasets
  },

  // Form Components
  form: {
    type: 'container',
    render: ({ children, onSubmit }) => ({
      type: 'form',
      children,
      onSubmit
    }),
    validate: () => true
  },

  // Layout Components
  grid: {
    type: 'layout',
    render: ({ children, columns }) => ({
      type: 'grid',
      children,
      columns
    }),
    validate: () => true
  },

  card: {
    type: 'layout',
    render: ({ title, content }) => ({
      type: 'card',
      title,
      content
    }),
    validate: () => true
  },

  // Integration Components
  apiEndpoint: {
    type: 'integration',
    render: ({ method, url, headers }) => ({
      type: 'api',
      method,
      url,
      headers
    }),
    validate: (config) => config.url && config.method
  },

  database: {
    type: 'integration',
    render: ({ operation, collection, query }) => ({
      type: 'database',
      operation,
      collection,
      query
    }),
    validate: (config) => config.operation && config.collection
  },

  // Monitoring Components
  metrics: {
    type: 'monitoring',
    render: ({ metric, timeframe }) => ({
      type: 'metric',
      metric,
      timeframe
    }),
    validate: (config) => config.metric
  },

  alert: {
    type: 'monitoring',
    render: ({ condition, message }) => ({
      type: 'alert',
      condition,
      message
    }),
    validate: (config) => config.condition && config.message
  }
};

// Component Categories for organization
export const componentCategories = {
  input: ['textInput', 'numberInput'],
  display: ['dataTable', 'chart'],
  container: ['form'],
  layout: ['grid', 'card'],
  integration: ['apiEndpoint', 'database'],
  monitoring: ['metrics', 'alert']
};
