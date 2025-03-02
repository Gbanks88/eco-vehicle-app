import { useState, useEffect } from 'react';
import {
  Line,
  Bar,
  Radar,
  Pie,
  Doughnut,
  PolarArea,
  Scatter
} from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function CustomCharts({ metrics }) {
  const [chartType, setChartType] = useState('line');
  const [metricKey, setMetricKey] = useState('systemLoad');
  const [customization, setCustomization] = useState({
    showLegend: true,
    fillArea: false,
    tension: 0.4,
    borderWidth: 2,
    pointRadius: 3
  });

  const chartTypes = {
    line: Line,
    bar: Bar,
    radar: Radar,
    pie: Pie,
    doughnut: Doughnut,
    polarArea: PolarArea,
    scatter: Scatter
  };

  const metricOptions = {
    systemLoad: 'System Load',
    responseTimes: 'Response Times',
    aiAccuracy: 'AI Accuracy',
    aiLatency: 'AI Latency',
    errorRates: 'Error Rates',
    throughput: 'Throughput'
  };

  const ChartComponent = chartTypes[chartType];

  const getChartData = () => {
    const baseData = metrics?.charts?.[metricKey] || {
      labels: [],
      datasets: []
    };

    return {
      ...baseData,
      datasets: baseData.datasets.map(dataset => ({
        ...dataset,
        fill: customization.fillArea,
        tension: customization.tension,
        borderWidth: customization.borderWidth,
        pointRadius: customization.pointRadius
      }))
    };
  };

  const getChartOptions = () => {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: customization.showLegend,
          position: 'top'
        },
        title: {
          display: true,
          text: metricOptions[metricKey]
        }
      }
    };

    // Add specific options based on chart type
    switch (chartType) {
      case 'line':
      case 'bar':
        return {
          ...baseOptions,
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            x: {
              grid: {
                display: false
              }
            }
          }
        };
      case 'radar':
        return {
          ...baseOptions,
          scales: {
            r: {
              beginAtZero: true,
              ticks: {
                stepSize: 20
              }
            }
          }
        };
      case 'pie':
      case 'doughnut':
      case 'polarArea':
        return {
          ...baseOptions,
          cutout: chartType === 'doughnut' ? '60%' : undefined
        };
      case 'scatter':
        return {
          ...baseOptions,
          scales: {
            x: {
              type: 'linear',
              position: 'bottom'
            }
          }
        };
      default:
        return baseOptions;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex flex-wrap gap-4 mb-6">
        {/* Chart Type Selection */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Chart Type
          </label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            {Object.keys(chartTypes).map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Metric Selection */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Metric
          </label>
          <select
            value={metricKey}
            onChange={(e) => setMetricKey(e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            {Object.entries(metricOptions).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Chart Customization */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={customization.showLegend}
              onChange={(e) => setCustomization(prev => ({
                ...prev,
                showLegend: e.target.checked
              }))}
              className="rounded text-blue-500"
            />
            <span className="text-sm text-gray-700">Show Legend</span>
          </label>
        </div>

        {(chartType === 'line') && (
          <>
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={customization.fillArea}
                  onChange={(e) => setCustomization(prev => ({
                    ...prev,
                    fillArea: e.target.checked
                  }))}
                  className="rounded text-blue-500"
                />
                <span className="text-sm text-gray-700">Fill Area</span>
              </label>
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">
                Line Tension
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={customization.tension}
                onChange={(e) => setCustomization(prev => ({
                  ...prev,
                  tension: parseFloat(e.target.value)
                }))}
                className="w-full"
              />
            </div>
          </>
        )}

        <div>
          <label className="block text-sm text-gray-700 mb-1">
            Point Size
          </label>
          <input
            type="range"
            min="0"
            max="10"
            value={customization.pointRadius}
            onChange={(e) => setCustomization(prev => ({
              ...prev,
              pointRadius: parseInt(e.target.value)
            }))}
            className="w-full"
          />
        </div>
      </div>

      {/* Chart Display */}
      <div className="h-[400px]">
        <ChartComponent
          data={getChartData()}
          options={getChartOptions()}
        />
      </div>
    </div>
  );
}
