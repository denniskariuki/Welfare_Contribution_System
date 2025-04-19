
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import RegistrationForm, LoginForm, ContributionForm, WithdrawalRequestForm, ApproveWithdrawalForm, RejectWithdrawalForm, EditUserForm
from app.models import User, Contribution, Withdrawal
from datetime import datetime
from app import app, db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    contributions = Contribution.query.filter_by(user_id=current_user.id).order_by(Contribution.contribution_date.desc()).all()
    withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.request_date.desc()).all()
    return render_template('dashboard.html', contributions=contributions, withdrawals=withdrawals)

@app.route('/contribute', methods=['GET', 'POST'])
@login_required
def contribute():
    form = ContributionForm()
    if form.validate_on_submit():
        contribution = Contribution(user_id=current_user.id, amount=form.amount.data, description=form.description.data)
        db.session.add(contribution)
        current_user.balance += form.amount.data
        db.session.commit()
        flash('Contribution recorded!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('contribute.html', form=form)

@app.route('/request_withdrawal', methods=['GET', 'POST'])
@login_required
def request_withdrawal():
    form = WithdrawalRequestForm()
    if form.validate_on_submit():
        if form.amount.data > current_user.balance:
            flash('Insufficient balance!', 'danger')
        else:
            withdrawal = Withdrawal(user_id=current_user.id, amount=form.amount.data, reason=form.reason.data)
            db.session.add(withdrawal)
            db.session.commit()
            flash('Withdrawal request submitted!', 'info')
            return redirect(url_for('dashboard'))
    return render_template('request_withdrawal.html', form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    users_count = User.query.count()
    pending_withdrawals_count = Withdrawal.query.filter_by(approval_status='pending').count()
    total_contributions = db.session.query(db.func.sum(Contribution.amount)).scalar() or 0
    return render_template('admin/dashboard.html', users_count=users_count, pending_withdrawals_count=pending_withdrawals_count, total_contributions=total_contributions)

@app.route('/admin/manage_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash('User information updated!', 'success')
        return redirect(url_for('admin_manage_users'))
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/manage_withdrawals')
@login_required
def manage_withdrawals():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    withdrawals = Withdrawal.query.order_by(Withdrawal.request_date.desc()).all()
    return render_template('admin/manage_withdrawals.html', withdrawals=withdrawals)

@app.route('/admin/approve_withdrawal/<int:withdrawal_id>', methods=['GET', 'POST'])
@login_required
def approve_withdrawal(withdrawal_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    form = ApproveWithdrawalForm()
    if form.validate_on_submit():
        if withdrawal.approval_status == 'pending':
            user = User.query.get(withdrawal.user_id)
            if user and user.balance >= withdrawal.amount:
                user.balance -= withdrawal.amount
                withdrawal.approval_status = 'approved'
                withdrawal.approval_date = datetime.utcnow()
                withdrawal.approved_by_admin_id = current_user.id
                withdrawal.notes = form.notes.data
                db.session.commit()
                flash(f'Withdrawal of KES {withdrawal.amount} approved for {user.username}!', 'success')
                return redirect(url_for('admin_manage_withdrawals'))
            else:
                flash(f'Insufficient balance for {user.username} to approve this withdrawal.', 'danger')
        else:
            flash('This withdrawal has already been processed.', 'warning')
        return render_template('admin/approve_withdrawal.html', form=form, withdrawal=withdrawal)
    return render_template('admin/approve_withdrawal.html', form=form, withdrawal=withdrawal)

@app.route('/admin/reject_withdrawal/<int:withdrawal_id>', methods=['GET', 'POST'])
@login_required
def reject_withdrawal(withdrawal_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    form = RejectWithdrawalForm()
    if form.validate_on_submit():
        if withdrawal.approval_status == 'pending':
            withdrawal.approval_status = 'rejected'
            withdrawal.approval_date = datetime.utcnow()
            withdrawal.approved_by_admin_id = current_user.id
            withdrawal.notes = form.notes.data
            db.session.commit()
            flash(f'Withdrawal of KES {withdrawal.amount} rejected for User ID {withdrawal.user_id}.', 'info')
            return redirect(url_for('admin_manage_withdrawals'))
        else:
            flash('This withdrawal has already been processed.', 'warning')
        return render_template('admin/reject_withdrawal.html', form=form, withdrawal=withdrawal)
    return render_template('admin/reject_withdrawal.html', form=form, withdrawal=withdrawal)