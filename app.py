from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import os
import pandas as pd
from database import get_table_names, get_table_data
from anonymization import detect_pii_columns, anonymize_pii, generate_anonymized_file

app = Flask(__name__)
app.secret_key = 'secret-key'  # Remplace par un vrai secret en production

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Identifiants incorrects.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    tables = get_table_names()
    table_data = None
    selected_table = None

    if request.method == 'POST':
        selected_table = request.form.get('table')
        if selected_table:
            df = get_table_data(selected_table)
            pii_columns = detect_pii_columns(df)
            df = anonymize_pii(df, pii_columns)
            table_data = df.to_dict(orient='records')
            columns = df.columns.tolist()
            return render_template('dashboard.html', tables=tables, selected_table=selected_table,
                                   columns=columns, table_data=table_data)

    return render_template('dashboard.html', tables=tables, selected_table=selected_table)

@app.route('/download/<table_name>')
def download(table_name):
    df = get_table_data(table_name)
    file_path = "anonymized_data.csv"
    anonymized_file_path = generate_anonymized_file(df, file_path)
    return send_file(anonymized_file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
