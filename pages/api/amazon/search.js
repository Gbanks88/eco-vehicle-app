import { searchProducts } from '../../../utils/amazon-api';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { q: query, category, sort, page, min_price, max_price } = req.query;

    if (!query) {
      return res.status(400).json({ error: 'Search query is required' });
    }

    const results = await searchProducts(query, {
      category,
      sortBy: sort,
      minPrice: min_price,
      maxPrice: max_price,
      page: parseInt(page) || 1
    });

    res.status(200).json(results);
  } catch (error) {
    console.error('Amazon search API error:', error);
    res.status(500).json({ error: 'Failed to search products' });
  }
}
