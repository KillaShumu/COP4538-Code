from flask import Flask, render_template, request, redirect, url_for
import os
import time

N = 1000000 #we will change this value later in the project

start_time = time.time()

#core logic
for i in range(N):
    pass #a simple operation

end_time = time.time()
elasped_time = end_time - start_time
print(f"Loop of {N} iterations took {elasped_time} seconds.")


app = Flask(__name__)

app.config['FLASK_TITLE'] = ""

# --- IN-MEMORY DATA STRUCTURES (Students will modify this area) ---
# Phase 1: A simple Python List to store contacts
contacts = [] 

# --- ROUTES ---

@app.route('/')
def index():
    #change the FLASK HTML title to my name 
    app.config['FLASK_TITLE'] = "Mohammed Haider "

    """
    Displays the main page.
    Eventually, students will pass their Linked List or Tree data here.
    """
    return render_template('index.html', 
                         contacts=contacts, 
                         title=app.config['FLASK_TITLE'])

@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact.
    Students will update this to insert into their Data Structure.
    """
    name = request.form.get('name')
    email = request.form.get('email')
    
    # Phase 1 Logic: Append to list
    contacts.append({'name': name, 'email': email})
    return redirect(url_for('index'))

# --- DATABASE CONNECTIVITY (For later phases) ---
# Placeholders for students to fill in during Sessions 5 and 27
def get_postgres_connection():
    pass

def get_mssql_connection():
    pass

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
