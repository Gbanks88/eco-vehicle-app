import { Parser } from 'json2csv';
import ExcelJS from 'exceljs';
import { connectToDatabase } from '../mongodb';

export async function exportMetrics(format, timeframe, system) {
  const { db } = await connectToDatabase();

  try {
    // Get metrics data
    const startTime = getStartTime(timeframe);
    const query = {
      timestamp: { $gte: startTime }
    };
    if (system !== 'all') {
      query.type = system;
    }

    const metrics = await db.collection('system_metrics')
      .find(query)
      .sort({ timestamp: 1 })
      .toArray();

    // Process metrics into a flat structure
    const processedData = metrics.map(metric => flattenMetric(metric));

    switch (format.toLowerCase()) {
      case 'csv':
        return exportToCSV(processedData);
      case 'excel':
        return exportToExcel(processedData);
      case 'json':
        return exportToJSON(processedData);
      default:
        throw new Error('Unsupported export format');
    }
  } catch (error) {
    console.error('Error exporting metrics:', error);
    throw error;
  }
}

function getStartTime(timeframe) {
  const now = new Date();
  switch (timeframe) {
    case '1h':
      return new Date(now - 60 * 60 * 1000);
    case '6h':
      return new Date(now - 6 * 60 * 60 * 1000);
    case '24h':
      return new Date(now - 24 * 60 * 60 * 1000);
    case '7d':
      return new Date(now - 7 * 24 * 60 * 60 * 1000);
    case '30d':
      return new Date(now - 30 * 24 * 60 * 60 * 1000);
    default:
      return new Date(now - 24 * 60 * 60 * 1000); // Default to 24h
  }
}

function flattenMetric(metric) {
  const flatMetric = {
    timestamp: metric.timestamp,
    type: metric.type
  };

  // Flatten nested objects
  function flatten(obj, prefix = '') {
    for (const [key, value] of Object.entries(obj)) {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        flatten(value, `${prefix}${key}_`);
      } else {
        flatMetric[`${prefix}${key}`] = value;
      }
    }
  }

  flatten(metric.metrics);
  return flatMetric;
}

async function exportToCSV(data) {
  try {
    const fields = Object.keys(data[0]);
    const parser = new Parser({ fields });
    const csv = parser.parse(data);
    return {
      data: csv,
      filename: `metrics_export_${new Date().toISOString()}.csv`,
      contentType: 'text/csv'
    };
  } catch (error) {
    console.error('Error generating CSV:', error);
    throw error;
  }
}

async function exportToExcel(data) {
  try {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Metrics');

    // Add headers
    const headers = Object.keys(data[0]);
    worksheet.addRow(headers);

    // Add data
    data.forEach(row => {
      worksheet.addRow(headers.map(header => row[header]));
    });

    // Style headers
    worksheet.getRow(1).font = { bold: true };
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE0E0E0' }
    };

    // Auto-fit columns
    worksheet.columns.forEach(column => {
      column.width = Math.max(
        15,
        ...worksheet.getColumn(column.number).values
          .map(v => String(v).length)
      );
    });

    // Generate buffer
    const buffer = await workbook.xlsx.writeBuffer();

    return {
      data: buffer,
      filename: `metrics_export_${new Date().toISOString()}.xlsx`,
      contentType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    };
  } catch (error) {
    console.error('Error generating Excel:', error);
    throw error;
  }
}

function exportToJSON(data) {
  try {
    return {
      data: JSON.stringify(data, null, 2),
      filename: `metrics_export_${new Date().toISOString()}.json`,
      contentType: 'application/json'
    };
  } catch (error) {
    console.error('Error generating JSON:', error);
    throw error;
  }
}
