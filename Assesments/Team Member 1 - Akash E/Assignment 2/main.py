from flask import Flask, redirect,render_template, request, url_for
app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("new.html")

# @app.route("/signin")
# def render_signin():
#     return render_template("new.html")

@app.route("/login")
def render_signin():
    return render_template("new.html")

# @app.route('/sg')
# def signin():
#     return redirect(url_for('home'))


@app.route("/login",methods=['POST'])
def send_data():
    username = request.form['usr']
    email = request.form['mailId']
    password = request.form['password']
    if(email == "nitish@123.com" and username=="nitish" and password=="123"):
        return render_template("home.html")
    else:
        print("error")


if __name__=='__main__':
    app.run()


