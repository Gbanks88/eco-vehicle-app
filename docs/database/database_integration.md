# Database Integration Guide

## 1. Time Series Database (InfluxDB)

### 1.1 Data Model
```sql
-- Metrics Measurement
measurement vehicle_metrics
    fields:
        cpu_usage float
        memory_usage float
        network_latency float
        battery_level float
        environmental_score float
    tags:
        vehicle_id string
        sensor_type string
        location string

-- Events Measurement
measurement system_events
    fields:
        event_type string
        severity string
        description string
    tags:
        component string
        status string
```

### 1.2 Retention Policies
```sql
-- Real-time data (high precision)
CREATE RETENTION POLICY "realtime"
    ON "vehicle_metrics"
    DURATION 24h
    REPLICATION 3

-- Aggregated data (hourly)
CREATE RETENTION POLICY "hourly"
    ON "vehicle_metrics"
    DURATION 30d
    REPLICATION 3

-- Historical data (daily)
CREATE RETENTION POLICY "historical"
    ON "vehicle_metrics"
    DURATION 365d
    REPLICATION 3
```

## 2. Document Store (MongoDB with Studio 3T)

### 2.1 Collections Schema
```javascript
// System Configuration
{
    "_id": ObjectId,
    "component": String,
    "settings": {
        "thresholds": {
            "cpu": Number,
            "memory": Number,
            "battery": Number
        },
        "intervals": {
            "collection": Number,
            "analysis": Number,
            "backup": Number
        }
    },
    "metadata": {
        "last_updated": Date,
        "version": String
    }
}

// ML Models
{
    "_id": ObjectId,
    "model_name": String,
    "version": String,
    "type": String,
    "parameters": {
        "hyperparameters": Object,
        "architecture": Object
    },
    "performance": {
        "accuracy": Number,
        "latency": Number,
        "resource_usage": Object
    },
    "training": {
        "start_time": Date,
        "end_time": Date,
        "dataset_version": String
    }
}

// Analysis Results
{
    "_id": ObjectId,
    "timestamp": Date,
    "type": String,
    "results": {
        "metrics": Object,
        "predictions": Array,
        "anomalies": Array
    },
    "metadata": {
        "model_version": String,
        "confidence": Number
    }
}
```

### 2.2 Indexes
```javascript
// Performance Indexes
db.metrics.createIndex({ "timestamp": 1 })
db.metrics.createIndex({ "vehicle_id": 1, "timestamp": 1 })
db.events.createIndex({ "severity": 1, "timestamp": 1 })

// Analysis Indexes
db.analysis.createIndex({ "type": 1, "timestamp": 1 })
db.models.createIndex({ "model_name": 1, "version": 1 })

// Compound Indexes
db.metrics.createIndex({ 
    "vehicle_id": 1, 
    "sensor_type": 1, 
    "timestamp": 1 
})
```

## 3. Cache Layer (Redis)

### 3.1 Data Structures
```redis
# Real-time Metrics
HSET vehicle:metrics:${id} 
    cpu_usage ${value}
    memory_usage ${value}
    battery_level ${value}

# Active Alerts
ZADD alerts:active ${timestamp} ${alert_json}

# Model Predictions
HSET predictions:${model}:${id} 
    value ${prediction}
    confidence ${confidence}
    timestamp ${timestamp}

# UI State
HSET ui:state:${session} 
    view ${view_json}
    filters ${filters_json}
```

### 3.2 Expiration Policies
```redis
# Metrics TTL
EXPIRE vehicle:metrics:${id} 3600

# Predictions TTL
EXPIRE predictions:${model}:${id} 1800

# Session TTL
EXPIRE ui:state:${session} 7200
```

## 4. Studio 3T Integration

### 4.1 Connection Configuration
```javascript
{
    "name": "EcoVehicle-Production",
    "type": "replica_set",
    "hosts": [
        "mongodb-0.example.com:27017",
        "mongodb-1.example.com:27017",
        "mongodb-2.example.com:27017"
    ],
    "options": {
        "replicaSet": "rs0",
        "ssl": true,
        "authSource": "admin"
    }
}
```

### 4.2 Aggregation Pipelines
```javascript
// Performance Analysis Pipeline
[
    {
        $match: {
            timestamp: {
                $gte: ISODate("2025-02-24"),
                $lt: ISODate("2025-02-25")
            }
        }
    },
    {
        $group: {
            _id: {
                vehicle: "$vehicle_id",
                hour: { $hour: "$timestamp" }
            },
            avg_cpu: { $avg: "$cpu_usage" },
            avg_memory: { $avg: "$memory_usage" },
            alerts: { $sum: 1 }
        }
    },
    {
        $sort: {
            "_id.hour": 1
        }
    }
]
```

### 4.3 Export Templates
```javascript
{
    "format": "csv",
    "collections": [
        "metrics",
        "events",
        "analysis"
    ],
    "query": {
        "timestamp": {
            "$gte": "$$start_date",
            "$lt": "$$end_date"
        }
    },
    "fields": {
        "timestamp": 1,
        "vehicle_id": 1,
        "metrics": 1,
        "events": 1
    }
}
```
