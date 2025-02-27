"""
Agile Process Monitor and Validator.
Helps teams maintain Agile best practices and avoid common anti-patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

class AgileMetricType(Enum):
    """Types of Agile metrics to monitor"""
    CUSTOMER_COLLABORATION = "customer_collaboration"
    ITERATION_REVIEWS = "iteration_reviews"
    DAILY_STANDUPS = "daily_standups"
    TECHNICAL_DEBT = "technical_debt"
    CROSS_FUNCTIONAL = "cross_functional"
    SPRINT_GOALS = "sprint_goals"
    RETROSPECTIVES = "retrospectives"
    PROCESS_ADHERENCE = "process_adherence"
    TEAM_AUTONOMY = "team_autonomy"
    COMMUNICATION = "communication"

@dataclass
class AgileMetric:
    """Represents a measurable Agile practice metric"""
    metric_type: AgileMetricType
    value: float  # 0-1 score
    timestamp: datetime
    details: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class SprintData:
    """Captures data about a sprint"""
    sprint_id: str
    start_date: datetime
    end_date: datetime
    goals: List[str]
    completed_goals: List[str]
    velocity: float
    burndown_data: List[tuple[datetime, float]]
    metrics: Dict[AgileMetricType, AgileMetric]
    retrospective_actions: List[str]
    technical_debt_items: List[str]

class AgileProcessMonitor:
    """Monitors and validates Agile practices"""

    def __init__(self):
        self.sprints: Dict[str, SprintData] = {}
        self.current_sprint: Optional[str] = None
        self.warning_thresholds = {
            AgileMetricType.CUSTOMER_COLLABORATION: 0.7,
            AgileMetricType.ITERATION_REVIEWS: 0.8,
            AgileMetricType.DAILY_STANDUPS: 0.8,
            AgileMetricType.TECHNICAL_DEBT: 0.6,
            AgileMetricType.CROSS_FUNCTIONAL: 0.7,
            AgileMetricType.SPRINT_GOALS: 0.75,
            AgileMetricType.RETROSPECTIVES: 0.8,
            AgileMetricType.PROCESS_ADHERENCE: 0.7,
            AgileMetricType.TEAM_AUTONOMY: 0.8,
            AgileMetricType.COMMUNICATION: 0.8
        }

    def start_sprint(self, sprint_id: str, goals: List[str], duration_days: int = 14) -> None:
        """Start a new sprint with specified goals"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        self.sprints[sprint_id] = SprintData(
            sprint_id=sprint_id,
            start_date=start_date,
            end_date=end_date,
            goals=goals,
            completed_goals=[],
            velocity=0.0,
            burndown_data=[],
            metrics={},
            retrospective_actions=[],
            technical_debt_items=[]
        )
        self.current_sprint = sprint_id

    def record_metric(self, metric_type: AgileMetricType, value: float, details: Dict[str, str]) -> None:
        """Record a metric for the current sprint"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        
        metric = AgileMetric(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            details=details
        )
        
        # Generate warnings and recommendations
        if value < self.warning_thresholds[metric_type]:
            self._generate_warnings(metric)
        
        sprint.metrics[metric_type] = metric

    def _generate_warnings(self, metric: AgileMetric) -> None:
        """Generate warnings and recommendations for low metric values"""
        warnings_map = {
            AgileMetricType.CUSTOMER_COLLABORATION: (
                "Low customer involvement detected",
                ["Schedule regular customer feedback sessions",
                 "Implement a customer feedback loop",
                 "Document and address customer concerns promptly"]
            ),
            AgileMetricType.ITERATION_REVIEWS: (
                "Inconsistent iteration reviews",
                ["Schedule reviews in advance",
                 "Make reviews mandatory",
                 "Keep reviews focused and time-boxed"]
            ),
            AgileMetricType.DAILY_STANDUPS: (
                "Ineffective daily standups",
                ["Limit standup duration to 15 minutes",
                 "Focus on blockers and coordination",
                 "Use a consistent format: done/doing/blocked"]
            ),
            AgileMetricType.TECHNICAL_DEBT: (
                "Increasing technical debt",
                ["Allocate time for debt reduction in each sprint",
                 "Maintain a technical debt backlog",
                 "Set clear criteria for acceptable technical debt"]
            ),
            AgileMetricType.CROSS_FUNCTIONAL: (
                "Limited cross-functional collaboration",
                ["Organize cross-functional workshops",
                 "Rotate pair programming partners",
                 "Create shared responsibility for features"]
            ),
            AgileMetricType.SPRINT_GOALS: (
                "Sprint goals may be unrealistic",
                ["Use historical velocity for planning",
                 "Break down goals into smaller tasks",
                 "Include buffer for unexpected issues"]
            ),
            AgileMetricType.RETROSPECTIVES: (
                "Retrospectives need improvement",
                ["Focus on actionable improvements",
                 "Track retrospective action items",
                 "Vary retrospective formats to maintain engagement"]
            ),
            AgileMetricType.PROCESS_ADHERENCE: (
                "Over-emphasis on process over principles",
                ["Review Agile Manifesto principles",
                 "Focus on value delivery",
                 "Adapt processes to team needs"]
            ),
            AgileMetricType.TEAM_AUTONOMY: (
                "Limited team autonomy",
                ["Empower team decision-making",
                 "Reduce external dependencies",
                 "Support self-organization"]
            ),
            AgileMetricType.COMMUNICATION: (
                "Communication needs improvement",
                ["Establish clear communication channels",
                 "Document decisions and rationale",
                 "Regular team building activities"]
            )
        }
        
        warning, recommendations = warnings_map[metric.metric_type]
        metric.warnings.append(warning)
        metric.recommendations.extend(recommendations)

    def add_technical_debt(self, description: str, severity: str) -> None:
        """Record a technical debt item"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        sprint.technical_debt_items.append(f"{severity}: {description}")

    def record_retrospective(self, actions: List[str]) -> None:
        """Record retrospective action items"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        sprint.retrospective_actions.extend(actions)

    def update_burndown(self, remaining_work: float) -> None:
        """Update sprint burndown data"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        sprint.burndown_data.append((datetime.now(), remaining_work))

    def complete_goal(self, goal: str) -> None:
        """Mark a sprint goal as completed"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        if goal in sprint.goals and goal not in sprint.completed_goals:
            sprint.completed_goals.append(goal)

    def get_sprint_health(self) -> Dict[str, float]:
        """Calculate overall sprint health metrics"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        metrics = sprint.metrics
        
        return {
            "customer_satisfaction": metrics.get(AgileMetricType.CUSTOMER_COLLABORATION, AgileMetric(AgileMetricType.CUSTOMER_COLLABORATION, 0, datetime.now())).value,
            "team_velocity": len(sprint.completed_goals) / len(sprint.goals) if sprint.goals else 0,
            "technical_debt": metrics.get(AgileMetricType.TECHNICAL_DEBT, AgileMetric(AgileMetricType.TECHNICAL_DEBT, 0, datetime.now())).value,
            "process_health": sum(m.value for m in metrics.values()) / len(metrics) if metrics else 0
        }

    def get_recommendations(self) -> Dict[AgileMetricType, List[str]]:
        """Get all current recommendations for improvement"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        return {
            metric_type: metric.recommendations
            for metric_type, metric in sprint.metrics.items()
            if metric.recommendations
        }

    def export_sprint_report(self) -> Dict[str, any]:
        """Generate a comprehensive sprint report"""
        if not self.current_sprint:
            raise ValueError("No active sprint")
        
        sprint = self.sprints[self.current_sprint]
        health = self.get_sprint_health()
        
        return {
            "sprint_id": sprint.sprint_id,
            "duration": {
                "start": sprint.start_date.isoformat(),
                "end": sprint.end_date.isoformat()
            },
            "goals": {
                "total": len(sprint.goals),
                "completed": len(sprint.completed_goals),
                "completion_rate": len(sprint.completed_goals) / len(sprint.goals) if sprint.goals else 0
            },
            "health_metrics": health,
            "technical_debt": {
                "items": sprint.technical_debt_items,
                "count": len(sprint.technical_debt_items)
            },
            "retrospective": {
                "actions": sprint.retrospective_actions,
                "count": len(sprint.retrospective_actions)
            },
            "warnings": [
                {str(metric_type): metric.warnings}
                for metric_type, metric in sprint.metrics.items()
                if metric.warnings
            ],
            "recommendations": self.get_recommendations()
        }
