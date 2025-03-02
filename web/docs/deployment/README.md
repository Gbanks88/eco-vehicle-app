# Deployment Guide

## Prerequisites
- Node.js 18+
- MongoDB
- Netlify CLI

## Environment Setup
1. Copy `.env.example` to `.env`
2. Configure environment variables:
   - `MONGODB_URI`
   - `NEXTAUTH_URL`
   - `NEXTAUTH_SECRET`
   - `ADMIN_EMAIL`
   - `ADMIN_PASSWORD`

## Database Setup
1. Run database seeding:
   ```bash
   npm run seed
   ```
2. Create admin user:
   ```bash
   npm run create-admin
   ```

## Build & Deploy
1. Install dependencies:
   ```bash
   npm install
   ```
2. Build project:
   ```bash
   npm run build
   ```
3. Deploy to Netlify:
   ```bash
   netlify deploy --prod
   ```

## Domain Configuration
1. Configure DNS records
2. Set up SSL certificates
3. Configure security headers
