import { connectToDatabase } from '../../../lib/mongodb';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const {
      q = '', // search query
      category,
      minPrice,
      maxPrice,
      sort = 'relevance', // relevance, price_asc, price_desc, newest
      page = 1,
      limit = 12
    } = req.query;

    const { db } = await connectToDatabase();

    // Build query
    const query = {
      $and: [
        q ? {
          $or: [
            { name: { $regex: q, $options: 'i' } },
            { description: { $regex: q, $options: 'i' } },
            { category: { $regex: q, $options: 'i' } }
          ]
        } : {},
        category ? { category } : {},
        minPrice || maxPrice ? {
          price: {
            ...(minPrice && { $gte: parseFloat(minPrice) }),
            ...(maxPrice && { $lte: parseFloat(maxPrice) })
          }
        } : {}
      ]
    };

    // Build sort
    const sortOptions = {
      relevance: { score: { $meta: 'textScore' } },
      price_asc: { price: 1 },
      price_desc: { price: -1 },
      newest: { createdAt: -1 }
    };

    // Create text index if it doesn't exist
    await db.collection('products').createIndex({
      name: 'text',
      description: 'text',
      category: 'text'
    });

    // Calculate skip for pagination
    const skip = (parseInt(page) - 1) * parseInt(limit);

    // Get total count for pagination
    const total = await db.collection('products').countDocuments(query);

    // Fetch products
    let products = await db.collection('products')
      .find(query)
      .sort(sortOptions[sort])
      .skip(skip)
      .limit(parseInt(limit))
      .toArray();

    // Get unique categories for filters
    const categories = await db.collection('products')
      .distinct('category');

    // Get price range for filters
    const priceRange = await db.collection('products').aggregate([
      {
        $group: {
          _id: null,
          minPrice: { $min: '$price' },
          maxPrice: { $max: '$price' }
        }
      }
    ]).toArray();

    // Add analytics
    await db.collection('search_analytics').insertOne({
      query: q,
      filters: {
        category,
        minPrice,
        maxPrice,
        sort
      },
      resultsCount: products.length,
      timestamp: new Date()
    });

    res.status(200).json({
      products,
      pagination: {
        total,
        pages: Math.ceil(total / parseInt(limit)),
        currentPage: parseInt(page),
        limit: parseInt(limit)
      },
      filters: {
        categories,
        priceRange: priceRange[0] || { minPrice: 0, maxPrice: 0 }
      }
    });
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: 'Failed to perform search' });
  }
}
