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


class LinkedList:
    """A minimal singly-linked list with list-like API used for the demo.
    Supports: append, insert, pop, __len__, __iter__, __getitem__.
    This preserves the original behavior but stores contacts in a linked list.
    """
    class _Node:
        __slots__ = ("value", "next")
        def __init__(self, value, nxt=None):
            self.value = value
            self.next = nxt

    def __init__(self, iterable=None):
        self.head = None
        self._len = 0
        if iterable:
            for v in iterable:
                self.append(v)

    def append(self, value):
        node = LinkedList._Node(value)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._len += 1

    def __len__(self):
        return self._len

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next

    def _node_at(self, index):
        # support negative indices similar to list
        if index < 0:
            index += self._len
        if index < 0 or index >= self._len:
            raise IndexError('index out of range')
        cur = self.head
        for _ in range(index):
            cur = cur.next
        return cur

    def __getitem__(self, index):
        return self._node_at(index).value

    def insert(self, index, value):
        # insert at bounds: <=0 -> head, >=len -> append
        if index <= 0:
            self.head = LinkedList._Node(value, self.head)
            self._len += 1
            return
        if index >= self._len:
            self.append(value)
            return
        prev = self._node_at(index - 1)
        prev.next = LinkedList._Node(value, prev.next)
        self._len += 1

    def pop(self, index=-1):
        if self._len == 0:
            raise IndexError('pop from empty list')
        if index < 0:
            index += self._len
        if index < 0 or index >= self._len:
            raise IndexError('pop index out of range')
        if index == 0:
            val = self.head.value
            self.head = self.head.next
            self._len -= 1
            return val
        prev = self._node_at(index - 1)
        val = prev.next.value
        prev.next = prev.next.next
        self._len -= 1
        return val

    def to_list(self):
        return list(iter(self))


# replace plain Python list with a LinkedList instance so existing
# code (append/insert/pop/len/iteration) continues to work
contacts = LinkedList(["Alice", "Bob", "Charlie", "David", "Eve"])
last_deleted = None  # single-level undo: dict with keys ('name','idx','time') or None


@app.route('/')
def index():
    app.config['FLASK_TITLE'] = "Mohammed Haider "

    return render_template('index.html', 
                         contacts=contacts, 
                         title=app.config['FLASK_TITLE'],
                         last_deleted=last_deleted)

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
    
    return render_template('contacts.html', contacts=contacts, last_deleted=last_deleted)

@app.route('/search')
def search():
    """
    Search for contacts by name.
    Returns contacts that match the search query (case-insensitive).

    The results are returned as (index, contact) pairs so the UI can
    perform index-based deletion on the in-memory list.
    """
    raw_query = request.args.get('q', '')
    query = raw_query.lower()
    
    if not query:
        search_results = []
    else:
        # return (index, contact) so the template can delete the exact item
        search_results = [(i, contact) for i, contact in enumerate(contacts) if query in contact.lower()]
    
    return render_template('search_results.html', 
                         query=raw_query,
                         results=search_results,
                         result_count=len(search_results),
                         last_deleted=last_deleted)


@app.route('/delete/<int:idx>', methods=['POST'])
def delete_contact(idx):
    """
    Remove a contact from the in-memory list by index and record it for a
    single-level undo. Accepts an optional 'next' URL to redirect after deletion.
    """
    global last_deleted
    try:
        name = contacts[idx]
        # record before removing so we can restore to the same position
        last_deleted = { 'name': name, 'idx': idx, 'time': time.time() }
        contacts.pop(idx)
    except Exception:
        # invalid index or other race — clear undo state to avoid confusion
        last_deleted = None

    # Prefer form 'next' (from POST), then querystring 'next', otherwise go home
    next_url = request.form.get('next') or request.args.get('next') or url_for('index')
    return redirect(next_url)


@app.route('/undo', methods=['POST'])
def undo():
    """Restore the last deleted contact (single-level undo)."""
    global last_deleted
    # Prefer form 'next' (from POST), then querystring 'next', otherwise go home
    next_url = request.form.get('next') or request.args.get('next') or url_for('index')

    if not last_deleted:
        return redirect(next_url)

    # restore at the original index (or append if index is out of range)
    name = last_deleted.get('name')
    idx = last_deleted.get('idx', len(contacts))
    insert_at = min(max(0, idx), len(contacts))
    contacts.insert(insert_at, name)

    # clear undo buffer
    last_deleted = None
    return redirect(next_url)


def get_postgres_connection():
    pass

def get_mssql_connection():
    pass

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
