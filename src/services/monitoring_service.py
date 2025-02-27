import os
import psutil
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
from database.connection_manager import DatabaseConnectionManager
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        self.db_manager = DatabaseConnectionManager()
        self.mongo = self.db_manager.get_studio3t_connection()
        self.db2_conn = self.db_manager.get_ibm_db2_connection()
        self.cloudant = self.db_manager.get_cloudant_client()
        self.cos = self.db_manager.get_object_storage_client()
        
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.register_routes()
        self.register_socket_events()
    
    def register_routes(self):
        """Register HTTP endpoints"""
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify(self.get_system_status())
        
        @self.app.route('/api/metrics')
        def get_metrics():
            return jsonify(self.get_system_metrics())
        
        @self.app.route('/api/alerts')
        def get_alerts():
            return jsonify(self.get_active_alerts())
    
    def register_socket_events(self):
        """Register WebSocket events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info("Client connected")
            emit('status', self.get_system_status())
        
        @self.socketio.on('request_metrics')
        def handle_metrics_request():
            emit('metrics', self.get_system_metrics())
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            # Check database connections
            mongo_status = self.check_mongo_status()
            db2_status = self.check_db2_status()
            cloudant_status = self.check_cloudant_status()
            
            # Check system resources
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # Determine overall status
            status = 'healthy'
            if not all([mongo_status, db2_status, cloudant_status]):
                status = 'error'
            elif cpu_usage > 80 or memory_usage > 80 or disk_usage > 80:
                status = 'warning'
            
            return {
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'components': {
                    'mongodb': mongo_status,
                    'db2': db2_status,
                    'cloudant': cloudant_status
                },
                'resources': {
                    'cpu': cpu_usage,
                    'memory': memory_usage,
                    'disk': disk_usage
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get detailed system metrics with enhanced monitoring"""
        try:
            # Get database metrics
            mongo_metrics = self.get_mongo_metrics()
            db2_metrics = self.get_db2_metrics()
            cloudant_metrics = self.get_cloudant_metrics()
            
            # Get enhanced performance metrics
            performance = self.get_enhanced_performance_metrics()
            
            # Get network metrics
            network = self.get_network_metrics()
            
            # Get storage metrics
            storage = self.get_storage_metrics()
            
            # Get application metrics
            app_metrics = self.get_application_metrics()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'databases': {
                    'mongodb': mongo_metrics,
                    'db2': db2_metrics,
                    'cloudant': cloudant_metrics
                },
                'performance': performance,
                'network': network,
                'storage': storage,
                'application': app_metrics
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
        """Get detailed system metrics"""
        try:
            # Get database metrics
            mongo_metrics = self.get_mongo_metrics()
            db2_metrics = self.get_db2_metrics()
            cloudant_metrics = self.get_cloudant_metrics()
            
            # Get performance metrics
            performance = self.get_performance_metrics()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'databases': {
                    'mongodb': mongo_metrics,
                    'db2': db2_metrics,
                    'cloudant': cloudant_metrics
                },
                'performance': performance
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        alerts = []
        
        # Check system resources
        cpu_usage = psutil.cpu_percent()
        if cpu_usage > 80:
            alerts.append({
                'type': 'warning',
                'component': 'cpu',
                'message': f'High CPU usage: {cpu_usage}%',
                'timestamp': datetime.now().isoformat()
            })
        
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            alerts.append({
                'type': 'warning',
                'component': 'memory',
                'message': f'High memory usage: {memory.percent}%',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check database health
        if not self.check_mongo_status():
            alerts.append({
                'type': 'error',
                'component': 'mongodb',
                'message': 'MongoDB connection error',
                'timestamp': datetime.now().isoformat()
            })
        
        if not self.check_db2_status():
            alerts.append({
                'type': 'error',
                'component': 'db2',
                'message': 'IBM DB2 connection error',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def check_mongo_status(self) -> bool:
        """Check MongoDB connection status"""
        try:
            self.mongo.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB error: {e}")
            return False
    
    def check_db2_status(self) -> bool:
        """Check DB2 connection status"""
        try:
            self.db2_conn.execute("SELECT 1 FROM SYSIBM.SYSDUMMY1")
            return True
        except Exception as e:
            logger.error(f"DB2 error: {e}")
            return False
    
    def check_cloudant_status(self) -> bool:
        """Check Cloudant connection status"""
        try:
            self.cloudant.get_server_information().get_result()
            return True
        except Exception as e:
            logger.error(f"Cloudant error: {e}")
            return False
    
    def get_mongo_metrics(self) -> Dict[str, Any]:
        """Get MongoDB metrics"""
        try:
            db_stats = self.mongo.cg4f_analytics.command('dbStats')
            return {
                'collections': db_stats['collections'],
                'objects': db_stats['objects'],
                'avg_obj_size': db_stats['avgObjSize'],
                'storage_size': db_stats['storageSize'],
                'indexes': db_stats['indexes']
            }
        except Exception as e:
            logger.error(f"Error getting MongoDB metrics: {e}")
            return {'error': str(e)}
    
    def get_db2_metrics(self) -> Dict[str, Any]:
        """Get DB2 metrics"""
        try:
            metrics = {}
            # Get table sizes
            query = """
                SELECT TABNAME, CARD as ROW_COUNT, NPAGES as PAGES
                FROM SYSIBM.SYSTABLES
                WHERE CREATOR = 'ANALYTICS'
            """
            result = pd.read_sql(query, self.db2_conn)
            metrics['tables'] = result.to_dict('records')
            return metrics
        except Exception as e:
            logger.error(f"Error getting DB2 metrics: {e}")
            return {'error': str(e)}
    
    def get_cloudant_metrics(self) -> Dict[str, Any]:
        """Get Cloudant metrics"""
        try:
            metrics = {}
            db_info = self.cloudant.get_database_information(
                db='cg4f_realtime'
            ).get_result()
            metrics['doc_count'] = db_info['doc_count']
            metrics['disk_size'] = db_info['disk_size']
            return metrics
        except Exception as e:
            logger.error(f"Error getting Cloudant metrics: {e}")
            return {'error': str(e)}
    
    def get_enhanced_performance_metrics(self) -> Dict[str, Any]:
        """Get enhanced system performance metrics"""
        try:
            # CPU metrics
            cpu_times = psutil.cpu_times_percent()
            cpu_freq = psutil.cpu_freq()
            cpu_stats = psutil.cpu_stats()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Process metrics
            process = psutil.Process()
            process_metrics = {
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'threads': process.num_threads(),
                'fds': process.num_fds() if hasattr(process, 'num_fds') else None
            }
            
            return {
                'cpu': {
                    'usage_percent': psutil.cpu_percent(interval=1, percpu=True),
                    'times': {
                        'user': cpu_times.user,
                        'system': cpu_times.system,
                        'idle': cpu_times.idle,
                        'iowait': cpu_times.iowait if hasattr(cpu_times, 'iowait') else None
                    },
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else None,
                        'min': cpu_freq.min if cpu_freq else None,
                        'max': cpu_freq.max if cpu_freq else None
                    },
                    'stats': {
                        'ctx_switches': cpu_stats.ctx_switches,
                        'interrupts': cpu_stats.interrupts,
                        'soft_interrupts': cpu_stats.soft_interrupts,
                        'syscalls': cpu_stats.syscalls
                    }
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'free': memory.free,
                    'percent': memory.percent,
                    'swap': {
                        'total': swap.total,
                        'used': swap.used,
                        'free': swap.free,
                        'percent': swap.percent
                    }
                },
                'process': process_metrics
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {'error': str(e)}
    
    def get_network_metrics(self) -> Dict[str, Any]:
        """Get detailed network metrics"""
        try:
            # Network I/O counters
            net_io = psutil.net_io_counters(pernic=True)
            net_connections = psutil.net_connections()
            
            # Network interfaces
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            return {
                'interfaces': {
                    name: {
                        'io_counters': {
                            'bytes_sent': stats.bytes_sent,
                            'bytes_recv': stats.bytes_recv,
                            'packets_sent': stats.packets_sent,
                            'packets_recv': stats.packets_recv,
                            'errin': stats.errin,
                            'errout': stats.errout,
                            'dropin': stats.dropin,
                            'dropout': stats.dropout
                        } if name in net_io else None,
                        'addresses': [
                            {
                                'address': addr.address,
                                'netmask': addr.netmask,
                                'broadcast': addr.broadcast,
                                'ptp': addr.ptp
                            } for addr in addrs
                        ] if name in net_if_addrs else [],
                        'stats': {
                            'isup': stats.isup,
                            'duplex': stats.duplex,
                            'speed': stats.speed,
                            'mtu': stats.mtu
                        } if name in net_if_stats else None
                    } for name, addrs in net_if_addrs.items()
                },
                'connections': {
                    'established': len([c for c in net_connections if c.status == 'ESTABLISHED']),
                    'listen': len([c for c in net_connections if c.status == 'LISTEN']),
                    'time_wait': len([c for c in net_connections if c.status == 'TIME_WAIT']),
                    'close_wait': len([c for c in net_connections if c.status == 'CLOSE_WAIT'])
                }
            }
        except Exception as e:
            logger.error(f"Error getting network metrics: {e}")
            return {'error': str(e)}
    
    def get_storage_metrics(self) -> Dict[str, Any]:
        """Get detailed storage metrics"""
        try:
            # Disk usage and I/O counters
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters(perdisk=True)
            disk_partitions = psutil.disk_partitions()
            
            return {
                'usage': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': disk_usage.percent
                },
                'io_counters': {
                    disk: {
                        'read_count': counters.read_count,
                        'write_count': counters.write_count,
                        'read_bytes': counters.read_bytes,
                        'write_bytes': counters.write_bytes,
                        'read_time': counters.read_time,
                        'write_time': counters.write_time
                    } for disk, counters in disk_io.items()
                },
                'partitions': [
                    {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts
                    } for partition in disk_partitions
                ]
            }
        except Exception as e:
            logger.error(f"Error getting storage metrics: {e}")
            return {'error': str(e)}
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        try:
            # Database connection pools
            db_connections = {
                'mongodb': self.mongo.cg4f_analytics.command('serverStatus')['connections'],
                'db2': self.db2_conn.get_stats() if hasattr(self.db2_conn, 'get_stats') else None,
                'cloudant': self.cloudant.get_server_information().get_result()
            }
            
            # Query performance
            query_stats = {
                'mongodb': self.mongo.cg4f_analytics.command('profile', -1),
                'db2': None,  # Implement DB2-specific query stats
                'cloudant': None  # Implement Cloudant-specific query stats
            }
            
            # Cache statistics
            cache_stats = {
                'size': 0,  # Implement cache size tracking
                'hits': 0,  # Implement cache hit tracking
                'misses': 0  # Implement cache miss tracking
            }
            
            return {
                'database_connections': db_connections,
                'query_performance': query_stats,
                'cache': cache_stats,
                'response_times': {
                    'avg': 0,  # Implement response time tracking
                    'p95': 0,  # Implement 95th percentile tracking
                    'p99': 0   # Implement 99th percentile tracking
                }
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {'error': str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'cpu': {
                'usage': psutil.cpu_percent(interval=1, percpu=True),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            }
        }
    
    def run(self, host: str = '0.0.0.0', port: int = 5000):
        """Run the monitoring service"""
        logger.info(f"Starting monitoring service on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port)

def main():
    """Run the monitoring service"""
    service = MonitoringService()
    service.run()

if __name__ == '__main__':
    main()
