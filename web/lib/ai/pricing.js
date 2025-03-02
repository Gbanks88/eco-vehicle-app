import { connectToDatabase } from '../mongodb';

export async function optimizeProductPrice(productId) {
  const { db } = await connectToDatabase();

  try {
    // Get product data
    const product = await db.collection('products').findOne({ _id: productId });
    if (!product) {
      throw new Error('Product not found');
    }

    // Get historical sales data
    const salesHistory = await db.collection('orders')
      .find({
        'items.productId': productId,
        status: 'completed',
        createdAt: {
          $gte: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) // Last 90 days
        }
      })
      .toArray();

    // Get competitor pricing data (if available)
    const competitorPrices = await db.collection('competitor_prices')
      .find({
        category: product.category,
        updatedAt: {
          $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // Last 7 days
        }
      })
      .toArray();

    // Calculate price elasticity
    const pricePoints = salesHistory.map(sale => ({
      price: sale.items.find(item => item.productId === productId).price,
      quantity: sale.items.find(item => item.productId === productId).quantity,
      date: sale.createdAt
    }));

    // Group sales by price points
    const salesByPrice = pricePoints.reduce((acc, { price, quantity }) => {
      acc[price] = (acc[price] || 0) + quantity;
      return acc;
    }, {});

    // Calculate optimal price based on various factors
    const optimizedPrice = calculateOptimalPrice({
      currentPrice: product.price,
      salesByPrice,
      competitorPrices: competitorPrices.map(cp => cp.price),
      cost: product.cost || product.price * 0.7, // Assume 30% margin if cost not available
      minMargin: 0.2 // Minimum 20% margin
    });

    // Log price optimization data
    await db.collection('price_optimization_logs').insertOne({
      productId,
      timestamp: new Date(),
      currentPrice: product.price,
      optimizedPrice,
      factors: {
        salesHistory: salesByPrice,
        competitorPrices: competitorPrices.map(cp => cp.price),
        elasticity: calculatePriceElasticity(salesByPrice)
      }
    });

    return {
      currentPrice: product.price,
      optimizedPrice,
      recommendation: generatePriceRecommendation(product.price, optimizedPrice)
    };
  } catch (error) {
    console.error('Error optimizing price:', error);
    return null;
  }
}

function calculateOptimalPrice({ currentPrice, salesByPrice, competitorPrices, cost, minMargin }) {
  // Convert sales data to arrays for analysis
  const prices = Object.keys(salesByPrice).map(Number);
  const quantities = Object.values(salesByPrice);

  // Calculate average competitor price
  const avgCompetitorPrice = competitorPrices.length > 0
    ? competitorPrices.reduce((a, b) => a + b, 0) / competitorPrices.length
    : currentPrice;

  // Calculate minimum viable price
  const minPrice = cost * (1 + minMargin);

  // Calculate price elasticity
  const elasticity = calculatePriceElasticity(salesByPrice);

  // Calculate optimal price using weighted factors
  const weights = {
    elasticity: 0.4,
    competition: 0.3,
    margin: 0.3
  };

  const elasticityOptimalPrice = prices.reduce((optimal, price) => {
    const revenue = price * salesByPrice[price];
    return revenue > optimal.revenue ? { price, revenue } : optimal;
  }, { price: currentPrice, revenue: 0 }).price;

  const optimalPrice = (
    elasticityOptimalPrice * weights.elasticity +
    avgCompetitorPrice * weights.competition +
    (cost * (1 + minMargin * 2)) * weights.margin
  );

  // Ensure price is above minimum viable price
  return Math.max(optimalPrice, minPrice);
}

function calculatePriceElasticity(salesByPrice) {
  const prices = Object.keys(salesByPrice).map(Number);
  const quantities = Object.values(salesByPrice);

  if (prices.length < 2) return 0;

  // Calculate average price and quantity
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
  const avgQuantity = quantities.reduce((a, b) => a + b, 0) / quantities.length;

  // Calculate price elasticity using midpoint formula
  const elasticity = prices.map((price, i) => {
    const quantity = quantities[i];
    const priceDiff = (price - avgPrice) / avgPrice;
    const quantityDiff = (quantity - avgQuantity) / avgQuantity;
    return priceDiff !== 0 ? quantityDiff / priceDiff : 0;
  }).reduce((a, b) => a + b, 0) / prices.length;

  return Math.abs(elasticity);
}

function generatePriceRecommendation(currentPrice, optimizedPrice) {
  const priceDiff = ((optimizedPrice - currentPrice) / currentPrice) * 100;
  const absDiff = Math.abs(priceDiff);

  if (absDiff < 5) {
    return {
      action: 'maintain',
      message: 'Current price is optimal. No change recommended.'
    };
  }

  if (priceDiff > 0) {
    return {
      action: 'increase',
      message: `Recommend increasing price by ${absDiff.toFixed(1)}% to optimize revenue.`
    };
  }

  return {
    action: 'decrease',
    message: `Recommend decreasing price by ${absDiff.toFixed(1)}% to stay competitive.`
  };
}
