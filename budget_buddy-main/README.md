
## 💰 BudgetBuddy — Secure Expense Tracker in Flask

**BudgetBuddy** is a modular, privacy-focused expense tracking app built with Python and Flask. It empowers users to log, analyze, and manage their daily expenses securely, with personalized dashboards, exportable insights, and visual analytics.

---

### 🚀 Features

- 🔐 **User Registration & Login**  
  Each user has a secure account with password hashing and session management.

- 🕵️‍♂️ **Expense Privacy Per User**  
  Users can only view and manage their own expenses—no shared views or data leaks.

- 📤 **Export to CSV**  
  Download your expense history in spreadsheet format for offline analysis or sharing.

- 📊 **Chart-Based Analytics**  
  Visualize your spending trends with dynamic charts—track categories, dates, and totals.

- 🧾 **CRUD Operations**  
  Add, view, update, and delete expenses with intuitive forms and clean UI.

- 🎨 **Bootstrap Styling + Favicon Branding**  
  Responsive design with a custom favicon for a polished, cinematic experience.

---

### 🧱 Tech Stack

- **Python 3.10+**  
- **Flask** — Web framework  
- **SQLite** — Lightweight database  
- **Flask-Login** — User authentication  
- **Werkzeug** — Password hashing  
- **Bootstrap** — UI styling  
- **Chart.js / Plotly** — Data visualization  
- **Jinja2** — Templating engine

---

### 📦 Installation

```bash
git clone https://github.com/GASH10TH/Budget-Buddy.git
cd Budget-Buddy
pip install -r requirements.txt
python app.py
```

Then open your browser at:  
`http://127.0.0.1:5000`

---

### 📁 Project Structure

```
Budget-Buddy/
├── app.py             # Main Flask app logic
├── db.py              # Database operations
├── modelkey.py        # User model and authentication logic
├── webpage.py         # Chart rendering and export logic
├── budgetbuddy.db     # SQLite database
├── templates/         # HTML templates (login, dashboard, forms)
├── static/            # CSS, JS, favicon files
├── README.md          # Project overview
├── TODO.md            # Development notes and future plans
└── requirements.txt   # Python dependencies
```

---

### 🌱 Future Enhancements
 Email reminders for budget goals  
- Mobile-friendly UI  
- Multi-language support (including Telugu)  
- AI-powered spending suggestions  
- Role-based access for teachers/admins

