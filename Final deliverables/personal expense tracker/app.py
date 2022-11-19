from flask import (
    Flask,
    render_template,
    send_file,
    request,
    redirect,
    url_for,
    session,
    flash,
)

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ibm_db
import re
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO

app = Flask(__name__)
app.secret_key = "Zenik"

conn = ibm_db.connect(
    "DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt; UID=dwd46636;PWD=vPVuK2TjmxDVRVeA",'',''
)



@app.route("/", methods=["POST", "GET"])
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(username,password)
        sql = "SELECT * FROM REGISTER WHERE email=? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['loggedin'] = True
            session['id'] = account['EMAIL']
            session["email"] = account["EMAIL"]
            session['username'] = account['USERNAME']
            msg = 'Logged in successfully !'

            return redirect("/dashboard")
        else:
            msg = "Incorrect login credentials"
    flash(msg)
    return render_template("login.html", title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password1 = request.form["password1"]
        sql = "SELECT * FROM REGISTER WHERE username =? or email=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        
        if account:
            msg = "Account already exists"
        elif password1 != password:
            msg = "re-entered password doesnt match"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username should be only alphabets and numbers"
        else:
            sql = "INSERT INTO REGISTER(USERNAME,EMAIL,PASSWORD) VALUES(?,?,?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, email)
            ibm_db.bind_param(stmt, 3, password)
            ibm_db.execute(stmt)


            message = Mail(
                from_email=os.environ.get('MAIL_DEFAULT_SENDER'),
                to_emails=email,
                subject='Welcome',
                html_content='<p>Hello, Your Registration was successfull. <br><br> Thank you for choosing us.</p>')
            try:
              sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
              response = sg.send(message)
              print(response.status_code)

            except Exception as e:
              print(e.message)

        return redirect("/login")     
            
    flash(msg)
    return render_template("register.html", title="Register")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def isLogged():
    return session["Loggedin"]


@app.route("/dashboard")
def dashboard():
    if isLogged:
        return render_template("dashboard.html", title="Dashboard")
    else:
        flash("Login to go to dashboard")
        return redirect("/login")


@app.route("/changePassword/", methods=["POST", "GET"])
def changePassword():
    msg = "Enter the new password"
    if request.method == "POST":
        pass1 = request.form["pass1"]
        pass2 = request.form["pass2"]
        if pass1 == pass2:
            sql = "UPDATE REGISTER SET password=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, pass1)
            # ibm_db.bind_param(stmt, 2, session["id"])
            if ibm_db.execute(stmt):
                msg = "Successfully Changed Password!!!!"

        else:
            msg = "Passwords not equal"
    flash(msg)
    return redirect(url_for("dashboard"))


@app.route("/changeBudget/", methods=["POST", "GET"])
def changeBudget():
    msg = "Enter the new budget"
    if request.method == "POST":
        budgetAmount = request.form["budgetAmount"]
        sql = "UPDATE BUDGETS SET maxBudget=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, budgetAmount)
        # ibm_db.bind_param(stmt, 2, session["id"])
        if ibm_db.execute(stmt):
            session["budget"] = budgetAmount
            msg = "Successfully Changed Budget!!!!"
        else:
            msg = "Budget not changed"
    flash(msg)
    return redirect(url_for("dashboard"))


@app.route("/addBudget/", methods=["POST", "GET"])
def addBudget():
    msg = "Enter the budget"
    if request.method == "POST":
        budgetAmount = request.form["budgetAmountToAdd"]
        sql = "INSERT INTO BUDGETS(id,maxbudget) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session["id"])
        ibm_db.bind_param(stmt, 2, budgetAmount)
        if ibm_db.execute(stmt):
            session["budget"] = budgetAmount
            msg = "Successfully Set The Budget!!!!"
        else:
            msg = "Budget not set yet"
    flash(msg)
    return redirect(url_for("dashboard"))


def fetchall(stmt):
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    results = []
    result_dict = ibm_db.fetch_assoc(stmt)
    results.append(result_dict)
    while result_dict is not False:
        result_dict = ibm_db.fetch_assoc(stmt)
        results.append(result_dict)
    results.pop()
    return results


def getTotal(table):
    sql = "SELECT SUM(AMOUNT) FROM " + table + " where USER_ID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    result = ibm_db.fetch_assoc(stmt)
    print(result)
    return result["1"]


@app.route("/logtoday")
def logtoday():
    # if isLogged():
        sql = "SELECT AMOUNT,CATEGORY,NEED FROM TRANSACTIONS WHERE USER_ID=? AND DATEADDED=CURRENT_DATE"
        stmt = ibm_db.prepare(conn, sql)
        expenseData = fetchall(stmt)
        print(expenseData)
        expenseTotal = getTotal("TRANSACTIONS")
        sql = "SELECT AMOUNT FROM income WHERE ID=? AND DATEADDED=CURRENT_DATE"
        stmt = ibm_db.prepare(conn, sql)
        incomeData = fetchall(stmt)
        print(incomeData)
        return render_template(
            "logtoday.html",
            title="Today's Log",
            expenseData=expenseData,
            incomeData=incomeData,
            expenseTotal=expenseTotal,
        )
    # else:
    #     flash("Login First")
    #     return redirect("/login")


@app.route("/addExpense/", methods=["POST", "GET"])
def addExpense():
    msg = ""
    if request.method == "POST":
        amount = request.form["Amount"]
        need = request.form["Need/Want"]
        category = request.form["category"]
        sql = "INSERT INTO TRANSACTIONS(USER_ID,AMOUNT,NEED,CATEGORY,DATEADDED) VALUES(?,?,?,?,CURRENT_DATE)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session["id"])
        ibm_db.bind_param(stmt, 2, amount)
        ibm_db.bind_param(stmt, 3, need)
        ibm_db.bind_param(stmt, 4, category)
        if ibm_db.execute(stmt):
            msg = "Successfully Added Expense!!!!"
        else:
            msg = "Expense not added"

    flash(msg)
    return redirect(url_for("logtoday"))
    # return redirect(url_for('logtoday'))


@app.route("/addIncome/", methods=["POST", "GET"])
def addIncome():
    msg = ""
    if request.method == "POST":
        amount = request.form["AmountIncome"]
        sql = "INSERT INTO INCOME(ID,AMOUNT,DATEADDED) VALUES(?,?,CURRENT_DATE)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session["id"])
        ibm_db.bind_param(stmt, 2, amount)
        if ibm_db.execute(stmt):
            msg = "Successfully Added Income!!!!"
        else:
            msg = "Income not added"

    flash(msg)
    return redirect(url_for("logtoday"))


# @app.route("/Edit")
###Visualization functions


@app.route("/reports")
def reports():
    return render_template("reports.html", title="Reports")


@app.route("/needVwant/")
def needVwant():
    sql = "SELECT Sum(amount) AS amount, need FROM transactions WHERE DAYS(CURRENT_DATE)-DAYS(DATEADDED)<29 AND  user_id = ? GROUP BY NEED ORDER BY need"
    stmt = ibm_db.prepare(conn, sql)
    transactions = fetchall(stmt)
    values = []
    labels = []
    print(transactions)
    for transaction in transactions:
        values.append(transaction["AMOUNT"])
        labels.append(transaction["NEED"])
    fig = plt.figure(figsize=(10, 7))
    plt.pie(values)
    plt.title("Need v Want")
    plt.legend(["WANT", "NEED"])
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype="image/png")


