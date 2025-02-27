from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required, hash_password
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@role_required(['admin'])
def dashboard():
    """Admin dashboard page."""
    # Fetch counts for dashboard widgets
    citizen_count = db.execute_query("SELECT COUNT(*) FROM users WHERE role = 'citizen'")[0][0]
    official_count = db.execute_query("SELECT COUNT(*) FROM users WHERE role = 'official'")[0][0]
    complaint_count = db.execute_query("SELECT COUNT(*) FROM complaints")[0][0]
    project_count = db.execute_query("SELECT COUNT(*) FROM projects")[0][0]
    
    return render_template(
        'admin/dashboard.html',
        citizen_count=citizen_count,
        official_count=official_count,
        complaint_count=complaint_count,
        project_count=project_count
    )

@admin_bp.route('/users')
@role_required(['admin'])
def users():
    """Manage users page."""
    # Fetch all users except current user
    query = """
        SELECT id, username, role, created_at
        FROM users
        WHERE id != %s
        ORDER BY role, username
    """
    users_list = db.execute_query(query, (session['user_id'],))
    
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@role_required(['admin'])
def add_user():
    """Add a new user page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validate input
        if not username or not password or not role:
            flash('All fields are required', 'error')
            return redirect(url_for('admin.add_user'))
        
        # Check if username already exists
        exists = db.execute_query(
            "SELECT COUNT(*) FROM users WHERE username = %s",
            (username,)
        )[0][0]
        
        if exists > 0:
            flash('Username already exists', 'error')
            return redirect(url_for('admin.add_user'))
        
        # Hash the password
        pw_hash, salt = hash_password(password)
        
        # Insert the new user
        query = """
            INSERT INTO users (username, password_hash, salt, role, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """
        db.execute_query(
            query,
            (username, pw_hash, salt, role, session['user_id']),
            fetch=False
        )
        
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@role_required(['admin'])
def delete_user(user_id):
    """Delete a user."""
    # Prevent self-deletion
    if user_id == session['user_id']:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.users'))
    
    # Delete the user
    db.execute_query(
        "DELETE FROM users WHERE id = %s",
        (user_id,),
        fetch=False
    )
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@role_required(['admin'])
def reset_password(user_id):
    """Reset a user's password."""
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        
        if not new_password:
            flash('Password is required', 'error')
            return redirect(url_for('admin.reset_password', user_id=user_id))
        
        # Hash the new password
        pw_hash, salt = hash_password(new_password)
        
        # Update the user's password
        query = """
            UPDATE users
            SET password_hash = %s, salt = %s
            WHERE id = %s
        """
        db.execute_query(
            query,
            (pw_hash, salt, user_id),
            fetch=False
        )
        
        flash('Password reset successfully', 'success')
        return redirect(url_for('admin.users'))
    
    # Get the username for display
    username = db.execute_query(
        "SELECT username FROM users WHERE id = %s",
        (user_id,)
    )[0][0]
    
    return render_template('admin/reset_password.html', user_id=user_id, username=username)