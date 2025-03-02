import { monitorSystemHealth } from '../index';
import { connectToDatabase } from '../../mongodb';

jest.mock('../../mongodb');

describe('Monitoring System', () => {
  let mockDb;

  beforeEach(() => {
    mockDb = {
      admin: jest.fn().mockReturnValue({
        ping: jest.fn().mockResolvedValue(true)
      }),
      collection: jest.fn().mockReturnValue({
        stats: jest.fn().mockResolvedValue({
          size: 1000,
          count: 100,
          avgObjSize: 100
        }),
        countDocuments: jest.fn().mockResolvedValue(10),
        find: jest.fn().mockReturnValue({
          toArray: jest.fn().mockResolvedValue([])
        }),
        findOne: jest.fn().mockResolvedValue(null)
      }),
      command: jest.fn().mockResolvedValue({
        metrics: {
          queryExecutor: {
            scanned: 1000
          }
        }
      })
    };

    connectToDatabase.mockResolvedValue({ db: mockDb });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('returns system health data', async () => {
    const result = await monitorSystemHealth();

    expect(result).toHaveProperty('status');
    expect(result).toHaveProperty('metrics');
    expect(result).toHaveProperty('alerts');
  });

  it('checks database health', async () => {
    const result = await monitorSystemHealth();

    expect(mockDb.admin().ping).toHaveBeenCalled();
    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'database'
      })
    );
  });

  it('checks API health', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      status: 200
    });

    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'api'
      })
    );

    delete global.fetch;
  });

  it('checks system metrics', async () => {
    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'system',
        metrics: expect.objectContaining({
          memory: expect.any(Object),
          cpu: expect.any(Object),
          eventLoop: expect.any(Object)
        })
      })
    );
  });

  it('checks AI systems health', async () => {
    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'ai_systems'
      })
    );
  });

  it('checks security metrics', async () => {
    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'security'
      })
    );
  });

  it('generates alerts for critical issues', async () => {
    mockDb.collection().stats.mockRejectedValueOnce(new Error('Database error'));

    const result = await monitorSystemHealth();

    expect(result.alerts).toContainEqual(
      expect.objectContaining({
        level: 'critical',
        type: 'database'
      })
    );
  });

  it('handles database connection failures', async () => {
    mockDb.admin().ping.mockRejectedValueOnce(new Error('Connection failed'));

    const result = await monitorSystemHealth();

    expect(result.alerts).toContainEqual(
      expect.objectContaining({
        level: 'critical',
        type: 'database',
        message: expect.stringContaining('Database connection failed')
      })
    );
  });

  it('handles high memory usage', async () => {
    const mockMemoryUsage = {
      heapUsed: 900,
      heapTotal: 1000,
      external: 100
    };
    jest.spyOn(process, 'memoryUsage').mockReturnValue(mockMemoryUsage);

    const result = await monitorSystemHealth();

    expect(result.alerts).toContainEqual(
      expect.objectContaining({
        level: 'high',
        type: 'system',
        message: expect.stringContaining('High memory usage')
      })
    );
  });

  it('handles high event loop lag', async () => {
    jest.useFakeTimers();
    const result = await monitorSystemHealth();
    jest.runAllTimers();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'system',
        metrics: expect.objectContaining({
          eventLoop: expect.any(Object)
        })
      })
    );
  });

  it('checks recommendation system accuracy', async () => {
    mockDb.collection().countDocuments.mockResolvedValueOnce(1000);

    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'ai_systems',
        systems: expect.objectContaining({
          recommendations: expect.any(Object)
        })
      })
    );
  });

  it('checks price optimization system', async () => {
    mockDb.collection().countDocuments.mockResolvedValueOnce(500);

    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'ai_systems',
        systems: expect.objectContaining({
          pricing: expect.any(Object)
        })
      })
    );
  });

  it('checks inventory prediction system', async () => {
    mockDb.collection().countDocuments.mockResolvedValueOnce(300);

    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'ai_systems',
        systems: expect.objectContaining({
          inventory: expect.any(Object)
        })
      })
    );
  });

  it('checks customer segmentation system', async () => {
    mockDb.collection().countDocuments.mockResolvedValueOnce(200);

    const result = await monitorSystemHealth();

    expect(result.metrics).toContainEqual(
      expect.objectContaining({
        type: 'ai_systems',
        systems: expect.objectContaining({
          segmentation: expect.any(Object)
        })
      })
    );
  });

  it('handles security events correctly', async () => {
    mockDb.collection().countDocuments
      .mockResolvedValueOnce(150) // failed logins
      .mockResolvedValueOnce(50)  // rate limit events
      .mockResolvedValueOnce(5);  // suspicious activities

    const result = await monitorSystemHealth();

    expect(result.alerts).toContainEqual(
      expect.objectContaining({
        level: 'high',
        type: 'security'
      })
    );
  });

  it('processes alerts correctly', async () => {
    const criticalError = new Error('Critical system error');
    mockDb.admin().ping.mockRejectedValueOnce(criticalError);

    const result = await monitorSystemHealth();

    expect(result.alerts).toContainEqual(
      expect.objectContaining({
        level: 'critical',
        message: expect.any(String)
      })
    );
  });

  it('logs errors correctly', async () => {
    const testError = new Error('Test error');
    mockDb.collection().stats.mockRejectedValueOnce(testError);

    await monitorSystemHealth();

    expect(mockDb.collection).toHaveBeenCalledWith('error_logs');
  });
});
