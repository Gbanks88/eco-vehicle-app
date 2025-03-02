import { getSession } from 'next-auth/react';

export async function withAuth(handler) {
  return async (req, res) => {
    try {
      const session = await getSession({ req });
      
      if (!session) {
        return res.status(401).json({ error: 'Unauthorized' });
      }

      // Add session to request object
      req.session = session;
      
      // Call the original handler
      return handler(req, res);
    } catch (error) {
      console.error('Auth middleware error:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  };
}

export async function withAdminAuth(handler) {
  return async (req, res) => {
    try {
      const session = await getSession({ req });
      
      if (!session?.user?.isAdmin) {
        return res.status(401).json({ error: 'Unauthorized - Admin access required' });
      }

      // Add session to request object
      req.session = session;
      
      // Call the original handler
      return handler(req, res);
    } catch (error) {
      console.error('Admin auth middleware error:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  };
}

export async function withRateLimit(handler, { maxRequests = 100, windowMs = 60000 } = {}) {
  const rateLimit = new Map();

  return async (req, res) => {
    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    const now = Date.now();
    const windowStart = now - windowMs;

    // Clean up old entries
    for (const [key, data] of rateLimit.entries()) {
      if (data.timestamp < windowStart) {
        rateLimit.delete(key);
      }
    }

    // Check rate limit
    const requestData = rateLimit.get(ip) || { count: 0, timestamp: now };
    if (requestData.count >= maxRequests) {
      return res.status(429).json({
        error: 'Too many requests',
        retryAfter: Math.ceil((requestData.timestamp + windowMs - now) / 1000)
      });
    }

    // Update rate limit
    rateLimit.set(ip, {
      count: requestData.count + 1,
      timestamp: now
    });

    // Call the original handler
    return handler(req, res);
  };
}
