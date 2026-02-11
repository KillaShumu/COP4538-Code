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


class Stack:
    """A stack data structure (LIFO) for storing undo operations."""
    def __init__(self):
        self.items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self.items.append(item)

    def pop(self):
        """Remove and return the top item from the stack."""
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        """View the top item without removing it."""
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        """Check if stack is empty."""
        return len(self.items) == 0

    def size(self):
        """Return the number of items in the stack."""
        return len(self.items)


class Queue:
    """A queue data structure (FIFO) for storing redo operations."""
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        """Add an item to the back of the queue."""
        self.items.append(item)

    def dequeue(self):
        """Remove and return the front item from the queue."""
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def peek(self):
        """View the front item without removing it."""
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        """Check if queue is empty."""
        return len(self.items) == 0

    def size(self):
        """Return the number of items in the queue."""
        return len(self.items)

    def clear(self):
        """Clear all items from the queue."""
        self.items = []


class ContactHashTable:
    """A hash table (dictionary-based) for O(1) contact lookup by name."""
    def __init__(self):
        self.table = {}  # key: lowercase name, value: list of positions/names

    def add(self, name):
        """Add a contact to the hash table for quick lookup."""
        key = name.lower()
        if key not in self.table:
            self.table[key] = []
        self.table[key].append(name)

    def remove(self, name):
        """Remove a contact from the hash table."""
        key = name.lower()
        if key in self.table and name in self.table[key]:
            self.table[key].remove(name)
            if not self.table[key]:
                del self.table[key]

    def search(self, query):
        """Search for contacts matching the query (case-insensitive) - O(1) lookup."""
        key = query.lower()
        if key in self.table:
            return self.table[key]
        return []

    def clear(self):
        """Clear all entries from the hash table."""
        self.table = {}


class ContactOperation:
    """Represents an operation (add or delete) for undo/redo tracking."""
    def __init__(self, operation_type, name, index):
        """
        operation_type: 'add' or 'delete'
        name: contact name
        index: position in the LinkedList
        """
        self.operation_type = operation_type
        self.name = name
        self.index = index
        self.timestamp = time.time()


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
contact_hash_table = ContactHashTable()

# Initialize hash table with existing contacts
for contact in contacts:
    contact_hash_table.add(contact)

# Undo/Redo stacks and queues
undo_stack = Stack()
redo_queue = Queue()


@app.route('/')
def index():
    app.config['FLASK_TITLE'] = "Mohammed Haider "

    return render_template('index.html', 
                         contacts=contacts, 
                         title=app.config['FLASK_TITLE'],
                         undo_available=not undo_stack.is_empty(),
                         redo_available=not redo_queue.is_empty())

@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact.
    Records the operation in the undo stack and adds to LinkedList and hash table.
    Clears the redo queue when a new operation is performed.
    """
    name = request.form.get('name')
    
    if name:
        # Record the operation for undo
        operation = ContactOperation('add', name, len(contacts))
        undo_stack.push(operation)
        
        # Clear redo queue when new operation is performed
        redo_queue.clear()
        
        # Add to LinkedList
        contacts.append(name)
        
        # Add to hash table for O(1) lookup
        contact_hash_table.add(name)
    
    return redirect(url_for('index'))


@app.route('/contacts', methods=['GET', 'POST'])
def contacts_page():
    """
    Display all contacts in an unordered list and provide a form to add new contacts.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            operation = ContactOperation('add', name, len(contacts))
            undo_stack.push(operation)
            redo_queue.clear()
            contacts.append(name)
            contact_hash_table.add(name)
        return redirect(url_for('contacts_page'))
    
    return render_template('contacts.html', contacts=contacts,
                         undo_available=not undo_stack.is_empty(),
                         redo_available=not redo_queue.is_empty())

@app.route('/search')
def search():
    """
    Search for contacts by name using hash table for O(1) lookup.
    Returns contacts that match the search query (case-insensitive).

    The results are returned as (index, contact) pairs so the UI can
    perform index-based deletion on the in-memory list.
    
    Hash table provides O(1) average-case lookup time instead of O(n) linear search.
    """
    raw_query = request.args.get('q', '')
    query = raw_query.lower()
    
    search_results = []
    if query:
        # Use hash table for O(1) lookup
        matching_contacts = contact_hash_table.search(raw_query)
        # Convert to (index, contact) pairs by finding indices in the LinkedList
        for contact in matching_contacts:
            for i, c in enumerate(contacts):
                if c == contact:
                    search_results.append((i, c))
                    break
    
    return render_template('search_results.html', 
                         query=raw_query,
                         results=search_results,
                         result_count=len(search_results),
                         undo_available=not undo_stack.is_empty(),
                         redo_available=not redo_queue.is_empty())


@app.route('/delete/<int:idx>', methods=['POST'])
def delete_contact(idx):
    """
    Remove a contact from the in-memory list by index and record it for undo.
    Records the deletion in the undo stack and removes from hash table.
    """
    try:
        name = contacts[idx]
        
        # Record the operation for undo
        operation = ContactOperation('delete', name, idx)
        undo_stack.push(operation)
        
        # Clear redo queue when new operation is performed
        redo_queue.clear()
        
        # Remove from LinkedList
        contacts.pop(idx)
        
        # Remove from hash table
        contact_hash_table.remove(name)
    except Exception:
        pass

    next_url = request.form.get('next') or request.args.get('next') or url_for('index')
    return redirect(next_url)


@app.route('/undo', methods=['POST'])
def undo():
    """
    Undo the last operation (add or delete) using the undo stack.
    Moves the undone operation to the redo queue for potential redo.
    """
    # Prefer form 'next' (from POST), then querystring 'next', otherwise go home
    next_url = request.form.get('next') or request.args.get('next') or url_for('index')

    if undo_stack.is_empty():
        return redirect(next_url)

    operation = undo_stack.pop()
    
    if operation.operation_type == 'add':
        # Undo an add: remove the contact
        try:
            contacts.pop(operation.index)
            contact_hash_table.remove(operation.name)
        except Exception:
            pass
    elif operation.operation_type == 'delete':
        # Undo a delete: restore the contact
        try:
            insert_at = min(max(0, operation.index), len(contacts))
            contacts.insert(insert_at, operation.name)
            contact_hash_table.add(operation.name)
        except Exception:
            pass
    
    # Move to redo queue for potential redo
    redo_queue.enqueue(operation)
    
    return redirect(next_url)


@app.route('/redo', methods=['POST'])
def redo():
    """
    Redo the last undone operation (add or delete) using the redo queue.
    Moves the redone operation back to the undo stack.
    """
    # Prefer form 'next' (from POST), then querystring 'next', otherwise go home
    next_url = request.form.get('next') or request.args.get('next') or url_for('index')

    if redo_queue.is_empty():
        return redirect(next_url)

    operation = redo_queue.dequeue()
    
    if operation.operation_type == 'add':
        # Redo an add: restore the contact
        try:
            insert_at = min(max(0, operation.index), len(contacts))
            contacts.insert(insert_at, operation.name)
            contact_hash_table.add(operation.name)
        except Exception:
            pass
    elif operation.operation_type == 'delete':
        # Redo a delete: remove the contact again
        try:
            contacts.pop(operation.index)
            contact_hash_table.remove(operation.name)
        except Exception:
            pass
    
    # Move back to undo stack
    undo_stack.push(operation)
    
    return redirect(next_url)


def get_postgres_connection():
    pass

def get_mssql_connection():
    pass

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
