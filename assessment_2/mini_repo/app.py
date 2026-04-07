"""
Mini Task Manager API — Flask Application
Contains an intentional pagination bug for Assessment 2.
"""

import os
import sqlite3
from flask import Flask, request, jsonify
from models import init_db, get_db, Task
from utils import paginate_results


app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), "tasks.db")


@app.before_request
def before_request():
    """Initialize database connection before each request."""
    if not hasattr(app, '_db_initialized'):
        init_db(DATABASE)
        app._db_initialized = True


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    """
    List tasks with pagination.
    
    Query params:
        page (int): Page number (1-indexed, default: 1)
        per_page (int): Items per page (default: 10, max: 50)
        status (str): Filter by status (optional)
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        status_filter = request.args.get("status")
        
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 50:
            return jsonify({"error": "per_page must be between 1 and 50"}), 400
        
        db = get_db(DATABASE)
        
        if status_filter:
            tasks = db.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY id",
                (status_filter,)
            ).fetchall()
        else:
            tasks = db.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        
        task_list = [Task.from_row(row).to_dict() for row in tasks]
        
        # Paginate results — BUG IS IN THIS FUNCTION
        result = paginate_results(task_list, page, per_page)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400
    except Exception as e:
        app.logger.error(f"Error listing tasks: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a single task by ID."""
    try:
        db = get_db(DATABASE)
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        
        if row is None:
            return jsonify({"error": "Task not found"}), 404
        
        return jsonify(Task.from_row(row).to_dict())
        
    except Exception as e:
        app.logger.error(f"Error getting task {task_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    try:
        data = request.get_json()
        if not data or "title" not in data:
            return jsonify({"error": "Title is required"}), 400
        
        db = get_db(DATABASE)
        cursor = db.execute(
            "INSERT INTO tasks (title, description, status, priority) VALUES (?, ?, ?, ?)",
            (data["title"], data.get("description", ""), 
             data.get("status", "todo"), data.get("priority", "medium"))
        )
        db.commit()
        
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(Task.from_row(row).to_dict()), 201
        
    except Exception as e:
        app.logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
