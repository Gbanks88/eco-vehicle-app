import { useState } from 'react';

export default function ExportMetrics({ timeframe, system }) {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState(null);

  const exportFormats = [
    { id: 'csv', name: 'CSV', icon: '📄' },
    { id: 'excel', name: 'Excel', icon: '📊' },
    { id: 'json', name: 'JSON', icon: '{ }' }
  ];

  const handleExport = async (format) => {
    try {
      setExporting(true);
      setError(null);

      const response = await fetch(
        `/api/monitoring/export?format=${format}&timeframe=${timeframe}&system=${system}`,
        { method: 'GET' }
      );

      if (!response.ok) {
        throw new Error('Export failed');
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/["']/g, '')
        : `metrics_export.${format}`;

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to export metrics');
      console.error('Export error:', err);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Export Metrics</h2>
        {exporting && (
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500 mr-2"></div>
            <span className="text-sm text-gray-500">Exporting...</span>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        {exportFormats.map(format => (
          <button
            key={format.id}
            onClick={() => handleExport(format.id)}
            disabled={exporting}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-colors
              ${exporting
                ? 'bg-gray-50 border-gray-200 cursor-not-allowed'
                : 'bg-white border-blue-100 hover:border-blue-500 hover:bg-blue-50'
              }`}
          >
            <span className="text-2xl mb-2">{format.icon}</span>
            <span className="font-medium">{format.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
