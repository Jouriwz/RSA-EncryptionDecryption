# Import necessary libraries
import math
import time
import sympy
from flask import Flask, render_template, request, g, session
from sympy import mod_inverse

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "topSecret"

# Route for the home page
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# Function to factorize a number into two prime factors
def factorize(n):
    # Loop through numbers up to the square root of n
    for i in range(2, int(math.sqrt(n)) + 1):
        # Check if n is divisible by i
        if n % i == 0:
            # Check if both i and n/i are prime
            if sympy.isprime(i) and sympy.isprime(n // i):
                # Check if i * (n // i) equals n
                if i * (n // i) == n:
                    return i, n // i
    return None, None

# Function to set global variables from session
def set_g_vars_from_session():
    g.n_value = session.get("n_value")
    g.q_value = session.get("q_value")
    g.p_value = session.get("p_value")
    g.e_value = session.get("e_value")
    g.d_value = session.get("d_value")
    g.taken_time = session.get("taken_time")
    g.m_value = session.get("m_value")
    g.encrypted_message = session.get("encrypted_message")
    g.encrypted_message_str = session.get("encrypted_message_str")
    g.decrypted_message = session.get("decrypted_message")

# Route to calculate p and q values
@app.route("/calculate/pq", methods=["POST"])
def calculatePQ():
    if request.method == "POST":
        if not request.form.get("n_value"):
            g.error = "Please enter a value for N."
            return render_template("index.html")
        session.clear()
        n_value = int(request.form.get("n_value"))
        start_time = time.perf_counter()
        p, q = factorize(n_value)
        if q is None:
            g.error = "Given N doesn't have distinct prime factors."
            return render_template("index.html")
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000
        session.update({
            'n_value': n_value,
            'q_value': q,
            'p_value': p,
            'taken_time': f"{elapsed_time:.6f} milliseconds"
        })
        set_g_vars_from_session()
    return render_template("index.html")

# Route to calculate e value
@app.route("/calculate/e", methods=["POST"])
def calculateE():
    if request.method == "POST":
        p = session.get("p_value")
        q = session.get("q_value")
        phi = (p - 1) * (q - 1)
        if phi <= 2:
            g.error = "Error: phi is too small for RSA. Enter a different N so that Q is more than 1."
            return render_template("index.html")
        e = sympy.randprime(2, phi)
        while sympy.gcd(e, phi) != 1:
            e = sympy.randprime(2, phi)
        session['e_value'] = e
        set_g_vars_from_session()
    return render_template("index.html")

# Route to encrypt a message
@app.route("/encrypt", methods=["POST"])
def encrypt_message():
    if request.method == "POST":
        m = request.form.get("m_value")
        p = int(request.form.get("p_value"))
        q = int(request.form.get("q_value"))
        e = int(request.form.get("e_value"))
        n = p * q
        encrypted_message = [pow(ord(char), e, n) for char in m]
        encrypted_message_str = "<" + ", ".join(map(str, encrypted_message)) + ">"
        session.update({
            'm_value': m,
            'encrypted_message': encrypted_message,
            'encrypted_message_str': encrypted_message_str
        })
        set_g_vars_from_session()
    return render_template("index.html")

# Route to calculate d value
@app.route("/calculate/d", methods=["POST"])
def calculate_d():
    if request.method == "POST":
        n = int(request.form.get("n_value"))
        e = int(request.form.get("e_value"))
        p, q = factorize(n)
        phi = (p - 1) * (q - 1)
        d = mod_inverse(e, phi)
        session['d_value'] = d
        set_g_vars_from_session()
    return render_template("index.html")

# Route to decrypt a cipher
@app.route("/decrypt", methods=["POST"])
def decrypt_cipher():
    if request.method == "POST":
        cipher_text = request.form.get("c_value")
        n = int(request.form.get("n_value"))
        d = int(request.form.get("d_value"))
        cipher_integers = list(map(int, cipher_text.strip("<>").split(", ")))
        decrypted_message = ''.join([chr(pow(c, d, n)) for c in cipher_integers])
        session['decrypted_message'] = decrypted_message
        set_g_vars_from_session()
    return render_template("index.html")

# Route to reset session
@app.route("/reset", methods=["POST"])
def reset_session():
    session.clear()
    return render_template("index.html")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
