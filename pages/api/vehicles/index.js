import { getSession } from 'next-auth/react';
import dbConnect from '../../../lib/mongodb';
import Vehicle from '../../../models/Vehicle';

// Rate limiting
const rateLimit = {};
const RATE_LIMIT_WINDOW = 60000; // 1 minute
const MAX_REQUESTS = 100;

// Helper function to check rate limit
function checkRateLimit(ip) {
  const now = Date.now();
  if (!rateLimit[ip]) {
    rateLimit[ip] = { count: 1, timestamp: now };
    return true;
  }

  if (now - rateLimit[ip].timestamp > RATE_LIMIT_WINDOW) {
    rateLimit[ip] = { count: 1, timestamp: now };
    return true;
  }

  if (rateLimit[ip].count >= MAX_REQUESTS) {
    return false;
  }

  rateLimit[ip].count++;
  return true;
}

export default async function handler(req, res) {
  // Rate limiting
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  if (!checkRateLimit(clientIp)) {
    return res.status(429).json({ error: 'Too many requests' });
  }

  try {
    await dbConnect();

    if (req.method === 'GET') {
      try {
        const query = {};
        const { category, inStock, maxPrice, search, page = 1, limit = 10 } = req.query;

        // Build query
        if (category && category !== 'All') {
          query.category = category;
        }

        if (inStock === 'true') {
          query['availability.inStock'] = true;
        }

        if (maxPrice) {
          query.price = { $lte: parseInt(maxPrice) };
        }

        if (search) {
          query.$text = { $search: search };
        }

        // Pagination
        const skip = (parseInt(page) - 1) * parseInt(limit);
        
        // Execute query with pagination
        const [vehicles, total] = await Promise.all([
          Vehicle.find(query)
            .sort({ createdAt: -1 })
            .skip(skip)
            .limit(parseInt(limit))
            .lean(),
          Vehicle.countDocuments(query)
        ]);

        res.status(200).json({
          vehicles,
          pagination: {
            total,
            pages: Math.ceil(total / parseInt(limit)),
            page: parseInt(page),
            limit: parseInt(limit)
          }
        });
      } catch (error) {
        console.error('GET vehicles error:', error);
        res.status(500).json({ error: 'Error fetching vehicles' });
      }
    } else {
      // Check authentication for POST and PUT requests
      const session = await getSession({ req });
      if (!session?.user?.isAdmin) {
        return res.status(401).json({ error: 'Unauthorized' });
      }

      if (req.method === 'POST') {
        try {
          const vehicle = await Vehicle.create(req.body);
          res.status(201).json(vehicle);
        } catch (error) {
          console.error('POST vehicle error:', error);
          res.status(400).json({ error: error.message });
        }
      } else if (req.method === 'PUT') {
        try {
          const { id } = req.query;
          const vehicle = await Vehicle.findOneAndUpdate(
            { id },
            req.body,
            { new: true, runValidators: true }
          );
          
          if (!vehicle) {
            return res.status(404).json({ error: 'Vehicle not found' });
          }
          
          res.status(200).json(vehicle);
        } catch (error) {
          console.error('PUT vehicle error:', error);
          res.status(400).json({ error: error.message });
        }
      } else {
        res.setHeader('Allow', ['GET', 'POST', 'PUT']);
        res.status(405).json({ error: `Method ${req.method} Not Allowed` });
      }
    }
  } catch (error) {
    console.error('API error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
