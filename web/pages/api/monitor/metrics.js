import { connectToDatabase } from '../../../lib/mongodb';
import { getSession } from 'next-auth/react';
import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  try {
    const session = await getSession({ req });
    if (!session || session.user.role !== 'admin') {
      res.status(401).json({ message: 'Not authenticated!' });
      return;
    }

    const { db } = await connectToDatabase();
    const metricsDir = path.join(process.cwd(), 'logs', 'metrics');
    
    // Get latest metrics from files
    const metrics = {};
    const files = fs.readdirSync(metricsDir);
    
    for (const file of files) {
      if (file.endsWith('.csv')) {
        const domain = file.split('_')[0];
        const content = fs.readFileSync(path.join(metricsDir, file), 'utf-8');
        const lines = content.trim().split('\n');
        const latest = lines[lines.length - 1].split(',');
        
        metrics[domain] = {
          responseTime: parseFloat(latest[1]),
          sslDaysRemaining: parseInt(latest[2]),
          securityScore: parseInt(latest[3]),
          uptime: parseFloat(latest[4]),
        };
      }
    }
    
    // Get recent alerts
    const alerts = await db.collection('alerts')
      .find({})
      .sort({ timestamp: -1 })
      .limit(10)
      .toArray();

    res.status(200).json({
      metrics,
      alerts,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
}
