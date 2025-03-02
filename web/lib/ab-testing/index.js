import { connectToDatabase } from '../mongodb';

export async function createExperiment({
  name,
  description,
  variants,
  targetAudience,
  startDate,
  endDate,
  goals
}) {
  const { db } = await connectToDatabase();

  try {
    // Validate experiment parameters
    if (!name || !variants || variants.length < 2) {
      throw new Error('Invalid experiment parameters');
    }

    // Create experiment
    const experiment = {
      name,
      description,
      variants: variants.map(variant => ({
        ...variant,
        impressions: 0,
        conversions: 0
      })),
      targetAudience,
      startDate: startDate || new Date(),
      endDate: endDate || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // Default 30 days
      goals,
      status: 'active',
      createdAt: new Date(),
      updatedAt: new Date()
    };

    await db.collection('experiments').insertOne(experiment);
    return experiment;
  } catch (error) {
    console.error('Error creating experiment:', error);
    throw error;
  }
}

export async function assignVariant(experimentName, userId) {
  const { db } = await connectToDatabase();

  try {
    // Check if user already has an assignment
    const existingAssignment = await db.collection('experiment_assignments').findOne({
      experimentName,
      userId
    });

    if (existingAssignment) {
      return existingAssignment.variant;
    }

    // Get experiment
    const experiment = await db.collection('experiments').findOne({
      name: experimentName,
      status: 'active',
      startDate: { $lte: new Date() },
      endDate: { $gt: new Date() }
    });

    if (!experiment) {
      return null;
    }

    // Check target audience
    if (experiment.targetAudience) {
      const userMatches = await checkTargetAudience(db, userId, experiment.targetAudience);
      if (!userMatches) {
        return null;
      }
    }

    // Assign variant using weighted random selection
    const variant = selectVariant(experiment.variants);

    // Store assignment
    await db.collection('experiment_assignments').insertOne({
      experimentName,
      userId,
      variant: variant.id,
      assignedAt: new Date()
    });

    // Update impression count
    await db.collection('experiments').updateOne(
      {
        name: experimentName,
        'variants.id': variant.id
      },
      {
        $inc: { 'variants.$.impressions': 1 },
        $set: { updatedAt: new Date() }
      }
    );

    return variant.id;
  } catch (error) {
    console.error('Error assigning variant:', error);
    return null;
  }
}

export async function trackConversion(experimentName, userId, goalId) {
  const { db } = await connectToDatabase();

  try {
    // Get user's variant assignment
    const assignment = await db.collection('experiment_assignments').findOne({
      experimentName,
      userId
    });

    if (!assignment) {
      return false;
    }

    // Record conversion
    await db.collection('experiment_conversions').insertOne({
      experimentName,
      userId,
      variantId: assignment.variant,
      goalId,
      timestamp: new Date()
    });

    // Update conversion count
    await db.collection('experiments').updateOne(
      {
        name: experimentName,
        'variants.id': assignment.variant
      },
      {
        $inc: { 'variants.$.conversions': 1 },
        $set: { updatedAt: new Date() }
      }
    );

    return true;
  } catch (error) {
    console.error('Error tracking conversion:', error);
    return false;
  }
}

export async function getExperimentResults(experimentName) {
  const { db } = await connectToDatabase();

  try {
    const experiment = await db.collection('experiments').findOne({
      name: experimentName
    });

    if (!experiment) {
      throw new Error('Experiment not found');
    }

    // Calculate metrics for each variant
    const results = experiment.variants.map(variant => {
      const conversionRate = variant.impressions > 0
        ? (variant.conversions / variant.impressions) * 100
        : 0;

      return {
        id: variant.id,
        name: variant.name,
        impressions: variant.impressions,
        conversions: variant.conversions,
        conversionRate
      };
    });

    // Determine winner
    const winner = determineWinner(results);

    // Calculate confidence intervals
    const statistics = calculateStatistics(results);

    return {
      experimentName,
      status: experiment.status,
      duration: {
        start: experiment.startDate,
        end: experiment.endDate
      },
      results,
      winner,
      statistics,
      recommendedAction: generateRecommendation(winner, statistics)
    };
  } catch (error) {
    console.error('Error getting experiment results:', error);
    throw error;
  }
}

// Helper functions
async function checkTargetAudience(db, userId, targetAudience) {
  const user = await db.collection('users').findOne({ _id: userId });
  if (!user) return false;

  // Check each targeting criterion
  for (const [criterion, value] of Object.entries(targetAudience)) {
    switch (criterion) {
      case 'segments':
        const userSegments = await db.collection('customer_segments')
          .find({ userId })
          .toArray();
        if (!value.some(segment => userSegments.includes(segment))) {
          return false;
        }
        break;

      case 'activity':
        const activity = await db.collection('user_activity')
          .countDocuments({
            userId,
            timestamp: { $gte: new Date(Date.now() - value * 24 * 60 * 60 * 1000) }
          });
        if (activity < 1) {
          return false;
        }
        break;

      case 'purchaseHistory':
        const orders = await db.collection('orders')
          .countDocuments({
            userId,
            status: 'completed'
          });
        if (orders < value) {
          return false;
        }
        break;

      default:
        if (user[criterion] !== value) {
          return false;
        }
    }
  }

  return true;
}

function selectVariant(variants) {
  const totalWeight = variants.reduce((sum, variant) => 
    sum + (variant.weight || 1), 0);
  
  let random = Math.random() * totalWeight;
  
  for (const variant of variants) {
    random -= (variant.weight || 1);
    if (random <= 0) {
      return variant;
    }
  }
  
  return variants[0];
}

function determineWinner(results) {
  if (results.length < 2) return null;

  const sorted = [...results].sort((a, b) => 
    b.conversionRate - a.conversionRate
  );

  const leader = sorted[0];
  const runnerUp = sorted[1];

  // Check if leader is significantly better
  const improvement = (leader.conversionRate - runnerUp.conversionRate) / runnerUp.conversionRate;
  
  return {
    variantId: leader.id,
    improvement: improvement * 100,
    significant: improvement > 0.1 && leader.impressions > 100
  };
}

function calculateStatistics(results) {
  const stats = results.map(variant => {
    // Calculate confidence interval using normal approximation
    const p = variant.conversionRate / 100;
    const n = variant.impressions;
    const standardError = Math.sqrt((p * (1 - p)) / n);
    const z = 1.96; // 95% confidence level

    return {
      variantId: variant.id,
      margin: z * standardError * 100,
      confidenceInterval: {
        lower: Math.max(0, (p - z * standardError) * 100),
        upper: Math.min(100, (p + z * standardError) * 100)
      }
    };
  });

  return {
    confidenceLevel: 95,
    intervals: stats
  };
}

function generateRecommendation(winner, statistics) {
  if (!winner) {
    return {
      action: 'continue',
      message: 'Continue running the experiment to gather more data.'
    };
  }

  if (!winner.significant) {
    return {
      action: 'monitor',
      message: 'Results show a potential winner but need more data to be confident.'
    };
  }

  return {
    action: 'implement',
    message: `Implement variant ${winner.variantId} which showed a ${winner.improvement.toFixed(1)}% improvement.`
  };
}
