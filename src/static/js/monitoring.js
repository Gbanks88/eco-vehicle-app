// Initialize Vue app
new Vue({
    el: '.monitoring-dashboard',
    data: {
        metrics: {
            databases: {
                mongodb: { status: 'healthy', connections: 45, latency: 12 },
                db2: { status: 'healthy', connections: 32, latency: 15 },
                cloudant: { status: 'healthy', connections: 28, latency: 18 }
            },
            performance: {
                cpu: {
                    usage: 45,
                    times: {},
                    frequency: {},
                    stats: {}
                },
                memory: {
                    total: 16000000000,
                    used: 8000000000,
                    free: 8000000000,
                    percent: 50,
                    swap: {}
                },
                process: {}
            },
            network: {
                throughput: 1500000,
                connections: {
                    established: 124,
                    listen: 12,
                    time_wait: 8,
                    close_wait: 2
                },
                interfaces: {}
            },
            storage: {
                usage: {
                    total: 1000000000000,
                    used: 400000000000,
                    free: 600000000000,
                    percent: 40
                },
                io_stats: {
                    operations: 250,
                    read_bytes: 1000000,
                    write_bytes: 500000
                },
                partitions: []
            }
        },
        alerts: [
            {
                id: 1,
                type: 'warning',
                title: 'High CPU Usage',
                message: 'CPU usage has exceeded 80% threshold',
                icon: 'mdi-cpu-64-bit'
            }
        ]
    },
    methods: {
        getStatusClass(status) {
            const statusMap = {
                'healthy': 'status-healthy',
                'warning': 'status-warning',
                'error': 'status-error'
            };
            return statusMap[status.toLowerCase()] || 'status-error';
        },
        
        formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        updateCharts() {
            // Update CPU chart
            Plotly.update('cpuChart', {
                y: [[this.metrics.performance.cpu.usage]]
            });
            
            // Update Memory chart
            Plotly.update('memoryChart', {
                y: [[this.metrics.performance.memory.percent]]
            });
            
            // Update Disk chart
            Plotly.update('diskChart', {
                values: [
                    this.metrics.storage.usage.used,
                    this.metrics.storage.usage.free
                ]
            });
            
            // Update Network chart
            Plotly.update('networkChart', {
                y: [[
                    this.metrics.network.throughput
                ]]
            });
        },
        
        initCharts() {
            // CPU Usage Chart
            Plotly.newPlot('cpuChart', [{
                y: [this.metrics.performance.cpu.usage],
                type: 'line',
                line: { color: '#2196F3' },
                fill: 'tozeroy'
            }], {
                margin: { t: 0, b: 30, l: 30, r: 10 },
                yaxis: { range: [0, 100] },
                showlegend: false
            });
            
            // Memory Usage Chart
            Plotly.newPlot('memoryChart', [{
                y: [this.metrics.performance.memory.percent],
                type: 'line',
                line: { color: '#4CAF50' },
                fill: 'tozeroy'
            }], {
                margin: { t: 0, b: 30, l: 30, r: 10 },
                yaxis: { range: [0, 100] },
                showlegend: false
            });
            
            // Disk Usage Chart
            Plotly.newPlot('diskChart', [{
                values: [
                    this.metrics.storage.usage.used,
                    this.metrics.storage.usage.free
                ],
                labels: ['Used', 'Free'],
                type: 'pie',
                marker: {
                    colors: ['#FF5722', '#E0E0E0']
                }
            }], {
                margin: { t: 0, b: 0, l: 0, r: 0 },
                showlegend: true,
                legend: { orientation: 'h' }
            });
            
            // Network Traffic Chart
            Plotly.newPlot('networkChart', [{
                y: [this.metrics.network.throughput],
                type: 'line',
                line: { color: '#9C27B0' },
                fill: 'tozeroy'
            }], {
                margin: { t: 0, b: 30, l: 30, r: 10 },
                showlegend: false
            });
        },
        
        simulateMetricsUpdate() {
            // Simulate real-time updates
            setInterval(() => {
                // Update CPU usage
                this.metrics.performance.cpu.usage = Math.floor(Math.random() * 30) + 40;
                
                // Update memory usage
                this.metrics.performance.memory.percent = Math.floor(Math.random() * 20) + 40;
                
                // Update network throughput
                this.metrics.network.throughput = Math.floor(Math.random() * 2000000);
                
                // Update storage I/O
                this.metrics.storage.io_stats.operations = Math.floor(Math.random() * 300) + 100;
                
                // Update charts
                this.updateCharts();
            }, 2000);
        }
    },
    mounted() {
        this.initCharts();
        this.simulateMetricsUpdate();
    }
});