@app.route("/categoriesChart/")
def categoriesChart():
    sql = "SELECT Sum(amount) AS amount, category FROM transactions WHERE DAYS(CURRENT_DATE)-DAYS(DATEADDED)<29 AND  user_id = ? GROUP BY category ORDER BY category"
    stmt = ibm_db.prepare(conn, sql)
    transactions = fetchall(stmt)
    values = []
    labels = []
    print(transactions)
    for transaction in transactions:
        values.append(transaction["AMOUNT"])
        labels.append(transaction["CATEGORY"])
    fig = plt.figure(figsize=(10, 7))
    plt.pie(values, labels=labels)
    plt.title("Categories")
    plt.legend()
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype="image/png")


##edit the legend... all visualizations workkkkkk!!!!!!!
@app.route("/dailyLineChart/")
def dailyLineChart():
    sql = "SELECT Sum(amount) AS amount, DAY(dateadded) as dateadded FROM transactions WHERE DAYS(CURRENT_DATE)-DAYS(DATEADDED)<29 AND  user_id = ? GROUP BY dateadded ORDER BY dateadded"
    stmt = ibm_db.prepare(conn, sql)
    transactions = fetchall(stmt)
    x = []
    y = []
    print(transactions)
    for transaction in transactions:
        y.append(transaction["AMOUNT"])
        x.append(transaction["DATEADDED"])
        ##get budget
    sql = "SELECT MAXBUDGET FROM budgets WHERE id = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    budget = ibm_db.fetch_assoc(stmt)
    print(budget)
    fig = plt.figure(figsize=(10, 7))
    plt.scatter(x, y)
    plt.plot(x, y, "-")
    if budget:
        plt.axhline(y=budget["MAXBUDGET"], color="r", linestyle="-")
    plt.xlabel("Day")
    plt.ylabel("Transaction")
    plt.title("Daily")
    plt.legend()
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype="image/png")


# if __name__ == "__main__":
#     app.debug = True
#     app.run()

if __name__=="__main__":
    port = int(os.environ.get('PORT',5000))
    app.run(port=port,host="0.0.0.0")
