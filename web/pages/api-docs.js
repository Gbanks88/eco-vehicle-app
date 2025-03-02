import { useEffect, useState } from 'react';
import Layout from '../components/admin/Layout';

export default function ApiDocs() {
  const [spec, setSpec] = useState(null);

  useEffect(() => {
    fetch('/openapi.yaml')
      .then(res => res.text())
      .then(text => setSpec(text))
      .catch(err => console.error('Error loading API spec:', err));
  }, []);

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">API Documentation</h1>
        <div className="bg-white rounded-lg shadow p-6">
          {spec ? (
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {spec}
            </pre>
          ) : (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading API documentation...</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
