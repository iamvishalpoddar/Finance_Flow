from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_jwt_extended import jwt_required, JWTManager, create_access_token, get_jwt_identity, set_access_cookies
import json
from database.mongo import reg_db, finance_db, budget_db
from datetime import datetime
import uuid
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from fpdf import FPDF
import os


app = Flask(__name__)
app.secret_key = "T2lvLJmNQ2lDrVUpfSY"
app.config["JWT_SECRET_KEY"] = "T2lvLJnNQ2lDrVUpfSY"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)


@app.route("/", methods = ['GET', 'POST'])
def handle_home():
    return render_template("home.html")


@app.route("/register", methods = ["GET", "POST"])
def handle_register():
    status = ""
    temp = False
    if request.method == "POST":
        reg_data = request.form.to_dict()
        email = request.form.get("email")
        data = reg_db['Details'].find()
        data_li = []
        for item in data:
            del item['_id']
            data_li.append(item)
        for item in data_li:
            if email == item["email"]:
                temp = True
                status = "User Already Registered"
                break
        if temp == False: 
            reg_db['Details'].insert_one(reg_data)
            return redirect('/login')
    return render_template("register.html", status = status)


@app.route("/login", methods = ["GET", "POST"])
def handle_login():
    status = ""
    if request.method == "POST":
        email = request.form.get("email")
        pw = request.form.get("password")
        data = reg_db['Details'].find()
        data_li = []
        for item in data:
            del item['_id']
            data_li.append(item)
        for item in data_li:
            if item['email'] == email and item['password'] == pw:
                token = create_access_token(identity=email)
                response = redirect('/dashboard')
                set_access_cookies(response, token)
                return response
                break
            else:
                status = "Invalid credentials!"
    return render_template("login.html", status = status)


@app.route("/dashboard", methods = ["GET"])
@jwt_required(locations=['cookies'])
def handle_news():
    email = get_jwt_identity()
    user_details = reg_db['Details'].find_one({"email" : email})
    user_name = user_details['name']
    trans_li = list(finance_db['Finance-Details'].find({"email": email}))
    total_income = 0
    for item in trans_li:
        if item['type'] == "Income":
            total_income += int(item['amount'])
    total_expense = 0
    for item in trans_li:
        if item['type'] == "Expense":
            total_expense += int(item['amount'])
    saving = total_income - total_expense
    budget_li = list(budget_db['Budget-Details'].find({"email" : email}))
    temp = False
    for item in budget_li:
        if item['month'].lower() == datetime.now().strftime("%B").lower() or item['month'].lower() == datetime.now().strftime("%b").lower():
            temp = True
            current_budget = int(item['budget'])
            break
    if temp == False:
        current_budget = "No budget set yet"
    soreted_li = sorted(trans_li, key=lambda d: d['date'], reverse=True)
    length = len(soreted_li)
    return render_template("dashboard.html", income = total_income, expense = total_expense, saving = saving, budget = current_budget, user_name = user_name, sorted_li = soreted_li, length = length)


@app.route("/transactions/add", methods = ["GET", "POST"])
@jwt_required(locations=['cookies'])
def handle_add_transaction():
    unique_id = 1
    if request.method == "POST":
        email = get_jwt_identity()
        form_data = request.form.to_dict()
        if not form_data.get("title") or not form_data.get("amount"):
            flash("Please fill in all the fields!", "error")
        else:
            trans_data = {
                **form_data,
                "email": email,
                "date": datetime.now().strftime("%d-%m-%Y, %H:%M:%S"),
                "unique_id" : str(uuid.uuid4())
            }
            finance_db['Finance-Details'].insert_one(trans_data)
            flash("Transaction added successfully!", "success")
    return render_template("add_trans.html")

@app.route("/transactions/view", methods = ["GET", "POST"])
@jwt_required(locations=['cookies'])
def handle_view_transaction():
    email = get_jwt_identity()
    trans_li = list(finance_db['Finance-Details'].find({"email": email}))
    sorted_li = sorted(trans_li, key=lambda d: d['date'], reverse=True)
    return render_template("view_trans.html", trans_li =  sorted_li)


@app.route('/transactions/del', methods = ["POST"])
@jwt_required(locations=['cookies'])
def handle_del():
    if request.method == "POST":
        id = request.form.get('unique_id')
        finance_db['Finance-Details'].delete_one({'unique_id' : id})
        email = get_jwt_identity()
        trans_li = list(finance_db['Finance-Details'].find({"email": email}))
        flash("Transaction deleted successfully!", "success")
    return render_template("view_trans.html", trans_li =  trans_li)

