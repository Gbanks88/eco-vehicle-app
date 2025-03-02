import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const BASE_DIR = process.cwd();
const LOG_DIR = path.join(BASE_DIR, 'logs');
const METRICS_DIR = path.join(LOG_DIR, 'metrics');

// Enhanced metrics collection
async function collectEnhancedMetrics(domain) {
  try {
    // Basic metrics
    const basicMetrics = await getBasicMetrics(domain);
    
    // Performance metrics
    const performanceMetrics = await getPerformanceMetrics(domain);
    
    // Security metrics
    const securityMetrics = await getSecurityMetrics(domain);
    
    // Traffic metrics
    const trafficMetrics = await getTrafficMetrics(domain);
    
    // Error metrics
    const errorMetrics = await getErrorMetrics(domain);
    
    return {
      ...basicMetrics,
      performance: performanceMetrics,
      security: securityMetrics,
      traffic: trafficMetrics,
      errors: errorMetrics,
    };
  } catch (error) {
    console.error(`Error collecting metrics for ${domain}:`, error);
    return null;
  }
}

async function getBasicMetrics(domain) {
  const metricsFile = path.join(METRICS_DIR, `${domain.replace(/\//g, '_')}_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.csv`);
  
  try {
    const content = fs.readFileSync(metricsFile, 'utf-8');
    const lines = content.trim().split('\n');
    const latest = lines[lines.length - 1].split(',');
    
    return {
      responseTime: parseFloat(latest[1]),
      sslDaysRemaining: parseInt(latest[2]),
      securityScore: parseInt(latest[3]),
      uptime: parseFloat(latest[4]),
    };
  } catch (error) {
    return {
      responseTime: 0,
      sslDaysRemaining: 0,
      securityScore: 0,
      uptime: 0,
    };
  }
}

async function getPerformanceMetrics(domain) {
  try {
    // Simulate performance data collection
    return {
      ttfb: Math.random() * 200 + 100,
      fcp: Math.random() * 500 + 300,
      lcp: Math.random() * 1000 + 500,
      cls: Math.random() * 0.1,
      fid: Math.random() * 50 + 20,
    };
  } catch (error) {
    return null;
  }
}

async function getSecurityMetrics(domain) {
  try {
    // Get SSL information
    const sslInfo = execSync(`echo | openssl s_client -connect ${domain}:443 2>/dev/null | openssl x509 -noout -text`).toString();
    
    // Get security headers
    const headers = execSync(`curl -sI https://${domain}`).toString();
    
    return {
      ssl: {
        valid: sslInfo.includes('SSL handshake'),
        protocol: sslInfo.match(/Protocol: (.*)/)?.[1] || 'unknown',
        cipher: sslInfo.match(/Cipher: (.*)/)?.[1] || 'unknown',
      },
      headers: {
        hsts: headers.includes('Strict-Transport-Security'),
        csp: headers.includes('Content-Security-Policy'),
        xfo: headers.includes('X-Frame-Options'),
        xxp: headers.includes('X-XSS-Protection'),
      },
      score: calculateSecurityScore(headers),
    };
  } catch (error) {
    return null;
  }
}

async function getTrafficMetrics(domain) {
  try {
    // Simulate traffic metrics
    return {
      requests: Math.floor(Math.random() * 1000),
      uniqueVisitors: Math.floor(Math.random() * 500),
      bandwidth: Math.floor(Math.random() * 1000000),
      avgResponseTime: Math.random() * 200 + 100,
    };
  } catch (error) {
    return null;
  }
}

async function getErrorMetrics(domain) {
  try {
    const errorLogFile = path.join(LOG_DIR, 'errors', `${domain.replace(/\//g, '_')}.log`);
    
    if (fs.existsSync(errorLogFile)) {
      const content = fs.readFileSync(errorLogFile, 'utf-8');
      const lines = content.trim().split('\n');
      
      return {
        total: lines.length,
        recent: lines.slice(-10).map(line => {
          const [timestamp, error] = line.split(' - ');
          return { timestamp, error };
        }),
        byType: lines.reduce((acc, line) => {
          const type = line.split(' - ')[1].split(':')[0];
          acc[type] = (acc[type] || 0) + 1;
          return acc;
        }, {}),
      };
    }
    
    return {
      total: 0,
      recent: [],
      byType: {},
    };
  } catch (error) {
    return null;
  }
}

function calculateSecurityScore(headers) {
  let score = 100;
  
  if (!headers.includes('Strict-Transport-Security')) score -= 20;
  if (!headers.includes('Content-Security-Policy')) score -= 20;
  if (!headers.includes('X-Frame-Options')) score -= 15;
  if (!headers.includes('X-Content-Type-Options')) score -= 15;
  if (!headers.includes('Referrer-Policy')) score -= 10;
  if (!headers.includes('Permissions-Policy')) score -= 10;
  
  return Math.max(0, score);
}

export default async function handler(req, res) {
  try {
    const configPath = path.join(process.cwd(), 'scripts', 'monitor-config.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    
    const domains = await Promise.all(
      Object.keys(config.domains).map(async domain => {
        const metrics = await collectEnhancedMetrics(domain);
        return {
          domain,
          type: config.domains[domain].type,
          metrics,
        };
      })
    );
    
    res.status(200).json({
      domains,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error in enhanced metrics API:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
