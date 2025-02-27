# Infrastructure and Deployment Guide

## 1. Kubernetes Deployment

### 1.1 Core Application Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eco-vehicle-monitor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: eco-vehicle-monitor
  template:
    metadata:
      labels:
        app: eco-vehicle-monitor
    spec:
      containers:
      - name: monitor
        image: eco-vehicle/monitor:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: mongodb-uri
        - name: INFLUXDB_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: influxdb-url
        ports:
        - containerPort: 8080
```

### 1.2 ML Pipeline Deployment
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ml-pipeline
spec:
  serviceName: ml-pipeline
  replicas: 2
  selector:
    matchLabels:
      app: ml-pipeline
  template:
    metadata:
      labels:
        app: ml-pipeline
    spec:
      containers:
      - name: model-server
        image: eco-vehicle/model-server:latest
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4000m"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: model-storage
          mountPath: /models
  volumeClaimTemplates:
  - metadata:
      name: model-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
```

## 2. Database Infrastructure

### 2.1 MongoDB Cluster (with Studio 3T)
```yaml
apiVersion: mongodb.com/v1
kind: MongoDB
metadata:
  name: mongodb-cluster
spec:
  members: 3
  version: "5.0.0"
  type: ReplicaSet
  security:
    authentication:
      modes: ["SCRAM"]
  users:
    - name: eco-vehicle-app
      db: admin
      roles:
        - name: readWrite
          db: eco_vehicle
    - name: studio-3t
      db: admin
      roles:
        - name: readWrite
          db: eco_vehicle
        - name: dbAdmin
          db: eco_vehicle
  persistent:
    storage:
      class: managed-premium
      size: 100Gi
```

### 2.2 InfluxDB Configuration
```yaml
apiVersion: influxdata.com/v2beta1
kind: InfluxDB
metadata:
  name: metrics-db
spec:
  replicas: 3
  storage:
    size: 500Gi
    storageClassName: premium-ssd
  retention:
    - name: "realtime"
      duration: "24h"
      replication: 3
    - name: "hourly"
      duration: "30d"
      replication: 3
    - name: "historical"
      duration: "365d"
      replication: 2
```

## 3. Monitoring Stack

### 3.1 Prometheus Configuration
```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: eco-vehicle-prometheus
spec:
  replicas: 2
  retention: 15d
  resources:
    requests:
      memory: 400Mi
  alerting:
    alertmanagers:
    - name: alertmanager-main
      namespace: monitoring
      port: web
  serviceMonitorSelector:
    matchLabels:
      team: eco-vehicle
```

### 3.2 Grafana Dashboards
```yaml
apiVersion: grafana.integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: eco-vehicle-metrics
spec:
  json: |
    {
      "dashboard": {
        "id": null,
        "title": "Eco Vehicle Metrics",
        "panels": [
          {
            "title": "CPU Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "cpu_usage_percent",
                "legendFormat": "{{vehicle_id}}"
              }
            ]
          },
          {
            "title": "Memory Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "memory_usage_percent",
                "legendFormat": "{{vehicle_id}}"
              }
            ]
          }
        ]
      }
    }
```

## 4. CI/CD Pipeline

### 4.1 GitHub Actions Workflow
```yaml
name: Eco Vehicle CI/CD
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and Test
      run: |
        docker build -t eco-vehicle/monitor:${{ github.sha }} .
        docker run eco-vehicle/monitor:${{ github.sha }} test
    
    - name: Deploy to Dev
      if: github.ref == 'refs/heads/main'
      run: |
        kubectl apply -f k8s/
        kubectl set image deployment/eco-vehicle-monitor \
          monitor=eco-vehicle/monitor:${{ github.sha }}

  ml-pipeline:
    runs-on: ubuntu-latest
    needs: build
    steps:
    - name: Train Models
      run: |
        python train_models.py
        
    - name: Deploy Models
      run: |
        python deploy_models.py
```

## 5. Scaling Configuration

### 5.1 Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: eco-vehicle-monitor
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: eco-vehicle-monitor
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 5.2 Vertical Pod Autoscaling
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: eco-vehicle-monitor
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: eco-vehicle-monitor
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        memory: "512Mi"
        cpu: "250m"
      maxAllowed:
        memory: "4Gi"
        cpu: "2000m"
```

## 6. Security Configuration

### 6.1 Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: eco-vehicle-network-policy
spec:
  podSelector:
    matchLabels:
      app: eco-vehicle-monitor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
  - to:
    - podSelector:
        matchLabels:
          app: influxdb
    ports:
    - protocol: TCP
      port: 8086
```

### 6.2 Secret Management
```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: eco-vehicle-secrets
spec:
  provider: azure
  parameters:
    keyvaultName: eco-vehicle-kv
    objects: |
      array:
        - |
          objectName: mongodb-uri
          objectType: secret
        - |
          objectName: influxdb-url
          objectType: secret
        - |
          objectName: api-key
          objectType: secret
  secretObjects:
    - secretName: db-secrets
      type: Opaque
      data:
        - objectName: mongodb-uri
          key: MONGODB_URI
        - objectName: influxdb-url
          key: INFLUXDB_URL
```
