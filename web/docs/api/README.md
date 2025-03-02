# API Documentation

## Authentication Endpoints

### POST /api/auth/signin
- Description: Authenticate user and create session
- Body: `{ email: string, password: string }`
- Returns: JWT token and user data

### POST /api/auth/signup
- Description: Create new user account
- Body: `{ name: string, email: string, password: string }`
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
- Body: `{ game: string, score: number }`
- Returns: Updated score
