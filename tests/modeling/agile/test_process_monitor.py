"""Tests for the Agile Process Monitor"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from freezegun import freeze_time

from src.modeling.agile.process_monitor import (
    AgileProcessMonitor,
    AgileMetric,
    AgileMetricType,
    SprintData
)

@pytest.fixture
def monitor():
    """Create a test process monitor"""
    return AgileProcessMonitor()

@pytest.fixture
def active_sprint(monitor):
    """Create an active sprint"""
    sprint_id = "SPRINT-2025-01"
    monitor.start_sprint(
        sprint_id=sprint_id,
        goals=[
            "Implement feature X",
            "Refactor component Y",
            "Update documentation"
        ]
    )
    return sprint_id

def test_sprint_creation(monitor):
    """Test basic sprint creation"""
    sprint_id = "TEST-SPRINT-1"
    goals = ["Goal 1", "Goal 2"]
    
    monitor.start_sprint(sprint_id, goals)
    
    assert monitor.current_sprint == sprint_id
    assert sprint_id in monitor.sprints
    sprint = monitor.sprints[sprint_id]
    assert sprint.goals == goals
    assert len(sprint.completed_goals) == 0
    assert len(sprint.metrics) == 0

def test_metric_recording(monitor, active_sprint):
    """Test recording and validating metrics"""
    # Record customer collaboration metric
    monitor.record_metric(
        metric_type=AgileMetricType.CUSTOMER_COLLABORATION,
        value=0.8,
        details={
            "feedback_sessions": 3,
            "implemented_suggestions": 5
        }
    )
    
    # Record daily standup metric
    monitor.record_metric(
        metric_type=AgileMetricType.DAILY_STANDUPS,
        value=0.9,
        details={
            "attendance_rate": "95%",
            "average_duration": "12 minutes"
        }
    )
    
    sprint = monitor.sprints[active_sprint]
    assert len(sprint.metrics) == 2
    assert AgileMetricType.CUSTOMER_COLLABORATION in sprint.metrics
    assert AgileMetricType.DAILY_STANDUPS in sprint.metrics

def test_warning_generation(monitor, active_sprint):
    """Test warning generation for low metric values"""
    # Record a low technical debt metric
    monitor.record_metric(
        metric_type=AgileMetricType.TECHNICAL_DEBT,
        value=0.3,  # Below threshold
        details={
            "debt_items": 15,
            "critical_items": 5
        }
    )
    
    sprint = monitor.sprints[active_sprint]
    metric = sprint.metrics[AgileMetricType.TECHNICAL_DEBT]
    
    assert len(metric.warnings) > 0
    assert len(metric.recommendations) > 0
    assert any("technical debt" in warning.lower() for warning in metric.warnings)

def test_sprint_health_calculation(monitor, active_sprint):
    """Test sprint health calculation"""
    # Record various metrics
    metrics_data = [
        (AgileMetricType.CUSTOMER_COLLABORATION, 0.8),
        (AgileMetricType.DAILY_STANDUPS, 0.9),
        (AgileMetricType.TECHNICAL_DEBT, 0.7),
        (AgileMetricType.SPRINT_GOALS, 0.85)
    ]
    
    for metric_type, value in metrics_data:
        monitor.record_metric(
            metric_type=metric_type,
            value=value,
            details={}
        )
    
    # Complete some goals
    monitor.complete_goal("Implement feature X")
    monitor.complete_goal("Update documentation")
    
    health = monitor.get_sprint_health()
    assert isinstance(health, dict)
    assert "customer_satisfaction" in health
    assert "team_velocity" in health
    assert "technical_debt" in health
    assert "process_health" in health
    
    # Verify team velocity calculation
    assert health["team_velocity"] == 2/3  # 2 completed out of 3 goals

def test_technical_debt_tracking(monitor, active_sprint):
    """Test technical debt tracking"""
    # Add technical debt items
    debt_items = [
        ("Refactor authentication module", "high"),
        ("Update deprecated API calls", "medium"),
        ("Improve test coverage", "low")
    ]
    
    for description, severity in debt_items:
        monitor.add_technical_debt(description, severity)
    
    sprint = monitor.sprints[active_sprint]
    assert len(sprint.technical_debt_items) == 3
    assert any("high: Refactor authentication" in item for item in sprint.technical_debt_items)

def test_retrospective_recording(monitor, active_sprint):
    """Test retrospective action recording"""
    actions = [
        "Improve code review process",
        "Schedule more customer feedback sessions",
        "Reduce meeting durations"
    ]
    
    monitor.record_retrospective(actions)
    
    sprint = monitor.sprints[active_sprint]
    assert len(sprint.retrospective_actions) == 3
    assert all(action in sprint.retrospective_actions for action in actions)

@freeze_time("2025-02-24")
def test_burndown_tracking(monitor, active_sprint):
    """Test sprint burndown tracking"""
    # Simulate burndown over several days
    remaining_work = [
        (datetime.now(), 100),
        (datetime.now() + timedelta(days=1), 80),
        (datetime.now() + timedelta(days=2), 60),
        (datetime.now() + timedelta(days=3), 30)
    ]
    
    for date, work in remaining_work:
        with freeze_time(date):
            monitor.update_burndown(work)
    
    sprint = monitor.sprints[active_sprint]
    assert len(sprint.burndown_data) == 4
    assert sprint.burndown_data[-1][1] == 30  # Last remaining work

def test_sprint_validation(monitor):
    """Test sprint validation"""
    # Test invalid sprint duration
    with pytest.raises(ValueError):
        monitor.start_sprint("INVALID", [], duration_days=0)
    
    # Test duplicate sprint ID
    sprint_id = "DUPLICATE"
    monitor.start_sprint(sprint_id, ["Goal"])
    with pytest.raises(ValueError):
        monitor.start_sprint(sprint_id, ["Another Goal"])

def test_metric_validation(monitor, active_sprint):
    """Test metric validation"""
    # Test invalid metric value
    with pytest.raises(ValueError):
        monitor.record_metric(
            metric_type=AgileMetricType.CUSTOMER_COLLABORATION,
            value=1.5,  # Should be between 0 and 1
            details={}
        )
    
    # Test recording metric without active sprint
    monitor.current_sprint = None
    with pytest.raises(ValueError):
        monitor.record_metric(
            metric_type=AgileMetricType.DAILY_STANDUPS,
            value=0.8,
            details={}
        )

def test_sprint_report_generation(monitor, active_sprint):
    """Test sprint report generation"""
    # Add various data points
    monitor.record_metric(
        metric_type=AgileMetricType.CUSTOMER_COLLABORATION,
        value=0.8,
        details={"feedback_sessions": 3}
    )
    monitor.add_technical_debt("Legacy code", "high")
    monitor.record_retrospective(["Improve CI/CD"])
    monitor.complete_goal("Implement feature X")
    
    report = monitor.export_sprint_report()
    
    assert isinstance(report, dict)
    assert "sprint_id" in report
    assert "goals" in report
    assert "health_metrics" in report
    assert "technical_debt" in report
    assert "retrospective" in report
    assert "recommendations" in report

def test_recommendations_generation(monitor, active_sprint):
    """Test recommendations generation"""
    # Record metrics that will trigger recommendations
    monitor.record_metric(
        metric_type=AgileMetricType.TEAM_AUTONOMY,
        value=0.5,  # Below threshold
        details={"decision_making": "limited"}
    )
    monitor.record_metric(
        metric_type=AgileMetricType.COMMUNICATION,
        value=0.6,  # Below threshold
        details={"missed_standups": 2}
    )
    
    recommendations = monitor.get_recommendations()
    
    assert isinstance(recommendations, dict)
    assert len(recommendations) == 2
    assert AgileMetricType.TEAM_AUTONOMY in recommendations
    assert AgileMetricType.COMMUNICATION in recommendations
    assert all(len(recs) > 0 for recs in recommendations.values())
