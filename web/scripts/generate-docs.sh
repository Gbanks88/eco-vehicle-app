#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directory
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
DOCS_DIR="$BASE_DIR/docs"

# Create docs directory
mkdir -p "$DOCS_DIR"
mkdir -p "$DOCS_DIR/api"
mkdir -p "$DOCS_DIR/deployment"
mkdir -p "$DOCS_DIR/monitoring"
mkdir -p "$DOCS_DIR/games"

# Generate API Documentation
cat << EOF > "$DOCS_DIR/api/README.md"
# API Documentation

## Authentication Endpoints

### POST /api/auth/signin
- Description: Authenticate user and create session
- Body: \`{ email: string, password: string }\`
- Returns: JWT token and user data

### POST /api/auth/signup
- Description: Create new user account
- Body: \`{ name: string, email: string, password: string }\`
- Returns: User data

## Vehicle Endpoints

### GET /api/vehicles
- Description: Get list of vehicles
- Query Parameters: 
  - page: number
  - limit: number
  - sort: string
- Returns: Array of vehicles

### POST /api/vehicles
- Description: Create new vehicle
- Authentication: Required (Admin)
- Body: Vehicle data
- Returns: Created vehicle

## Game Endpoints

### GET /api/games/scores
- Description: Get game high scores
- Query Parameters:
  - game: string
  - limit: number
- Returns: Array of scores

### POST /api/games/scores
- Description: Submit game score
- Authentication: Required
- Body: \`{ game: string, score: number }\`
- Returns: Updated score
EOF

# Generate Deployment Documentation
cat << EOF > "$DOCS_DIR/deployment/README.md"
# Deployment Guide

## Prerequisites
- Node.js 18+
- MongoDB
- Netlify CLI

## Environment Setup
1. Copy \`.env.example\` to \`.env\`
2. Configure environment variables:
   - \`MONGODB_URI\`
   - \`NEXTAUTH_URL\`
   - \`NEXTAUTH_SECRET\`
   - \`ADMIN_EMAIL\`
   - \`ADMIN_PASSWORD\`

## Database Setup
1. Run database seeding:
   \`\`\`bash
   npm run seed
   \`\`\`
2. Create admin user:
   \`\`\`bash
   npm run create-admin
   \`\`\`

## Build & Deploy
1. Install dependencies:
   \`\`\`bash
   npm install
   \`\`\`
2. Build project:
   \`\`\`bash
   npm run build
   \`\`\`
3. Deploy to Netlify:
   \`\`\`bash
   netlify deploy --prod
   \`\`\`

## Domain Configuration
1. Configure DNS records
2. Set up SSL certificates
3. Configure security headers
EOF

# Generate Monitoring Documentation
cat << EOF > "$DOCS_DIR/monitoring/README.md"
# Monitoring Guide

## System Components
1. Domain Monitoring
2. Performance Metrics
3. Security Alerts
4. Backup System

## Monitoring Dashboard
Access the monitoring dashboard at \`/admin/monitor\`

## Available Commands

### Monitor Manager
\`\`\`bash
./scripts/monitor-manager.sh {start|stop|restart|status|logs}
\`\`\`

### Backup Manager
\`\`\`bash
./scripts/backup-manager.sh {daily|weekly|monthly|cleanup}
\`\`\`

### Security Enhancer
\`\`\`bash
./scripts/security-enhancer.sh domain.com
\`\`\`

## Alert Configuration
1. Email notifications
2. Slack integration
3. Custom webhooks

## Metrics Collection
- Response time
- SSL status
- Security score
- Error rates
- Traffic patterns
EOF

# Generate Game Documentation
cat << EOF > "$DOCS_DIR/games/README.md"
# Game Integration Guide

## Available Games
1. Motherboard Explorer
2. Recycling Challenge
3. SysML Viewer

## Game Server Setup
1. Install dependencies:
   \`\`\`bash
   cd games/[game_name]
   npm install
   \`\`\`
2. Configure database
3. Start server:
   \`\`\`bash
   npm start
   \`\`\`

## Game Assets
- Location: \`public/assets/games/\`
- Required formats
- Asset optimization

## Scoring System
- Score calculation
- Leaderboard integration
- Score submission API

## Integration with Main App
1. React components
2. Game state management
3. User progress tracking
EOF

echo -e "${GREEN}Documentation generated successfully!${NC}"
echo -e "${YELLOW}Documentation is available in the /docs directory${NC}"
