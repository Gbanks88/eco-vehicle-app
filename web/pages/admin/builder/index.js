import { useState, useEffect } from 'react';
import Layout from '../../../components/admin/Layout';
import { ApplicationBuilder } from '../../../lib/builder';
import { components, componentCategories } from '../../../lib/builder/components';

export default function Builder() {
  const [builder, setBuilder] = useState(null);
  const [activeComponent, setActiveComponent] = useState(null);
  const [workflow, setWorkflow] = useState([]);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    initializeBuilder();
  }, []);

  const initializeBuilder = async () => {
    const appBuilder = new ApplicationBuilder();
    await appBuilder.initialize();
    
    // Register components
    Object.entries(components).forEach(([name, config]) => {
      appBuilder.registerComponent(name, config);
    });

    // Enable monitoring
    appBuilder.enableMonitoring({
      interval: 60000, // Collect metrics every minute
      retention: '7d' // Keep metrics for 7 days
    });

    setBuilder(appBuilder);
  };

  const handleComponentDrop = (component) => {
    setWorkflow(prev => [...prev, component]);
  };

  const handleWorkflowExecute = async () => {
    if (!workflow.length) return;

    try {
      const result = await builder.executeWorkflow('custom', workflow);
      console.log('Workflow executed:', result);
    } catch (error) {
      console.error('Workflow execution failed:', error);
    }
  };

  const updateMetrics = async () => {
    if (!builder) return;
    const newMetrics = await builder.collectMetrics();
    setMetrics(newMetrics);
  };

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Application Builder</h1>

        {/* Component Palette */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {Object.entries(componentCategories).map(([category, componentList]) => (
            <div key={category} className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold text-gray-700 mb-4 capitalize">
                {category} Components
              </h2>
              <div className="grid grid-cols-2 gap-2">
                {componentList.map(componentName => (
                  <button
                    key={componentName}
                    onClick={() => handleComponentDrop(components[componentName])}
                    className="p-2 text-sm bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 transition-colors"
                  >
                    {componentName}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Workflow Builder */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Workflow</h2>
          {workflow.length === 0 ? (
            <p className="text-gray-500">Drag components here to build your workflow</p>
          ) : (
            <div className="space-y-4">
              {workflow.map((component, index) => (
                <div
                  key={index}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <h3 className="font-medium">{component.type}</h3>
                  <p className="text-sm text-gray-500">{JSON.stringify(component.render({}))}</p>
                </div>
              ))}
              <button
                onClick={handleWorkflowExecute}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Execute Workflow
              </button>
            </div>
          )}
        </div>

        {/* Metrics Display */}
        {metrics && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(metrics.components).map(([name, componentMetrics]) => (
                <div key={name} className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium mb-2">{name}</h3>
                  <dl className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <dt>Usage:</dt>
                      <dd>{componentMetrics.usage}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Errors:</dt>
                      <dd>{componentMetrics.errors}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Avg Latency:</dt>
                      <dd>
                        {componentMetrics.latency.length
                          ? Math.round(
                              componentMetrics.latency.reduce((a, b) => a + b, 0) /
                                componentMetrics.latency.length
                            )
                          : 0}
                        ms
                      </dd>
                    </div>
                  </dl>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
