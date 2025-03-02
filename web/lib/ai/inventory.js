import { connectToDatabase } from '../mongodb';

export async function predictInventoryNeeds(productId = null, daysAhead = 30) {
  const { db } = await connectToDatabase();

  try {
    const query = productId ? { _id: productId } : {};
    const products = await db.collection('products').find(query).toArray();

    const predictions = await Promise.all(products.map(async product => {
      // Get historical sales data
      const salesHistory = await getSalesHistory(db, product._id);
      
      // Get seasonal patterns
      const seasonality = analyzeSeasonality(salesHistory);
      
      // Calculate trend
      const trend = analyzeTrend(salesHistory);
      
      // Get stock levels and lead times
      const inventory = await getInventoryMetrics(db, product._id);
      
      // Generate daily predictions
      const dailyPredictions = generateDailyPredictions(
        salesHistory,
        seasonality,
        trend,
        daysAhead
      );

      // Calculate reorder points and quantities
      const reorderMetrics = calculateReorderMetrics(
        dailyPredictions,
        inventory
      );

      // Store prediction results
      await db.collection('inventory_predictions').insertOne({
        productId: product._id,
        timestamp: new Date(),
        predictions: dailyPredictions,
        reorderMetrics,
        confidence: calculateConfidenceScore(salesHistory, seasonality)
      });

      return {
        productId: product._id,
        name: product.name,
        predictions: dailyPredictions,
        reorderMetrics,
        recommendations: generateRecommendations(reorderMetrics, inventory)
      };
    }));

    return predictions;
  } catch (error) {
    console.error('Error predicting inventory:', error);
    return null;
  }
}

async function getSalesHistory(db, productId) {
  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

  const sales = await db.collection('orders').aggregate([
    {
      $match: {
        'items.productId': productId,
        status: 'completed',
        createdAt: { $gte: oneYearAgo }
      }
    },
    {
      $unwind: '$items'
    },
    {
      $match: {
        'items.productId': productId
      }
    },
    {
      $group: {
        _id: {
          year: { $year: '$createdAt' },
          month: { $month: '$createdAt' },
          day: { $dayOfMonth: '$createdAt' }
        },
        quantity: { $sum: '$items.quantity' }
      }
    },
    {
      $sort: {
        '_id.year': 1,
        '_id.month': 1,
        '_id.day': 1
      }
    }
  ]).toArray();

  return sales.map(sale => ({
    date: new Date(sale._id.year, sale._id.month - 1, sale._id.day),
    quantity: sale.quantity
  }));
}

function analyzeSeasonality(salesHistory) {
  // Group sales by month to identify seasonal patterns
  const monthlySales = salesHistory.reduce((acc, sale) => {
    const month = sale.date.getMonth();
    acc[month] = (acc[month] || 0) + sale.quantity;
    return acc;
  }, {});

  // Calculate seasonal indices
  const totalSales = Object.values(monthlySales).reduce((a, b) => a + b, 0);
  const avgMonthlySales = totalSales / 12;

  return Object.entries(monthlySales).map(([month, sales]) => ({
    month: parseInt(month),
    index: sales / avgMonthlySales
  }));
}

function analyzeTrend(salesHistory) {
  if (salesHistory.length < 2) return { slope: 0, intercept: 0 };

  // Simple linear regression
  const xValues = salesHistory.map((_, i) => i);
  const yValues = salesHistory.map(sale => sale.quantity);

  const n = salesHistory.length;
  const sumX = xValues.reduce((a, b) => a + b, 0);
  const sumY = yValues.reduce((a, b) => a + b, 0);
  const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
  const sumXX = xValues.reduce((sum, x) => sum + x * x, 0);

  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;

  return { slope, intercept };
}

async function getInventoryMetrics(db, productId) {
  const product = await db.collection('products').findOne({ _id: productId });
  
  // Get supplier lead times
  const supplierData = await db.collection('suppliers').findOne({
    _id: product.supplierId
  });

  return {
    currentStock: product.stockLevel || 0,
    reorderPoint: product.reorderPoint || 0,
    leadTime: supplierData?.leadTime || 7, // Default to 7 days if unknown
    safetyStock: product.safetyStock || 0,
    minOrderQuantity: product.minOrderQuantity || 1
  };
}

