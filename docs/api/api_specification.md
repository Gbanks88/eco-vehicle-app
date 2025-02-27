# API Specification

## 1. REST API

### 1.1 Metrics Endpoints

#### Get Vehicle Metrics
```http
GET /api/v1/metrics/{vehicle_id}
Authorization: Bearer {token}

Response 200:
{
    "timestamp": "2025-02-25T04:29:12-07:00",
    "metrics": {
        "cpu_usage": 45.2,
        "memory_usage": 68.7,
        "battery_level": 82.3,
        "network_latency": 23.1,
        "environmental_score": 89.5
    },
    "status": "healthy"
}
```

#### Submit Metrics
```http
POST /api/v1/metrics/{vehicle_id}
Authorization: Bearer {token}
Content-Type: application/json

{
    "metrics": {
        "cpu_usage": 45.2,
        "memory_usage": 68.7,
        "battery_level": 82.3
    }
}

Response 201:
{
    "id": "metric_123",
    "timestamp": "2025-02-25T04:29:12-07:00",
    "status": "accepted"
}
```

### 1.2 Analysis Endpoints

#### Get Analysis Results
```http
GET /api/v1/analysis/{vehicle_id}
Authorization: Bearer {token}

Response 200:
{
    "timestamp": "2025-02-25T04:29:12-07:00",
    "analysis": {
        "performance_score": 92.5,
        "anomalies": [],
        "predictions": {
            "maintenance_needed": false,
            "next_service": "2025-03-25"
        }
    }
}
```

### 1.3 Alert Endpoints

#### Get Active Alerts
```http
GET /api/v1/alerts/{vehicle_id}
Authorization: Bearer {token}

Response 200:
{
    "alerts": [
        {
            "id": "alert_123",
            "severity": "warning",
            "message": "High CPU usage detected",
            "timestamp": "2025-02-25T04:29:12-07:00"
        }
    ]
}
```

## 2. WebSocket API

### 2.1 Real-time Metrics Stream
```javascript
// Connect to WebSocket
ws://api.example.com/ws/metrics/{vehicle_id}

// Subscribe to metrics
{
    "action": "subscribe",
    "channels": ["metrics", "alerts"]
}

// Receive updates
{
    "type": "metric_update",
    "data": {
        "timestamp": "2025-02-25T04:29:12-07:00",
        "metric": "cpu_usage",
        "value": 45.2
    }
}
```

### 2.2 Alert Notifications
```javascript
// Alert message format
{
    "type": "alert",
    "data": {
        "id": "alert_123",
        "severity": "warning",
        "message": "High CPU usage detected",
        "timestamp": "2025-02-25T04:29:12-07:00"
    }
}
```

## 3. gRPC Service

### 3.1 Service Definition
```protobuf
syntax = "proto3";

service VehicleMonitoring {
    rpc StreamMetrics (VehicleId) returns (stream Metric);
    rpc SubmitMetrics (MetricsBatch) returns (SubmissionResponse);
    rpc GetAnalysis (AnalysisRequest) returns (AnalysisResponse);
    rpc SubscribeAlerts (VehicleId) returns (stream Alert);
}

message VehicleId {
    string id = 1;
}

message Metric {
    string name = 1;
    double value = 2;
    string unit = 3;
    int64 timestamp = 4;
}

message MetricsBatch {
    string vehicle_id = 1;
    repeated Metric metrics = 2;
}

message AnalysisRequest {
    string vehicle_id = 1;
    string analysis_type = 2;
    int64 start_time = 3;
    int64 end_time = 4;
}

message Alert {
    string id = 1;
    string severity = 2;
    string message = 3;
    int64 timestamp = 4;
}
```

## 4. Authentication

### 4.1 OAuth2 Configuration
```javascript
{
    "auth_url": "https://auth.example.com/oauth2/authorize",
    "token_url": "https://auth.example.com/oauth2/token",
    "client_id": "${CLIENT_ID}",
    "scopes": [
        "metrics:read",
        "metrics:write",
        "analysis:read",
        "alerts:read"
    ]
}
```

### 4.2 API Key Authentication
```http
GET /api/v1/metrics
X-API-Key: ${API_KEY}
```

## 5. Rate Limiting

### 5.1 Limits
```yaml
endpoints:
  metrics:
    read: 1000/minute
    write: 100/minute
  analysis:
    read: 100/minute
  alerts:
    read: 500/minute

websocket:
  messages: 100/second
  connections: 1000/hour
```

## 6. Error Responses

### 6.1 Standard Error Format
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {
            "field": "specific_field",
            "reason": "validation_failed"
        }
    },
    "request_id": "req_123"
}
```

### 6.2 Error Codes
```yaml
error_codes:
  - INVALID_REQUEST: 400
  - UNAUTHORIZED: 401
  - FORBIDDEN: 403
  - NOT_FOUND: 404
  - RATE_LIMITED: 429
  - INTERNAL_ERROR: 500
```
