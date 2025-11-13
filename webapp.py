import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import csv
from io import StringIO
from flask import Response
from models import db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Expense
from sqlalchemy import func

def create_app():
    """
    Create and configure the Flask application with routes for managing expenses.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')  # Use env var for production
    database_uri = 'sqlite:///budgetbuddy.db'
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Convert postgres:// to postgresql:// for SQLAlchemy
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        database_uri = db_url
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        """
        Main page to add new expenses and list all expenses.
        """
        if request.method == 'POST':
            d = request.form.get('date') or date.today().isoformat()
            cat = request.form.get('category', '').strip()
            amt = request.form.get('amount', '').strip()
            notes = request.form.get('notes', '').strip()
            try:
                amt = float(amt)
                new_expense = Expense(date=d, category=cat, amount=amt, notes=notes, user_id=current_user.id)
                db.session.add(new_expense)
                db.session.commit()
            except Exception as e:
                return f"Error: {e}", 400
            return redirect(url_for('index'))
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', expenses=expenses)

    @app.route('/edit/<int:id>')
    @login_required
    def edit(id):
        """
        Render the edit page for a specific expense by ID.
        """
        expense = Expense.query.filter_by(id=id, user_id=current_user.id).first()
        if not expense:
            return "Expense not found", 404
        return render_template('edit.html', expense=expense)

    @app.route('/update/<int:id>', methods=['POST'])
    @login_required
    def update(id):
        """
        Handle updating an existing expense.
        """
        expense = Expense.query.filter_by(id=id, user_id=current_user.id).first()
        if not expense:
            return "Expense not found", 404
        d = request.form.get('date')
        cat = request.form.get('category', '').strip()
        amt = request.form.get('amount', '').strip()
        notes = request.form.get('notes', '').strip()
        try:
            amt = float(amt)
            expense.date = d
            expense.category = cat
            expense.amount = amt
            expense.notes = notes
            db.session.commit()
        except Exception as e:
            return f"Error: {e}", 400
        return redirect(url_for('index'))

    @app.route('/delete/<int:id>', methods=['POST'])
    @login_required
    def delete(id):
        """
        Handle deleting an expense by ID.
        """
        expense = Expense.query.filter_by(id=id, user_id=current_user.id).first()
        if expense:
            db.session.delete(expense)
            db.session.commit()
        return redirect(url_for('index'))

    @app.route('/summary')
    @login_required
    def summary():
        """
        Show summary page with total expenses and breakdown by category.
        """
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        total = sum(e.amount for e in expenses)
        categories = {}
        for e in expenses:
            cat = e.category
            categories[cat] = categories.get(cat, 0) + e.amount
        return render_template('summary.html', total=total, categories=categories)

    @app.route('/category', methods=['GET', 'POST'])
    @login_required
    def category():
        """
        View expenses filtered by category.
        """
        expenses = []
        selected_category = None
        if request.method == 'POST':
            selected_category = request.form.get('category', '').strip()
            if selected_category:
                expenses = Expense.query.filter_by(category=selected_category, user_id=current_user.id).all()
        return render_template('category.html', expenses=expenses, selected_category=selected_category)

    @app.route('/date-range', methods=['GET', 'POST'])
    @login_required
    def date_range():
        """
        View expenses filtered by a date range.
        """
        expenses = []
        start_date = None
        end_date = None
        error = None
        if request.method == 'POST':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            if not start_date or not end_date:
                error = "Please provide both start and end dates."
            else:
                try:
                    expenses = Expense.query.filter(Expense.date >= start_date, Expense.date <= end_date, Expense.user_id == current_user.id).all()
                except Exception as e:
                    error = str(e)
        return render_template('date_range.html', expenses=expenses, start_date=start_date, end_date=end_date, error=error)

    @app.route('/export')
    @login_required
    def export():
        """
        Export all expenses as a CSV file download.
        """
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Date', 'Category', 'Amount', 'Notes'])
        for e in expenses:
            cw.writerow([e.date, e.category, e.amount, e.notes])
        output = si.getvalue()
        return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=expenses.csv"})

    @app.route('/monthly-summary')
    @login_required
    def monthly_summary():
        """
        Show monthly summary of expenses aggregated by month.
        """
        from sqlalchemy import text
        summary = db.session.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(Expense.user_id == current_user.id).group_by('month').order_by(text('month DESC')).all()
        return render_template('monthly_summary.html', summary=summary)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if User.query.filter_by(username=username).first():
                return 'User already exists'
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            return 'Invalid credentials'
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/exit', methods=['POST'])
    @login_required
    def exit_app():
        """
        Handle exit action from the web page by logging out and redirecting to login.
        """
        logout_user()
        return redirect(url_for('login'))

    @app.route('/view')
    @login_required
    def view_expenses():
        # Show only current_user's expenses
        expenses = current_user.expenses
        return render_template('index.html', expenses=expenses)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
