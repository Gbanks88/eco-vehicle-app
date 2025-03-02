import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import Monitoring from '../../../pages/admin/monitoring';

// Mock Chart.js
jest.mock('chart.js', () => ({
  Chart: {
    register: jest.fn()
  },
  CategoryScale: jest.fn(),
  LinearScale: jest.fn(),
  PointElement: jest.fn(),
  LineElement: jest.fn(),
  BarElement: jest.fn(),
  RadialLinearScale: jest.fn(),
  Title: jest.fn(),
  Tooltip: jest.fn(),
  Legend: jest.fn(),
  Filler: jest.fn()
}));

// Mock react-chartjs-2 components
jest.mock('react-chartjs-2', () => ({
  Line: () => <div data-testid="line-chart">Line Chart</div>,
  Bar: () => <div data-testid="bar-chart">Bar Chart</div>,
  Radar: () => <div data-testid="radar-chart">Radar Chart</div>
}));

describe('Monitoring Dashboard', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  const mockMetricsData = {
    metrics: {
      system: {
        status: 'healthy',
        metrics: {
          cpu: '50%',
          memory: '4096MB',
          uptime: '2h 30m'
        }
      },
      database: {
        status: 'healthy',
        metrics: {
          connections: 100,
          queryTime: '50ms',
          size: '1.2GB'
        }
      },
      api: {
        status: 'healthy',
        metrics: {
          requests: 1000,
          responseTime: '100ms',
          errors: 0
        }
      },
      security: {
        status: 'healthy',
        metrics: {
          threats: 0,
          failedLogins: 5,
          suspicious: 2
        }
      },
      charts: {
        systemLoad: {
          labels: ['12:00', '12:05', '12:10'],
          datasets: []
        },
        responseTimes: {
          labels: ['12:00', '12:05', '12:10'],
          datasets: []
        },
        aiAccuracy: {
          labels: ['Recommendations', 'Pricing', 'Inventory'],
          datasets: []
        },
        aiLatency: {
          labels: ['Recommendations', 'Pricing', 'Inventory'],
          datasets: []
        }
      }
    },
    alerts: [
      {
        level: 'high',
        type: 'system',
        message: 'High CPU usage',
        timestamp: new Date().toISOString()
      }
    ]
  };

  it('renders loading state initially', () => {
    global.fetch.mockImplementationOnce(() => new Promise(() => {}));

    render(<Monitoring />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders dashboard with metrics data', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockMetricsData)
    });

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByText('System Monitoring')).toBeInTheDocument();
    });

    expect(screen.getByText('System Health')).toBeInTheDocument();
    expect(screen.getByText('Database Health')).toBeInTheDocument();
    expect(screen.getByText('API Health')).toBeInTheDocument();
    expect(screen.getByText('Security Status')).toBeInTheDocument();
  });

  it('handles timeframe changes', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockMetricsData)
    });

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByText('System Monitoring')).toBeInTheDocument();
    });

    const timeframeSelect = screen.getByRole('combobox', {
      name: /timeframe/i
    });

    act(() => {
      fireEvent.change(timeframeSelect, { target: { value: '6h' } });
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('timeframe=6h')
    );
  });

  it('handles system filter changes', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockMetricsData)
    });

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByText('System Monitoring')).toBeInTheDocument();
    });

    const systemSelect = screen.getByRole('combobox', {
      name: /system/i
    });

    act(() => {
      fireEvent.change(systemSelect, { target: { value: 'database' } });
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('system=database')
    );
  });

  it('displays alerts correctly', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockMetricsData)
    });

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByText('Active Alerts')).toBeInTheDocument();
    });

    expect(screen.getByText('High CPU usage')).toBeInTheDocument();
  });

  it('refreshes data periodically', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockMetricsData)
    });

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByText('System Monitoring')).toBeInTheDocument();
    });

    act(() => {
      jest.advanceTimersByTime(60000); // 1 minute
    });

    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it('handles error states gracefully', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Failed to fetch'));

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByText('Error loading monitoring data')).toBeInTheDocument();
    });
  });

  it('displays correct status colors', async () => {
    const errorMetrics = {
      ...mockMetricsData,
      metrics: {
        ...mockMetricsData.metrics,
        system: {
          ...mockMetricsData.metrics.system,
          status: 'error'
        }
      }
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(errorMetrics)
    });

    render(<Monitoring />);

    await waitFor(() => {
      const statusElement = screen.getByText('error');
      expect(statusElement).toHaveClass('bg-red-100');
    });
  });

  it('renders all chart components', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockMetricsData)
    });

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
      expect(screen.getByTestId('radar-chart')).toBeInTheDocument();
    });
  });

  it('displays detailed metrics correctly', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockMetricsData)
    });

    render(<Monitoring />);

    await waitFor(() => {
      expect(screen.getByText('CPU')).toBeInTheDocument();
      expect(screen.getByText('50%')).toBeInTheDocument();
      expect(screen.getByText('Memory')).toBeInTheDocument();
      expect(screen.getByText('4096MB')).toBeInTheDocument();
    });
  });
});
