% System Interface for MATLAB-Python Integration
% This file handles the communication between MATLAB and the Python monitoring system

classdef SystemInterface < handle
    properties (Access = private)
        pythonPath
        vehicleSystem
    end
    
    methods
        function obj = SystemInterface()
            % Initialize the interface
            obj.pythonPath = fullfile(pwd, '..', '..', 'src');
            obj.vehicleSystem = VehicleSystem();
            
            % Add Python path
            if count(py.sys.path, obj.pythonPath) == 0
                insert(py.sys.path, int32(0), obj.pythonPath);
            end
        end
        
        function startMonitoring(obj)
            % Import Python modules
            monitoring = py.importlib.import_module('monitoring.system_monitor');
            dashboard = py.importlib.import_module('monitoring.dashboard');
            
            % Create monitor instance
            monitor = py.monitoring.system_monitor.SystemMonitor();
            
            % Create callback for metric updates
            function callback(metrics)
                % Convert Python dict to MATLAB struct
                metricStruct = struct();
                for k = py.list(metrics.keys())
                    key = char(k);
                    value = double(metrics{k});
                    metricStruct.(key) = value;
                end
                
                % Update vehicle system
                obj.vehicleSystem.updateMetrics(metricStruct);
                
                % Plot updates
                obj.vehicleSystem.plotSystemOverview();
                drawnow;
            end
            
            % Set up timer for periodic updates
            t = timer('ExecutionMode', 'fixedRate', ...
                     'Period', 1, ...
                     'TimerFcn', @(~,~) callback(monitor.collect_metrics()));
            start(t);
        end
        
        function exportToCameo(obj)
            % Export current state to Cameo-compatible format
            timestamp = datetime('now');
            filename = sprintf('cameo_export_%s.xml', ...
                             datestr(timestamp, 'yyyymmdd_HHMMSS'));
            
            % Create XML structure
            docNode = com.mathworks.xml.XMLUtils.createDocument('ComponentState');
            root = docNode.getDocumentElement;
            
            % Add components
            components = {'Dashboard', 'MetricsCollector', ...
                         'PerformanceAnalyzer', 'EnvironmentalMonitor'};
            
            for i = 1:length(components)
                comp = docNode.createElement('Component');
                comp.setAttribute('name', components{i});
                comp.setAttribute('health', ...
                    num2str(obj.vehicleSystem.componentHealth(components{i})));
                root.appendChild(comp);
            end
            
            % Add metrics
            metrics = docNode.createElement('Metrics');
            fields = {'batteryLevel', 'cpuUsage', 'memoryUsage', ...
                     'networkLatency', 'environmentalScore'};
            
            for i = 1:length(fields)
                metric = docNode.createElement('Metric');
                metric.setAttribute('name', fields{i});
                metric.setAttribute('value', ...
                    num2str(obj.vehicleSystem.(fields{i})));
                metrics.appendChild(metric);
            end
            
            root.appendChild(metrics);
            
            % Write to file
            xmlwrite(fullfile('models', 'cameo', filename), docNode);
        end
    end
end
