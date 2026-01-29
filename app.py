from flask import Flask, render_template, request, redirect, url_for
import os
import time

#Configure SQLAlchemy connection string based on docker-compose environment variables

POSTGRES_USER = os.getenv('POSTGRES_USER', 'student')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password123')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres_db')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'contact_db')

MSSQL_USER = os.getenv('MSSQL_USER', 'sa')
MSSQL_PASSWORD = os.getenv('MSSQL_PASSWORD', 'Password123!')
MSSQL_HOST = os.getenv('MSSQL_HOST', 'mssql_db')
MSSQL_PORT = os.getenv('MSSQL_PORT', '1433')
MSSQL_DB = os.getenv('MSSQL_DB', 'contact_db')

# Build connection strings
POSTGRES_CONNECTION_STRING = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
MSSQL_CONNECTION_STRING = f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}@{MSSQL_HOST}:{MSSQL_PORT}/{MSSQL_DB}?driver=ODBC+Driver+17+for+SQL+Server"



app = Flask(__name__)

app.config['FLASK_TITLE'] = ""


contacts = ["Alice", "Bob", "Charlie", "David", "Eve"]


@app.route('/')
def index():
    app.config['FLASK_TITLE'] = "Mohammed Haider "

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
    
    # Phase 1 Logic: Append to list
    if name:
        contacts.append(name)
    return redirect(url_for('index'))

@app.route('/contacts', methods=['GET', 'POST'])
def contacts_page():
    """
    Display all contacts in an unordered list and provide a form to add new contacts.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            contacts.append(name)
        return redirect(url_for('contacts_page'))
    
    return render_template('contacts.html', contacts=contacts)

@app.route('/search')
def search():
    """
    Search for contacts by name.
    Returns contacts that match the search query (case-insensitive).
    """
    query = request.args.get('q', '').lower()
    
    if not query:
        search_results = []
    else:
        search_results = [contact for contact in contacts if query in contact.lower()]
    
    return render_template('search_results.html', 
                         query=request.args.get('q', ''),
                         results=search_results,
                         result_count=len(search_results))


def get_postgres_connection():
    pass

def get_mssql_connection():
    pass

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