function generateDailyPredictions(salesHistory, seasonality, trend, daysAhead) {
  const predictions = [];
  const today = new Date();

  for (let i = 0; i < daysAhead; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() + i);

    // Apply trend
    const baseQuantity = trend.intercept + trend.slope * (salesHistory.length + i);

    // Apply seasonality
    const monthIndex = date.getMonth();
    const seasonalFactor = seasonality.find(s => s.month === monthIndex)?.index || 1;

    // Generate prediction
    predictions.push({
      date,
      predictedQuantity: Math.max(0, Math.round(baseQuantity * seasonalFactor)),
      confidence: calculateDailyConfidence(i, salesHistory.length)
    });
  }

  return predictions;
}

function calculateReorderMetrics(predictions, inventory) {
  const totalPredicted = predictions.reduce((sum, pred) => 
    sum + pred.predictedQuantity, 0);
  
  const averageDailyDemand = totalPredicted / predictions.length;
  const standardDeviation = calculateStandardDeviation(
    predictions.map(p => p.predictedQuantity)
  );

  const serviceLevel = 0.95; // 95% service level
  const zScore = 1.645; // z-score for 95% service level

  const reorderPoint = Math.ceil(
    averageDailyDemand * inventory.leadTime +
    zScore * standardDeviation * Math.sqrt(inventory.leadTime)
  );

  const economicOrderQuantity = Math.ceil(Math.sqrt(
    (2 * averageDailyDemand * 365 * 25) / // Ordering cost assumed to be 25
    (0.25 * inventory.currentStock) // Holding cost assumed to be 25% of item value
  ));

  return {
    reorderPoint,
    economicOrderQuantity: Math.max(
      economicOrderQuantity,
      inventory.minOrderQuantity
    ),
    averageDailyDemand,
    standardDeviation
  };
}

function generateRecommendations(reorderMetrics, inventory) {
  const recommendations = [];

  if (inventory.currentStock <= reorderMetrics.reorderPoint) {
    recommendations.push({
      type: 'reorder',
      priority: 'high',
      message: `Stock level (${inventory.currentStock}) below reorder point (${reorderMetrics.reorderPoint}). Place order for ${reorderMetrics.economicOrderQuantity} units.`
    });
  }

  if (inventory.currentStock > reorderMetrics.economicOrderQuantity * 3) {
    recommendations.push({
      type: 'overstock',
      priority: 'medium',
      message: `Current stock level (${inventory.currentStock}) significantly above optimal. Consider reducing future order quantities.`
    });
  }

  if (reorderMetrics.standardDeviation > reorderMetrics.averageDailyDemand) {
    recommendations.push({
      type: 'volatility',
      priority: 'low',
      message: 'High demand volatility detected. Consider increasing safety stock levels.'
    });
  }

  return recommendations;
}

// Helper functions
function calculateStandardDeviation(values) {
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const squaredDiffs = values.map(value => Math.pow(value - mean, 2));
  const variance = squaredDiffs.reduce((a, b) => a + b, 0) / values.length;
  return Math.sqrt(variance);
}

function calculateConfidenceScore(salesHistory, seasonality) {
  const historyScore = Math.min(1, salesHistory.length / 365); // More history = higher confidence
  const seasonalityScore = 1 - calculateStandardDeviation(
    seasonality.map(s => s.index)
  ) / 2; // Less seasonal variation = higher confidence
  
  return (historyScore + seasonalityScore) / 2;
}

function calculateDailyConfidence(daysAhead, historyLength) {
  // Confidence decreases with prediction distance and increases with history length
  const distanceDecay = Math.exp(-daysAhead / 30); // 30-day decay factor
  const historyFactor = Math.min(1, historyLength / 365);
  return distanceDecay * historyFactor;
}
