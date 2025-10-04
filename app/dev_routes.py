"""
Developer routes for debugging and monitoring.
This file contains development-only routes that should NEVER be enabled in production.
"""

from flask import Blueprint, render_template, request
from app import db
from app.models import User, Candidate, Vote
import os
import platform
import psutil
import socket
from flask import current_app
from datetime import datetime

dev = Blueprint('dev', __name__, url_prefix='/dev')

@dev.route('/dashboard')
def dev_dashboard():
    """Developer dashboard - LOCAL DEVELOPMENT ONLY"""
    # Only allow access from localhost
    if request.remote_addr not in ['127.0.0.1', 'localhost', '::1']:
        return "Access denied: Developer dashboard only available locally", 403

    # Database contents
    users = User.query.all()
    candidates = Candidate.query.all()
    votes = Vote.query.all()

    # System information
    system_info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'hostname': socket.gethostname(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
        'memory_used': f"{psutil.virtual_memory().used / (1024**3):.1f} GB",
        'disk_free': f"{psutil.disk_usage('/').free / (1024**3):.1f} GB",
    }

    # App information
    app_info = {
        'flask_version': current_app.config.get('VERSION', 'Unknown'),
        'debug_mode': current_app.debug,
        'testing_mode': current_app.testing,
        'database_uri': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
        'secret_key_configured': bool(current_app.config.get('SECRET_KEY')),
    }

    # Read log files (last 50 lines each)
    def read_last_lines(filepath, lines=50):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()
                return ''.join(content[-lines:])
        except Exception as e:
            return f"Error reading file: {e}"

    # Web server logs (Flask logs)
    web_logs = "Flask application logs not available in development mode"

    # WAF logs (nginx access/error logs)
    nginx_access_log = read_last_lines('nginx-access.log')
    nginx_error_log = read_last_lines('nginx-error.log')

    # Database file info
    db_path = os.path.join(current_app.instance_path, 'app.db')
    db_info = {
        'path': db_path,
        'exists': os.path.exists(db_path),
        'size': f"{os.path.getsize(db_path) / 1024:.1f} KB" if os.path.exists(db_path) else "N/A",
        'modified': datetime.fromtimestamp(os.path.getmtime(db_path)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(db_path) else "N/A"
    }

    return render_template('dev_dashboard.html',
                         users=users,
                         candidates=candidates,
                         votes=votes,
                         system_info=system_info,
                         app_info=app_info,
                         web_logs=web_logs,
                         nginx_access_log=nginx_access_log,
                         nginx_error_log=nginx_error_log,
                         db_info=db_info)