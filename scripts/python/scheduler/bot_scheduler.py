#!/usr/bin/env python3

import yaml
import schedule
import time
from datetime import datetime
import psutil
import logging
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

from scripts.python.data_collection.run_bots import BotRunner

class BotScheduler:
    def __init__(self):
        self.config_path = project_root / "config/bot_scheduler.yaml"
        self.load_config()
        self.setup_logging()
        self.bot_runner = BotRunner()

    def setup_logging(self):
        log_file = project_root / "logs/scheduler.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("BotScheduler")

    def load_config(self):
        """Load scheduler configuration"""
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)['scheduler_config']

    def check_system_resources(self):
        """Check if system resources meet requirements"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_space = psutil.disk_usage('/').free / (1024 * 1024)  # Convert to MB

        return (
            cpu_usage < self.config['resource_limits']['cpu_threshold'] and
            memory_usage < self.config['resource_limits']['memory_threshold'] and
            disk_space > self.config['resource_limits']['disk_space_required']
        )

    def can_run_bot(self, bot_name):
        """Check if bot can run based on conditions"""
        if not self.check_system_resources():
            self.logger.warning(f"Insufficient system resources to run {bot_name}")
            return False

        schedule_config = self.config['default_schedules'][bot_name]
        
        # Check conditions (simplified for example)
        if "system_resources_available" in schedule_config['conditions']:
            if not self.check_system_resources():
                return False
                
        if "no_active_development" in schedule_config['conditions']:
            # This would need to be implemented based on your development tracking
            pass
            
        if "system_load_below_50%" in schedule_config['conditions']:
            if psutil.cpu_percent() >= 50:
                return False

        return True

    def run_bot_with_timeout(self, bot_name):
        """Run bot with timeout and retry logic"""
        schedule_config = self.config['default_schedules'][bot_name]
        max_runtime = schedule_config['max_runtime']
        retry_attempts = schedule_config['retry_attempts']

        for attempt in range(retry_attempts):
            if not self.can_run_bot(bot_name):
                self.logger.warning(f"Cannot run {bot_name}, conditions not met")
                return

            try:
                self.logger.info(f"Starting {bot_name} (attempt {attempt + 1}/{retry_attempts})")
                
                # Run the appropriate bot method
                if bot_name == 'requirements_bot':
                    self.bot_runner.run_requirements_bot()
                elif bot_name == 'optimization_bot':
                    self.bot_runner.run_system_optimization_bot()
                elif bot_name == 'validation_bot':
                    self.bot_runner.run_validation_bot()
                
                self.logger.info(f"Successfully completed {bot_name}")
                break
            except Exception as e:
                self.logger.error(f"Error running {bot_name}: {str(e)}")
                if attempt < retry_attempts - 1:
                    time.sleep(60)  # Wait before retry
                else:
                    self.logger.error(f"Failed to run {bot_name} after {retry_attempts} attempts")

    def schedule_bots(self):
        """Schedule all bots according to configuration"""
        for bot_name, schedule_config in self.config['default_schedules'].items():
            frequency = schedule_config['frequency']
            
            if frequency == 'hourly':
                schedule.every().hour.at(":00").do(self.run_bot_with_timeout, bot_name)
            elif frequency == 'daily':
                schedule.every().day.at(schedule_config['preferred_time']).do(
                    self.run_bot_with_timeout, bot_name
                )
            elif frequency == 'weekly':
                schedule.every().monday.at(schedule_config['preferred_time']).do(
                    self.run_bot_with_timeout, bot_name
                )

        self.logger.info("All bots scheduled successfully")

    def run_scheduler(self):
        """Run the scheduler"""
        self.schedule_bots()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error

def main():
    scheduler = BotScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