@app.route("/transactions/budget/set", methods = ["GET", "POST"])
@jwt_required(locations=['cookies'])
def handle_set_budget():
    if request.method == "POST":
        email = get_jwt_identity()
        budget_data = request.form.to_dict()
        if not budget_data.get("month") or not budget_data.get("budget"):
            flash("Please fill in all the fields!", "error")
        else:
            input_month = budget_data.get("month").lower()

            month_to_delete_full = ""
            month_to_delete_abbr = ""

            try:
                month_to_delete_full = datetime.strptime(input_month, "%B").strftime("%B")
                month_to_delete_abbr = datetime.strptime(input_month, "%B").strftime("%b")
            except ValueError:
                try:
                    month_to_delete_full = datetime.strptime(input_month, "%b").strftime("%B")
                    month_to_delete_abbr = datetime.strptime(input_month, "%b").strftime("%b")
                except ValueError:
                    flash("Invalid month format. Please use full month name (e.g., January) or abbreviation (e.g., Jan).", "error")
                    return render_template("budget.html")

            budget_db['Budget-Details'].delete_many({
                "email": email,
                "$or": [
                    {"month": month_to_delete_full},
                    {"month": month_to_delete_abbr}
                ]
            })

            budget_data["email"] = email
            budget_data["month"] = month_to_delete_full
            budget_db['Budget-Details'].insert_one(budget_data)
            flash("Budget set successfully!", "success")
    return render_template("budget.html")

@app.route("/transactions/report", methods = ["GET", "POST"])
@jwt_required(locations=['cookies'])
def handle_report():
    email = get_jwt_identity()
    trans_li = list(finance_db['Finance-Details'].find({"email": email}))
    total_income = 0
    for item in trans_li:
        if item['type'] == "Income":
            total_income += int(item['amount'])
    total_expense = 0
    for item in trans_li:
        if item['type'] == "Expense":
            total_expense += int(item['amount'])
    x = ["Income", "Expense"]
    y = [total_income, total_expense]
    plt.pie(y, labels=x, autopct="%.2f%%", startangle=90)
    plt.title("income vs expense")
    plt.savefig("static/income_expense_pie.png", bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.clf()
    title_li = [item for item in trans_li if item['type'] == "Expense"]
    category_dict = {}
    for item in title_li:
        if item['title'] in category_dict:
            category_dict[item['title']] += int(item['amount'])
        else:
            category_dict[item['title']] = int(item['amount'])
    x = list(category_dict.keys())
    y = list(category_dict.values())
    plt.pie(y, labels=x, autopct="%.2f%%", startangle=90)
    plt.title("Detailed Expense Category Breakdown")
    plt.savefig("static/expense_breakdown_pie.png", bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.clf()
    income = {
        'January': 0, 'February': 0, 'March': 0, 'April': 0,
        'May': 0, 'June': 0, 'July': 0, 'August': 0,
        'September': 0, 'October': 0, 'November': 0, 'December': 0
    }
    for item in trans_li:
        if item['type'] == 'Income':
            month = datetime.strptime(item['date'], "%d-%m-%Y, %H:%M:%S").strftime("%B")
            income[month] += int(item['amount'])
    x = list(income.keys())
    y_1 = list(income.values())
    expense = {
        'January': 0, 'February': 0, 'March': 0, 'April': 0,
        'May': 0, 'June': 0, 'July': 0, 'August': 0,
        'September': 0, 'October': 0, 'November': 0, 'December': 0
    }
    for item in trans_li:
        if item['type'] == "Expense":
            month = datetime.strptime(item['date'], "%d-%m-%Y, %H:%M:%S").strftime("%B")
            expense[month] += int(item['amount'])
    y_2 = list(expense.values())
    x_pos = list(range(len(x))) 
    plt.figure(figsize=(14, 6))
    plt.bar([p - 0.2 for p in x_pos], y_1, width=0.4, label="Income", color="green")
    plt.bar([p + 0.2 for p in x_pos], y_2, width=0.4, label="Expense", color="red")
    plt.xticks(x_pos, x)
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.title("Monthly Income vs Expense")
    plt.legend()
    plt.savefig("static/monthly_report_bar.png", bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.clf()
    return render_template("report.html")


@app.route("/transactions/download_pdf")
@jwt_required(locations=['cookies'])
def download_transactions_pdf():
    email = get_jwt_identity()
    trans_li = list(finance_db['Finance-Details'].find({"email": email}))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    pdf.cell(200, 10, txt = "Your Transactions", 
             ln = 1, align = 'C')
    pdf.ln(10)
    if not trans_li:
        pdf.cell(200, 10, txt = "No transactions to display.", ln = 1, align = 'C')
    else:
        pdf.set_font("Arial", size = 10, style='B')
        pdf.cell(50, 10, "Title", 1, 0, 'C')
        pdf.cell(30, 10, "Type", 1, 0, 'C')
        pdf.cell(40, 10, "Amount", 1, 0, 'C')
        pdf.cell(70, 10, "Date", 1, 1, 'C')
        pdf.set_font("Arial", size = 10)
        sorted_li = sorted(trans_li, key=lambda d: d['date'], reverse=True)
        for trans in sorted_li:
            pdf.cell(50, 10, trans.get('title', 'N/A'), 1, 0, 'C')
            pdf.cell(30, 10, trans.get('type', 'N/A'), 1, 0, 'C')
            amount_str = f"Rs. {trans.get('amount', 'N/A')}"
            pdf.cell(40, 10, amount_str, 1, 0, 'C')
            pdf.cell(70, 10, trans.get('date', 'N/A'), 1, 1, 'C')
    pdf_output_path = os.path.join(app.root_path, "transactions.pdf")
    pdf.output(pdf_output_path)
    return send_file(pdf_output_path, as_attachment=True, download_name="your_transactions.pdf")


@app.route('/logout', methods = ["GET", "POST"])
@jwt_required(locations=['cookies'])
def handle_logout():
    email = get_jwt_identity()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)