# Finance Flow

Finance Flow is a web-based personal finance management application built with Flask and MongoDB. It helps users track their income, expenses, set budgets, and visualize their financial data with interactive charts and reports.

## Features

- User registration and login
- Add, view, and manage transactions (income & expenses)
- Set and monitor monthly budgets
- Dashboard with visualizations (pie charts, bar graphs)
- Generate monthly financial reports
- Secure data storage with MongoDB

## Screenshots

![Dashboard](static/income_expense_pie.png)
![Expense Breakdown](static/expense_breakdown_pie.png)
![Monthly Report](static/monthly_report_bar.png)

## Getting Started

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- MongoDB Atlas account (or local MongoDB instance)

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/iamvishalpoddar/Finance_Flow.git
   cd Finance_Flow
   ```
2. **Install dependencies:**
   ```bash
   pip install flask pymongo
   ```
   *(Or use `pip install -r requirements.txt` if available)*

3. **Configure MongoDB:**
   - Update the MongoDB connection string in `database/mongo.py` if needed.

4. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Project Structure
```
Finance_Flow/
├── app.py
├── database/
│   └── mongo.py
├── static/
│   └── [charts and images]
├── templates/
│   └── [HTML templates]
└── ...
```

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

