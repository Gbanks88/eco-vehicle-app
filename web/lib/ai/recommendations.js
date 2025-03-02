import { connectToDatabase } from '../mongodb';

export async function generateProductRecommendations(userId, currentProductId = null) {
  const { db } = await connectToDatabase();

  try {
    // Get user's purchase history and viewed products
    const userHistory = await db.collection('user_activity').find({
      userId,
      type: { $in: ['purchase', 'view'] }
    }).toArray();

    // Get user's preferred categories and price ranges
    const categories = new Set();
    const prices = [];
    userHistory.forEach(activity => {
      if (activity.productCategory) {
        categories.add(activity.productCategory);
      }
      if (activity.productPrice) {
        prices.push(activity.productPrice);
      }
    });

    // Calculate preferred price range
    const avgPrice = prices.length > 0 
      ? prices.reduce((a, b) => a + b, 0) / prices.length 
      : 0;
    const priceRange = {
      min: avgPrice * 0.7,
      max: avgPrice * 1.3
    };

    // Build recommendation query
    const query = {
      $and: [
        // Exclude current product if provided
        currentProductId ? { _id: { $ne: currentProductId } } : {},
        // Match user's preferred categories
        categories.size > 0 ? { category: { $in: Array.from(categories) } } : {},
        // Match user's price range with some flexibility
        prices.length > 0 ? {
          price: {
            $gte: priceRange.min,
            $lte: priceRange.max
          }
        } : {},
        // Ensure product is in stock
        { inStock: true }
      ]
    };

    // Get product recommendations
    const recommendations = await db.collection('products')
      .aggregate([
        { $match: query },
        // Calculate recommendation score based on various factors
        { $addFields: {
          score: {
            $sum: [
              // Higher score for products in same category
              { $cond: [
                { $in: ['$category', Array.from(categories)] },
                10,
                0
              ]},
              // Higher score for products in similar price range
              { $cond: [
                { $and: [
                  { $gte: ['$price', priceRange.min] },
                  { $lte: ['$price', priceRange.max] }
                ]},
                5,
                0
              ]},
              // Higher score for popular products
              { $multiply: ['$totalSales', 0.1] },
              // Higher score for well-rated products
              { $multiply: ['$rating', 2] }
            ]
          }
        }},
        // Sort by recommendation score
        { $sort: { score: -1 } },
        // Limit to top recommendations
        { $limit: 10 }
      ]).toArray();

    // Log recommendation data for analysis
    await db.collection('recommendation_logs').insertOne({
      userId,
      currentProductId,
      timestamp: new Date(),
      userPreferences: {
        categories: Array.from(categories),
        priceRange
      },
      recommendedProducts: recommendations.map(r => r._id)
    });

    return recommendations;
  } catch (error) {
    console.error('Error generating recommendations:', error);
    return [];
  }
}
