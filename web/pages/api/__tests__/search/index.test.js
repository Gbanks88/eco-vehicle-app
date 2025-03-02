import { createMocks } from 'node-mocks-http';
import { jest } from '@jest/globals';
import searchHandler from '../../search';

const mockDb = {
  collection: jest.fn(() => ({
    createIndex: jest.fn(),
    find: jest.fn(() => ({
      sort: jest.fn(() => ({
        skip: jest.fn(() => ({
          limit: jest.fn(() => ({
            toArray: jest.fn(() => Promise.resolve([])),
          })),
        })),
      })),
    })),
    countDocuments: jest.fn(() => Promise.resolve(0)),
    distinct: jest.fn(() => Promise.resolve([])),
    aggregate: jest.fn(() => ({
      toArray: jest.fn(() => Promise.resolve([])),
    })),
    insertOne: jest.fn(),
  })),
};

describe('Search API', () => {
  const mockProducts = [
    {
      _id: '1',
      name: 'Electric Car Model X',
      description: 'High-performance electric vehicle',
      category: 'vehicles',
      price: 45000,
      createdAt: new Date('2025-01-01'),
    },
    {
      _id: '2',
      name: 'Charging Station',
      description: 'Fast charging station for EVs',
      category: 'accessories',
      price: 1200,
      createdAt: new Date('2025-01-02'),
    },
  ];

  const mockDb = {
    collection: jest.fn(() => ({
      createIndex: jest.fn(),
      find: jest.fn(() => ({
        sort: jest.fn(() => ({
          skip: jest.fn(() => ({
            limit: jest.fn(() => ({
              toArray: jest.fn(() => Promise.resolve(mockProducts)),
            })),
          })),
        })),
      })),
      countDocuments: jest.fn(() => Promise.resolve(2)),
      distinct: jest.fn(() => Promise.resolve(['vehicles', 'accessories'])),
      aggregate: jest.fn(() => ({
        toArray: jest.fn(() => Promise.resolve([
          { minPrice: 1200, maxPrice: 45000 },
        ])),
      })),
      insertOne: jest.fn(),
    })),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    connectToDatabase.mockResolvedValue({ db: mockDb });
  });

  it('returns 405 for non-GET requests', async () => {
    const { req, res } = createMocks({
      method: 'POST',
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(405);
  });

  it('performs basic search without filters', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        q: '',
        page: '1',
        limit: '12',
      },
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    
    const data = JSON.parse(res._getData());
    expect(data.products).toHaveLength(2);
    expect(data.pagination).toEqual({
      total: 2,
      pages: 1,
      currentPage: 1,
      limit: 12,
    });
    expect(data.filters.categories).toEqual(['vehicles', 'accessories']);
    expect(data.filters.priceRange).toEqual({
      minPrice: 1200,
      maxPrice: 45000,
    });
  });

  it('applies search query filter', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        q: 'electric',
      },
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(mockDb.collection().find).toHaveBeenCalledWith(
      expect.objectContaining({
        $and: expect.arrayContaining([
          {
            $or: [
              { name: { $regex: 'electric', $options: 'i' } },
              { description: { $regex: 'electric', $options: 'i' } },
              { category: { $regex: 'electric', $options: 'i' } },
            ],
          },
        ]),
      })
    );
  });

  it('applies category filter', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        category: 'vehicles',
      },
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(mockDb.collection().find).toHaveBeenCalledWith(
      expect.objectContaining({
        $and: expect.arrayContaining([
          { category: 'vehicles' },
        ]),
      })
    );
  });

  it('applies price range filter', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        minPrice: '1000',
        maxPrice: '50000',
      },
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(mockDb.collection().find).toHaveBeenCalledWith(
      expect.objectContaining({
        $and: expect.arrayContaining([
          {
            price: {
              $gte: 1000,
              $lte: 50000,
            },
          },
        ]),
      })
    );
  });

  it('applies sorting', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        sort: 'price_asc',
      },
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(mockDb.collection().find().sort).toHaveBeenCalledWith({
      price: 1,
    });
  });

  it('handles pagination', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        page: '2',
        limit: '10',
      },
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(mockDb.collection().find().sort().skip).toHaveBeenCalledWith(10);
    expect(mockDb.collection().find().sort().skip().limit).toHaveBeenCalledWith(10);
  });

  it('tracks search analytics', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        q: 'electric',
        category: 'vehicles',
        minPrice: '1000',
        maxPrice: '50000',
        sort: 'price_asc',
      },
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(mockDb.collection().insertOne).toHaveBeenCalledWith(
      expect.objectContaining({
        query: 'electric',
        filters: {
          category: 'vehicles',
          minPrice: '1000',
          maxPrice: '50000',
          sort: 'price_asc',
        },
        resultsCount: 2,
        timestamp: expect.any(Date),
      })
    );
  });

  it('handles database errors gracefully', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    });

    mockDb.collection().find.mockImplementationOnce(() => {
      throw new Error('Database error');
    });

    await searchHandler(req, res);

    expect(res._getStatusCode()).toBe(500);
    expect(JSON.parse(res._getData())).toEqual({
      error: 'Failed to perform search',
    });
  });
});
