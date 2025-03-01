from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from app import db
from app.queries.admin_queries import admin_queries

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def admin_required(f):
    """Decorator to require admin login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    flash('Admin logged out', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard page."""
    # Get all table names
    
    tables = db.execute_query(admin_queries['tables_query'])
    
    # Get all columns for each table
    table_columns = {}
    for table in tables:
        table_name = table[0]
        
        columns = db.execute_query(admin_queries['columns_query'], (table_name,))
        table_columns[table_name] = columns
    
    return render_template(
        'admin/dashboard.html',
        tables=tables,
        table_columns=table_columns
    )

@admin_bp.route('/execute', methods=['POST'])
@admin_required
def execute_query():
    """Execute a SQL query."""
    query = request.form.get('query', '')
    
    if not query.strip():
        flash('Query cannot be empty', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        # Determine if the query is a SELECT query
        is_select = query.strip().upper().startswith('SELECT')
        
        # Execute the query
        result = db.execute_query(query, fetch=is_select)
        
        if is_select:
            # If it's a SELECT query, get column names
            if result:
                # Execute a query to get column names for the result set
                column_names = []
                
                # Use the column descriptions from the cursor
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute(query)
                column_names = [desc[0] for desc in cursor.description]
                cursor.close()
                
                flash('Query executed successfully', 'success')
                return render_template(
                    'admin/execute_result.html',
                    query=query,
                    result=result,
                    column_names=column_names,
                    is_select=True
                )
            else:
                flash('Query executed successfully, but returned no rows', 'success')
                return render_template(
                    'admin/execute_result.html',
                    query=query,
                    result=[],
                    column_names=[],
                    is_select=True
                )
        else:
            # For non-SELECT queries
            flash('Query executed successfully', 'success')
            return render_template(
                'admin/execute_result.html',
                query=query,
                result=None,
                column_names=None,
                is_select=False
            )
    except Exception as e:
        flash(f'Error executing query: {str(e)}', 'error')
        return render_template(
            'admin/execute_result.html',
            query=query,
            error=str(e),
            is_select=None
        )