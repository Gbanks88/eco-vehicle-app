import { components, componentCategories } from '../../../lib/builder/components';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    res.status(200).json({
      components,
      categories: componentCategories
    });
  } catch (error) {
    console.error('Error in components API:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
