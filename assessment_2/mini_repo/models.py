"""
Data models for the Mini Task Manager.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str
    priority: str
    created_at: str
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_row(cls, row):
        return cls(
            id=row[0],
            title=row[1],
            description=row[2],
            status=row[3],
            priority=row[4],
            created_at=row[5]
        )


def get_db(db_path: str) -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = None  # Use tuple rows
    return conn


def init_db(db_path: str):
    """Initialize the database with schema and seed data."""
    conn = sqlite3.connect(db_path)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'done', 'blocked')),
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'critical')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if data already exists
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        _seed_tasks(conn)
    
    conn.commit()
    conn.close()


def _seed_tasks(conn):
    """Seed 30 sample tasks for testing pagination."""
    tasks = [
        ("Set up CI/CD pipeline", "Configure GitHub Actions for automated testing and deployment", "done", "high"),
        ("Design user dashboard", "Create wireframes for the main dashboard view", "done", "high"),
        ("Implement user authentication", "Add JWT-based auth with refresh tokens", "done", "critical"),
        ("Write API documentation", "Document all REST endpoints using OpenAPI spec", "in_progress", "medium"),
        ("Fix login redirect bug", "Users redirected to wrong page after login", "done", "high"),
        ("Add search functionality", "Implement full-text search across tasks", "in_progress", "medium"),
        ("Optimize database queries", "Add indexes and optimize slow queries", "todo", "high"),
        ("Create onboarding flow", "Design and implement new user onboarding", "in_progress", "medium"),
        ("Set up monitoring alerts", "Configure PagerDuty alerts for critical metrics", "todo", "high"),
        ("Update dependencies", "Upgrade Flask and SQLAlchemy to latest versions", "todo", "low"),
        ("Implement rate limiting", "Add API rate limiting to prevent abuse", "todo", "medium"),
        ("Design email templates", "Create HTML templates for transactional emails", "done", "low"),
        ("Add unit tests for auth", "Write tests for authentication module", "in_progress", "high"),
        ("Fix pagination bug", "Pagination returns wrong results on last page", "todo", "critical"),
        ("Implement file upload", "Add support for task attachments", "todo", "medium"),
        ("Create admin panel", "Build admin interface for user management", "todo", "low"),
        ("Add websocket support", "Real-time updates using WebSockets", "todo", "medium"),
        ("Implement caching layer", "Add Redis caching for frequently accessed data", "todo", "high"),
        ("Security audit", "Conduct security review of all endpoints", "in_progress", "critical"),
        ("Write integration tests", "End-to-end tests for critical user flows", "todo", "high"),
        ("Mobile responsive design", "Ensure dashboard works on mobile devices", "in_progress", "medium"),
        ("Add export functionality", "Export tasks to CSV and PDF formats", "todo", "low"),
        ("Implement webhooks", "Allow users to configure webhook notifications", "todo", "low"),
        ("Performance load testing", "Run load tests to identify bottlenecks", "todo", "medium"),
        ("Add dark mode", "Implement dark mode toggle for the UI", "done", "low"),
        ("Database backup setup", "Configure automated daily database backups", "done", "critical"),
        ("Implement task comments", "Allow users to add comments on tasks", "in_progress", "medium"),
        ("Add task dependencies", "Allow tasks to depend on other tasks", "todo", "medium"),
        ("Create changelog page", "Auto-generated changelog from git commits", "todo", "low"),
        ("Setup staging environment", "Configure staging environment for QA testing", "done", "high"),
    ]
    
    for title, desc, status, priority in tasks:
        conn.execute(
            "INSERT INTO tasks (title, description, status, priority) VALUES (?, ?, ?, ?)",
            (title, desc, status, priority)
        )
