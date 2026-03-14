# 🛡 NovaPay — Full-Stack Digital Banking System

A complete banking platform with three clients:
- **Django REST API** — Backend core
- **React Web App** — Browser frontend
- **Tkinter Desktop App** — Python GUI desktop client

---

## 📁 Project Structure

```
banking_system/
├── backend/                    # Django REST API
│   ├── banking_project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/                   # Single core app
│   │   ├── models.py           # User, Account, Transaction, Card, Loan, Notification
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── requirements.txt
│   └── manage.py
│
├── frontend/                   # React Web Application
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js          # All API calls
│   │   ├── components/
│   │   │   ├── AuthContext.js
│   │   │   ├── Sidebar.js
│   │   │   └── Topbar.js
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Dashboard.js
│   │   │   ├── Accounts.js
│   │   │   ├── Transactions.js
│   │   │   ├── Transfer.js
│   │   │   ├── Cards.js
│   │   │   ├── Loans.js
│   │   │   ├── Beneficiaries.js
│   │   │   ├── Notifications.js
│   │   │   └── Profile.js
│   │   ├── styles/
│   │   │   └── main.css        # Full design system
│   │   └── App.js
│   └── package.json
│
└── desktop/
    └── novapay_desktop.py      # Tkinter GUI application
```

---

## ⚙️ Backend Setup (Django)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

API will be available at: **http://localhost:8000/api/**
Admin panel: **http://localhost:8000/admin/**

---

## ⚛️ Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start
```

Web app will be available at: **http://localhost:3000**

> Make sure the Django backend is running first!

---

## 🖥️ Desktop App Setup (Tkinter)

```bash
cd desktop

# Install requests library (only dependency)
pip install requests

# Run the application
python novapay_desktop.py
```

> The desktop app connects to the same Django backend. Make sure it's running!

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login, returns JWT tokens |
| POST | `/api/auth/logout/` | Logout |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Accounts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/accounts/` | List accounts |
| POST | `/api/accounts/` | Create account |
| GET/PUT | `/api/accounts/{id}/` | Get/update account |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions/` | List transactions |
| POST | `/api/transactions/deposit/` | Deposit funds |
| POST | `/api/transactions/withdraw/` | Withdraw funds |
| POST | `/api/transactions/transfer/` | Transfer between accounts |

### Cards
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cards/` | List cards |
| POST | `/api/cards/{id}/toggle/` | Block/unblock card |

### Loans
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/loans/` | List loans |
| POST | `/api/loans/apply/` | Apply for loan |

### Other
- `/api/dashboard/` — Dashboard stats
- `/api/beneficiaries/` — Saved payees
- `/api/notifications/` — User notifications
- `/api/profile/` — User profile

---

## 🎨 Design System

- **Theme**: Clean professional white with `#0057FF` blue primary
- **Icons**: Bootstrap Icons (bi-*)
- **Fonts**: DM Sans (body) + Space Grotesk (headings)
- **Components**: Cards, modals, tables, stat cards, bank cards

---

## 🔒 Security Features

- JWT authentication (access + refresh tokens)
- Password validation
- Transaction fees (0.1%)
- Balance checks before withdrawals
- Atomic database transactions
- CORS configuration