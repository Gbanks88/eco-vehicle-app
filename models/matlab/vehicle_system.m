% MATLAB Interface for Eco-Vehicle System
% This file provides the interface between MATLAB/Simulink and our monitoring system

classdef VehicleSystem < handle
    properties
        % System components
        batteryLevel
        cpuUsage
        memoryUsage
        networkLatency
        environmentalScore
        
        % Component status
        componentHealth
        
        % Data history
        metricsHistory
    end
    
    methods
        function obj = VehicleSystem()
            % Initialize system
            obj.batteryLevel = 100;
            obj.cpuUsage = 0;
            obj.memoryUsage = 0;
            obj.networkLatency = 0;
            obj.environmentalScore = 100;
            obj.componentHealth = containers.Map();
            obj.metricsHistory = containers.Map();
            
            % Initialize component health
            obj.componentHealth('Dashboard') = 1.0;
            obj.componentHealth('MetricsCollector') = 1.0;
            obj.componentHealth('PerformanceAnalyzer') = 1.0;
            obj.componentHealth('EnvironmentalMonitor') = 1.0;
        end
        
        function updateMetrics(obj, metrics)
            % Update system metrics
            if isfield(metrics, 'battery_level')
                obj.batteryLevel = metrics.battery_level;
            end
            if isfield(metrics, 'cpu_usage')
                obj.cpuUsage = metrics.cpu_usage;
            end
            if isfield(metrics, 'memory_usage')
                obj.memoryUsage = metrics.memory_usage;
            end
            if isfield(metrics, 'network_latency')
                obj.networkLatency = metrics.network_latency;
            end
            if isfield(metrics, 'environmental_score')
                obj.environmentalScore = metrics.environmental_score;
            end
            
            % Update history
            timestamp = datetime('now');
            for field = fieldnames(metrics)'
                fname = field{1};
                if ~isKey(obj.metricsHistory, fname)
                    obj.metricsHistory(fname) = [];
                end
                obj.metricsHistory(fname) = [obj.metricsHistory(fname); ...
                    [timestamp, metrics.(fname)]];
            end
            
            % Update component health based on metrics
            obj.updateComponentHealth();
        end
        
        function updateComponentHealth(obj)
            % Update health status of components based on metrics
            if obj.cpuUsage > 80
                obj.componentHealth('MetricsCollector') = 0.5;
            else
                obj.componentHealth('MetricsCollector') = 1.0;
            end
            
            if obj.memoryUsage > 90
                obj.componentHealth('PerformanceAnalyzer') = 0.5;
            else
                obj.componentHealth('PerformanceAnalyzer') = 1.0;
            end
            
            if obj.environmentalScore < 70
                obj.componentHealth('EnvironmentalMonitor') = 0.5;
            else
                obj.componentHealth('EnvironmentalMonitor') = 1.0;
            end
        end
        
        function plotSystemOverview(obj)
            % Create system overview visualization
            figure('Name', 'System Overview', 'NumberTitle', 'off');
            
            % Plot metrics
            subplot(2,2,1);
            plot(obj.metricsHistory('cpu_usage')(:,1), ...
                 obj.metricsHistory('cpu_usage')(:,2));
            title('CPU Usage');
            ylabel('%');
            grid on;
            
            subplot(2,2,2);
            plot(obj.metricsHistory('memory_usage')(:,1), ...
                 obj.metricsHistory('memory_usage')(:,2));
            title('Memory Usage');
            ylabel('%');
            grid on;
            
            subplot(2,2,3);
            plot(obj.metricsHistory('network_latency')(:,1), ...
                 obj.metricsHistory('network_latency')(:,2));
            title('Network Latency');
            ylabel('ms');
            grid on;
            
            subplot(2,2,4);
            plot(obj.metricsHistory('battery_level')(:,1), ...
                 obj.metricsHistory('battery_level')(:,2));
            title('Battery Level');
            ylabel('%');
            grid on;
        end
    end
end
