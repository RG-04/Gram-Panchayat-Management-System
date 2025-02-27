from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.utils.auth_utils import role_required
from app import db

official_bp = Blueprint('official', __name__)

@official_bp.route('/dashboard')
@role_required(['official', 'admin'])
def dashboard():
    """Official dashboard page."""
    # Get complaints assigned to this official
    complaints_query = """
        SELECT c.id, c.subject, c.status, c.priority, c.created_at, u.username as citizen
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        WHERE c.assigned_to = %s
        ORDER BY 
            CASE 
                WHEN c.priority = 'high' THEN 1
                WHEN c.priority = 'medium' THEN 2
                WHEN c.priority = 'low' THEN 3
            END,
            c.created_at DESC
    """
    complaints = db.execute_query(complaints_query, (session['user_id'],))
    
    # Get projects managed by this official
    projects_query = """
        SELECT id, name, status, start_date, end_date
        FROM projects
        WHERE manager_id = %s
        ORDER BY 
            CASE 
                WHEN status = 'in_progress' THEN 1
                WHEN status = 'planned' THEN 2
                WHEN status = 'completed' THEN 3
            END,
            start_date
    """
    projects = db.execute_query(projects_query, (session['user_id'],))
    
    return render_template(
        'official/dashboard.html',
        complaints=complaints,
        projects=projects
    )

@official_bp.route('/complaints')
@role_required(['official', 'admin'])
def complaints():
    """View all complaints page."""
    # Get all complaints with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Count total complaints for pagination
    total_count = db.execute_query(
        "SELECT COUNT(*) FROM complaints"
    )[0][0]
    
    # Get complaints with citizen info
    complaints_query = """
        SELECT c.id, c.subject, c.status, c.priority, c.created_at, 
               u.username as citizen, o.username as official
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        LEFT JOIN users o ON c.assigned_to = o.id
        ORDER BY c.created_at DESC
        LIMIT %s OFFSET %s
    """
    complaints = db.execute_query(complaints_query, (per_page, offset))
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template(
        'official/complaints.html',
        complaints=complaints,
        current_page=page,
        total_pages=total_pages
    )

@official_bp.route('/complaint/<int:complaint_id>')
@role_required(['official', 'admin'])
def view_complaint(complaint_id):
    """View a single complaint."""
    # Get complaint details
    complaint_query = """
        SELECT c.id, c.subject, c.description, c.status, c.priority, 
               c.created_at, c.updated_at, c.resolved_at,
               u.username as citizen, u.id as citizen_id,
               o.username as official, o.id as official_id
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        LEFT JOIN users o ON c.assigned_to = o.id
        WHERE c.id = %s
    """
    complaint = db.execute_query(complaint_query, (complaint_id,))
    
    if not complaint:
        flash('Complaint not found', 'error')
        return redirect(url_for('official.complaints'))
    
    # Get complaint comments
    comments_query = """
        SELECT cc.id, cc.content, cc.created_at, u.username
        FROM complaint_comments cc
        JOIN users u ON cc.user_id = u.id
        WHERE cc.complaint_id = %s
        ORDER BY cc.created_at
    """
    comments = db.execute_query(comments_query, (complaint_id,))
    
    return render_template(
        'official/view_complaint.html',
        complaint=complaint[0],
        comments=comments
    )

@official_bp.route('/add_comment/<int:complaint_id>', methods=['POST'])
@role_required(['official', 'admin'])
def add_comment(complaint_id):
    """Add a comment to a complaint."""
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('official.view_complaint', complaint_id=complaint_id))
    
    # Insert comment
    query = """
        INSERT INTO complaint_comments (complaint_id, user_id, content)
        VALUES (%s, %s, %s)
    """
    db.execute_query(
        query,
        (complaint_id, session['user_id'], content),
        fetch=False
    )
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('official.view_complaint', complaint_id=complaint_id))

@official_bp.route('/update_complaint/<int:complaint_id>', methods=['POST'])
@role_required(['official', 'admin'])
def update_complaint(complaint_id):
    """Update complaint status."""
    status = request.form.get('status')
    
    if not status:
        flash('Status is required', 'error')
        return redirect(url_for('official.view_complaint', complaint_id=complaint_id))
    
    # Update complaint status
    query = """
        UPDATE complaints
        SET status = %s, updated_at = CURRENT_TIMESTAMP
    """
    
    # If status is 'resolved', set resolved_at timestamp
    params = [status]
    if status == 'resolved':
        query += ", resolved_at = CURRENT_TIMESTAMP"
    
    query += " WHERE id = %s"
    params.append(complaint_id)
    
    db.execute_query(query, tuple(params), fetch=False)
    
    flash('Complaint updated successfully', 'success')
    return redirect(url_for('official.view_complaint', complaint_id=complaint_id))

@official_bp.route('/assign_complaint/<int:complaint_id>', methods=['POST'])
@role_required(['official', 'admin'])
def assign_complaint(complaint_id):
    """Assign complaint to an official."""
    official_id = request.form.get('official_id')
    
    # Update complaint assignment
    query = """
        UPDATE complaints
        SET assigned_to = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """
    db.execute_query(query, (official_id, complaint_id), fetch=False)
    
    flash('Complaint assigned successfully', 'success')
    return redirect(url_for('official.view_complaint', complaint_id=complaint_id))