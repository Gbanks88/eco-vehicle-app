#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directory
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
API_DIR="$BASE_DIR/pages/api"

echo -e "${BLUE}Starting API fix...${NC}"

# Create necessary API directories
mkdir -p "$API_DIR/auth"
mkdir -p "$API_DIR/vehicles"
mkdir -p "$API_DIR/games"
mkdir -p "$API_DIR/monitor"

# Create auth API endpoints
cat << 'EOF' > "$API_DIR/auth/[...nextauth].js"
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { verifyPassword } from '../../../lib/auth';
import { connectToDatabase } from '../../../lib/mongodb';

export default NextAuth({
  session: {
    strategy: 'jwt',
  },
  providers: [
    CredentialsProvider({
      async authorize(credentials) {
        const { db } = await connectToDatabase();
        
        const user = await db.collection('users').findOne({
          email: credentials.email,
        });

        if (!user) {
          throw new Error('No user found!');
        }

        const isValid = await verifyPassword(
          credentials.password,
          user.password
        );

        if (!isValid) {
          throw new Error('Invalid password!');
        }

        return {
          id: user._id.toString(),
          email: user.email,
          name: user.name,
          role: user.role,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.role = token.role;
      return session;
    },
  },
});
EOF

# Create vehicles API endpoint
cat << 'EOF' > "$API_DIR/vehicles/index.js"
import { connectToDatabase } from '../../../lib/mongodb';
import { getSession } from 'next-auth/react';

export default async function handler(req, res) {
  try {
    const session = await getSession({ req });
    const { db } = await connectToDatabase();

    switch (req.method) {
      case 'GET':
        const vehicles = await db.collection('vehicles')
          .find({})
          .sort({ createdAt: -1 })
          .toArray();
        
        res.status(200).json(vehicles);
        break;

      case 'POST':
        if (!session || session.user.role !== 'admin') {
          res.status(401).json({ message: 'Not authenticated!' });
          return;
        }

        const result = await db.collection('vehicles').insertOne({
          ...req.body,
          createdAt: new Date(),
        });

        res.status(201).json(result);
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
}
EOF

# Create games API endpoint
cat << 'EOF' > "$API_DIR/games/scores.js"
import { connectToDatabase } from '../../../lib/mongodb';
import { getSession } from 'next-auth/react';

export default async function handler(req, res) {
  try {
    const { db } = await connectToDatabase();

    switch (req.method) {
      case 'GET':
        const { game, limit = 10 } = req.query;
        
        const scores = await db.collection('scores')
          .find({ game })
          .sort({ score: -1 })
          .limit(parseInt(limit))
          .toArray();
        
        res.status(200).json(scores);
        break;

      case 'POST':
        const session = await getSession({ req });
        if (!session) {
          res.status(401).json({ message: 'Not authenticated!' });
          return;
        }

        const { game, score } = req.body;
        
        const result = await db.collection('scores').insertOne({
          game,
          score: parseInt(score),
          userId: session.user.id,
          userName: session.user.name,
          createdAt: new Date(),
        });

        res.status(201).json(result);
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
}
EOF

# Create monitor API endpoint
cat << 'EOF' > "$API_DIR/monitor/metrics.js"
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
EOF

echo -e "${GREEN}API endpoints created successfully!${NC}"

# Make all scripts executable
chmod +x "$BASE_DIR/scripts/"*.sh

echo -e "${YELLOW}Starting services...${NC}"

# Start MongoDB if not running
if ! pgrep mongod > /dev/null; then
    echo -e "${BLUE}Starting MongoDB...${NC}"
    brew services start mongodb-community
fi

# Start Next.js development server
echo -e "${BLUE}Starting Next.js server...${NC}"
cd "$BASE_DIR"
npm run dev &

echo -e "${GREEN}All services started!${NC}"
echo -e "${YELLOW}Please check the API endpoints are working correctly${NC}"
