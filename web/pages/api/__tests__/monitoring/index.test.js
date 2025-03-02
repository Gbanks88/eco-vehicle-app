import { createMocks } from 'node-mocks-http';
import handler from '../../monitoring';
import { monitorSystemHealth } from '../../../../lib/monitoring';

jest.mock('../../../../lib/monitoring');

describe('Monitoring API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('returns 405 for non-GET requests', async () => {
    const { req, res } = createMocks({
      method: 'POST',
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(405);
    expect(JSON.parse(res._getData())).toEqual({
      error: 'Method not allowed'
    });
  });

  it('returns monitoring data with default parameters', async () => {
    const mockHealthData = {
      status: 'healthy',
      metrics: [
        {
          type: 'system',
          timestamp: new Date(),
          metrics: {
            cpu: { usage: 50 },
            memory: { used: 4096 },
            uptime: 3600
          }
        }
      ],
      alerts: []
    };

    monitorSystemHealth.mockResolvedValueOnce(mockHealthData);

    const { req, res } = createMocks({
      method: 'GET',
      query: {}
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    const data = JSON.parse(res._getData());
    expect(data).toHaveProperty('metrics');
    expect(data).toHaveProperty('alerts');
  });

  it('handles different timeframes correctly', async () => {
    const mockHealthData = {
      status: 'healthy',
      metrics: [
        {
          type: 'system',
          timestamp: new Date(),
          metrics: {
            cpu: { usage: 50 },
            memory: { used: 4096 }
          }
        }
      ],
      alerts: []
    };

    monitorSystemHealth.mockResolvedValueOnce(mockHealthData);

    const { req, res } = createMocks({
      method: 'GET',
      query: { timeframe: '6h' }
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    const data = JSON.parse(res._getData());
    expect(data.metrics).toBeDefined();
  });

  it('handles system filtering correctly', async () => {
    const mockHealthData = {
      status: 'healthy',
      metrics: [
        {
          type: 'database',
          timestamp: new Date(),
          metrics: {
            connections: 100,
            queryTime: 50
          }
        }
      ],
      alerts: []
    };

    monitorSystemHealth.mockResolvedValueOnce(mockHealthData);

    const { req, res } = createMocks({
      method: 'GET',
      query: { system: 'database' }
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    const data = JSON.parse(res._getData());
    expect(data.metrics.database).toBeDefined();
  });

  it('handles errors gracefully', async () => {
    monitorSystemHealth.mockRejectedValueOnce(new Error('Test error'));

    const { req, res } = createMocks({
      method: 'GET',
      query: {}
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(500);
    expect(JSON.parse(res._getData())).toEqual({
      error: 'Internal server error'
    });
  });
});
