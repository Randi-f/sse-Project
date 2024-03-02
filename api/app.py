from flask import Flask, render_template, jsonify, request
import psycopg as db
import math

app = Flask(__name__)
app.secret_key = "your_unique_and_secret_key"

def get_db_connection():
    # config = configparser.ConfigParser()
    # config.read("dbtool.ini")
    server_params = {
        "dbname": "sf23",
        "host": "db.doc.ic.ac.uk",
        "port": "5432",
        "user": "sf23",
        "password": "3048=N35q4nEsm",
        "client_encoding": "utf-8",
    }
    return db.connect(**server_params)

# home page for the app
@app.route("/")
def hello_world():
    return render_template("index.html")


# login page
@app.route("/login")
def login():
    return render_template("login.html")


# login submit
@app.route("/loginsubmit", methods=["POST"])
def login_submit():
    user_id = request.form.get("user_id")
    password = request.form.get("password")
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM notes_user WHERE user_id = %s AND password = %s"
    cursor.execute(query, (user_id, password))
    user = cursor.fetchone()
    conn.close()
    if user is not None:
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "User not found"}), 401


# register page
@app.route("/register")
def register():
    return render_template("register.html")


# register submit
@app.route("/registersubmit", methods=["POST"])
def register_submit():
    data = request.json
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    full_name = first_name + " " + last_name
    DoB = data.get('DoB')
    email = data.get('email')
    password = data.get('password')

    # generate unique user_id
    sqlcommand = (
        "SELECT COUNT(*) AS row_count FROM my_user WHERE name = '"
        + first_name
        + " "
        + last_name
        + "';"
    )
    try:
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute(sqlcommand)
        ret = curs.fetchone()
    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error
    finally:
        if "curs" in locals():
            curs.close()
        if "conn" in locals():
            conn.close()


    user_id = (first_name + last_name).lower() + (str)(ret[0] + 1)

    sqlcommand = """
        INSERT INTO notes_user (user_id, name, email, dob, password) 
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        user_id,
        full_name,
        email,
        DoB,
        password
    )

    try:
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute(sqlcommand, values)
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if "curs" in locals():
            curs.close()
        if "conn" in locals():
            conn.close()

    return jsonify({'success': True, 'message': 'Registration successful'})    


if __name__ == "__main__":
    app.run()
