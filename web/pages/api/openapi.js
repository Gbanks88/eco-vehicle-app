import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { builderPaths, builderSchemas } from '../../lib/builder/swagger';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const openApiPath = path.join(process.cwd(), '..', 'openapi.yaml');
    const fileContents = fs.readFileSync(openApiPath, 'utf8');
    const openApiSpec = yaml.load(fileContents);

    // Add builder paths and schemas
    openApiSpec.paths = {
      ...openApiSpec.paths,
      ...builderPaths
    };

    openApiSpec.components.schemas = {
      ...openApiSpec.components.schemas,
      ...builderSchemas
    };

    // Replace server URLs based on environment
    const baseUrl = process.env.NODE_ENV === 'production'
      ? 'https://api.eco-vehicle.app/v1'
      : `${req.headers['x-forwarded-proto'] || 'http'}://${req.headers.host}/api`;

    openApiSpec.servers = [
      {
        url: baseUrl,
        description: process.env.NODE_ENV === 'production' ? 'Production server' : 'Development server'
      }
    ];

    res.setHeader('Content-Type', 'application/yaml');
    res.status(200).send(yaml.dump(openApiSpec));
  } catch (error) {
    console.error('Error serving OpenAPI spec:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
