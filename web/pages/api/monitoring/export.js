import { exportMetrics } from '../../../lib/monitoring/export';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { format = 'csv', timeframe = '24h', system = 'all' } = req.query;

    const exportData = await exportMetrics(format, timeframe, system);

    res.setHeader('Content-Type', exportData.contentType);
    res.setHeader('Content-Disposition', `attachment; filename=${exportData.filename}`);
    res.status(200).send(exportData.data);
  } catch (error) {
    console.error('Error in export API:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
