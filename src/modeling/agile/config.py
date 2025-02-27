"""
Configuration settings for Agile process monitoring.
"""

from typing import Dict, List

# Sprint configuration
DEFAULT_SPRINT_LENGTH_DAYS = 14
MAX_SPRINT_LENGTH_DAYS = 30
MIN_SPRINT_LENGTH_DAYS = 7

# Meeting durations (minutes)
MEETING_DURATIONS = {
    "daily_standup": 15,
    "sprint_planning": 120,
    "sprint_review": 60,
    "retrospective": 60
}

# Warning thresholds (0-1 scale)
METRIC_THRESHOLDS = {
    "customer_collaboration": 0.7,
    "iteration_reviews": 0.8,
    "daily_standups": 0.8,
    "technical_debt": 0.6,
    "cross_functional": 0.7,
    "sprint_goals": 0.75,
    "retrospectives": 0.8,
    "process_adherence": 0.7,
    "team_autonomy": 0.8,
    "communication": 0.8
}

# Technical debt severity levels
TECH_DEBT_SEVERITY = [
    "critical",
    "high",
    "medium",
    "low"
]

# Required sprint ceremonies
REQUIRED_CEREMONIES = [
    "sprint_planning",
    "daily_standup",
    "sprint_review",
    "retrospective"
]

# Best practices checklist
BEST_PRACTICES = {
    "planning": [
        "Define clear sprint goals",
        "Break down work into small tasks",
        "Estimate tasks collaboratively",
        "Consider team capacity",
        "Include technical debt reduction"
    ],
    "execution": [
        "Daily standups",
        "Regular pair programming",
        "Continuous integration",
        "Automated testing",
        "Code reviews"
    ],
    "review": [
        "Demo working software",
        "Gather stakeholder feedback",
        "Document decisions",
        "Update documentation",
        "Review technical debt"
    ],
    "retrospective": [
        "Celebrate successes",
        "Identify improvements",
        "Create action items",
        "Track previous actions",
        "Rotate facilitator"
    ]
}

# Communication guidelines
COMMUNICATION_GUIDELINES = {
    "daily_standup": [
        "What did you complete?",
        "What are you working on?",
        "What blockers do you have?"
    ],
    "sprint_review": [
        "Demo completed work",
        "Gather feedback",
        "Discuss next priorities"
    ],
    "retrospective": [
        "What went well?",
        "What could be improved?",
        "What actions should we take?"
    ]
}

# Metrics to track
METRICS_TO_TRACK = {
    "velocity": {
        "description": "Number of story points completed per sprint",
        "target_trend": "stable or increasing"
    },
    "cycle_time": {
        "description": "Time from task start to completion",
        "target_trend": "decreasing"
    },
    "technical_debt": {
        "description": "Number of technical debt items",
        "target_trend": "decreasing"
    },
    "customer_satisfaction": {
        "description": "Customer feedback score",
        "target_trend": "increasing"
    },
    "team_morale": {
        "description": "Team happiness score",
        "target_trend": "stable or increasing"
    }
}

# Warning signs and remedies
WARNING_SIGNS = {
    "decreasing_velocity": [
        "Review sprint commitments",
        "Check for external blockers",
        "Assess team capacity"
    ],
    "increasing_technical_debt": [
        "Allocate time for debt reduction",
        "Review definition of done",
        "Improve code review process"
    ],
    "missing_ceremonies": [
        "Schedule ceremonies in advance",
        "Make attendance mandatory",
        "Keep ceremonies focused"
    ],
    "low_collaboration": [
        "Encourage pair programming",
        "Schedule team building",
        "Rotate team roles"
    ]
}

# Success criteria
SUCCESS_CRITERIA = {
    "sprint": [
        "All sprint goals achieved",
        "No critical bugs introduced",
        "Technical debt managed",
        "Customer feedback positive"
    ],
    "release": [
        "Features meet requirements",
        "Performance targets met",
        "Documentation complete",
        "Customer acceptance"
    ]
}

# Continuous improvement focus areas
IMPROVEMENT_AREAS = [
    "Technical practices",
    "Team collaboration",
    "Customer engagement",
    "Process efficiency",
    "Quality assurance"
]
