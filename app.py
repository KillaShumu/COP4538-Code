from flask import Flask, render_template, request, redirect, url_for
import os
import time
import heapq

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


class Contact:
    """Represents a contact with name, category path, and priority."""
    def __init__(self, name, category_path=None, priority=0):
        self.name = name
        self.category_path = category_path or []  # list like ['Work', 'Engineering', 'Team A']
        self.priority = priority  # higher number = higher priority for VIP

    def get_category_string(self):
        return ' -> '.join(self.category_path) if self.category_path else 'Uncategorized'

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Contact({self.name}, {self.category_path}, {self.priority})"


class TreeNode:
    """Node in the category tree."""
    def __init__(self, name):
        self.name = name
        self.children = {}  # dict of child_name -> TreeNode
        self.contacts = []  # list of Contact objects at this level

    def add_contact(self, contact):
        """Add a contact to this node."""
        self.contacts.append(contact)

    def get_child(self, name):
        """Get or create child node."""
        if name not in self.children:
            self.children[name] = TreeNode(name)
        return self.children[name]

    def get_all_contacts(self):
        """Recursively get all contacts in this subtree."""
        all_contacts = self.contacts[:]
        for child in self.children.values():
            all_contacts.extend(child.get_all_contacts())
        return all_contacts


class CategoryTree:
    """Tree structure for organizing contacts by categories."""
    def __init__(self):
        self.root = TreeNode('Root')

    def add_contact(self, contact):
        """Add a contact to the tree based on its category path."""
        current = self.root
        for category in contact.category_path:
            current = current.get_child(category)
        current.add_contact(contact)

    def get_contacts_by_category(self, category_path):
        """Get contacts under a specific category path."""
        current = self.root
        try:
            for category in category_path:
                current = current.children[category]
            return current.get_all_contacts()
        except KeyError:
            return []

    def get_all_contacts(self):
        """Get all contacts in the tree."""
        return self.root.get_all_contacts()

    def remove_contact(self, contact):
        """Remove a contact from the tree."""
        current = self.root
        for category in contact.category_path:
            if category not in current.children:
                return False
            current = current.children[category]
        if contact in current.contacts:
            current.contacts.remove(contact)
            return True
        return False


class BSTNode:
    """Node in Binary Search Tree."""
    def __init__(self, key, value):
        self.key = key  # category path as tuple
        self.value = value  # list of contacts or TreeNode
        self.left = None
        self.right = None


class CategoryBST:
    """Binary Search Tree for fast category retrieval."""
    def __init__(self):
        self.root = None

    def _insert(self, node, key, value):
        if node is None:
            return BSTNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Update existing
            node.value = value
        return node

    def insert(self, key, value):
        """Insert or update a category."""
        self.root = self._insert(self.root, key, value)

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def search(self, key):
        """Search for a category."""
        node = self._search(self.root, key)
        return node.value if node else None

    def get_all_categories(self):
        """Get all category keys in sorted order."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.key)
            self._inorder(node.right, result)


class PriorityQueue:
    """Priority Queue using heapq for VIP contacts."""
    def __init__(self):
        self.heap = []  # list of (-priority, contact) for max-heap
        self.entry_count = 0  # to handle duplicate priorities

    def push(self, contact):
        """Add contact to priority queue."""
        heapq.heappush(self.heap, (-contact.priority, self.entry_count, contact))
        self.entry_count += 1

    def pop(self):
        """Remove and return highest priority contact."""
        if self.heap:
            return heapq.heappop(self.heap)[2]
        return None

    def peek(self):
        """Return highest priority contact without removing."""
        if self.heap:
            return self.heap[0][2]
        return None

    def is_empty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)

    def get_top_contacts(self, n=5):
        """Get top n contacts without removing them."""
        # Create a sorted list from heap
        sorted_contacts = sorted(self.heap, key=lambda x: x[0])  # sort by priority (already negative)
        return [contact for _, _, contact in sorted_contacts[:n]]

    def remove(self, contact):
        """Remove a contact from the priority queue."""
        self.heap = [item for item in self.heap if item[2] != contact]
        heapq.heapify(self.heap)

    def remove(self, contact):
        """Remove a contact from the priority queue."""
        self.heap = [item for item in self.heap if item[2] != contact]
        heapq.heapify(self.heap)

    def remove(self, contact):
        """Remove a contact from the priority queue."""
        self.heap = [item for item in self.heap if item[2] != contact]
        heapq.heapify(self.heap)


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
    """A hash table (dictionary-based) for O(1) contact lookup by name.

    NOTE: this structure remains in the codebase for demonstration purposes
    but the search endpoint has been updated to rely on quick sort and a
    simple linear scan instead of O(1) hashing.  It is no longer used by
    the search route itself.
    """
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
    def __init__(self, operation_type, contact):
        """
        operation_type: 'add' or 'delete'
        contact: Contact object
        """
        self.operation_type = operation_type
        self.contact = contact
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


def quick_sort(arr, key=lambda x: x):
    """Return a new list that is a quick-sorted version of *arr*.

    The `key` function is applied to each element for comparisons (similar to
    the built-in ``sorted``).  This implementation is recursive and uses the
    pivot-at-middle strategy. It produces a new list, leaving *arr* unmodified.
    """
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[len(arr) // 2]
    pivot_key = key(pivot)
    left = [x for x in arr if key(x) < pivot_key]
    middle = [x for x in arr if key(x) == pivot_key]
    right = [x for x in arr if key(x) > pivot_key]
    return quick_sort(left, key) + middle + quick_sort(right, key)


def find_contact_by_id(contact_id, sorted_contacts):
    """Perform binary search to find a contact by ID (index) in a sorted list.
    
    Args:
        contact_id: The contact name to search for (performs case-insensitive comparison).
        sorted_contacts: A sorted list of contact names.
    
    Returns:
        A tuple (index, contact_name) if found, otherwise None.
        The index refers to the position in the sorted list.
    
    Time Complexity: O(log n) where n is the number of contacts.
    Space Complexity: O(1)
    """
    if not sorted_contacts:
        return None
    
    left = 0
    right = len(sorted_contacts) - 1
    contact_id_lower = contact_id.strip().lower()
    
    while left <= right:
        mid = (left + right) // 2
        mid_contact = sorted_contacts[mid]
        mid_contact_lower = mid_contact.lower()
        
        # Compare case-insensitively
        if mid_contact_lower == contact_id_lower:
            return (mid, mid_contact)
        elif mid_contact_lower < contact_id_lower:
            left = mid + 1
        else:
            right = mid - 1
    
    # Contact not found
    return None


# Initialize data structures
category_tree = CategoryTree()
category_bst = CategoryBST()
vip_queue = PriorityQueue()

# Sample contacts with categories and priorities
sample_contacts = [
    Contact("Alice", ["Work", "Engineering"], 3),  # VIP
    Contact("Bob", ["Work", "Sales"], 0),
    Contact("Charlie", ["Personal", "Friends"], 0),
    Contact("David", ["Work", "Engineering", "Team A"], 5),  # High VIP
    Contact("Eve", ["Personal", "Family"], 0),
    Contact("Frank", ["Work", "HR"], 2),  # VIP
]

# Add contacts to tree and BST
for contact in sample_contacts:
    category_tree.add_contact(contact)
    category_bst.insert(tuple(contact.category_path), contact.category_path)
    if contact.priority > 0:
        vip_queue.push(contact)

# For backward compatibility, create a list of all contacts
contacts = category_tree.get_all_contacts()

# Undo/Redo stacks and queues
undo_stack = Stack()
redo_queue = Queue()


@app.route('/')
def index():
    app.config['FLASK_TITLE'] = "Mohammed Haider "

    # Get VIP contacts (top 5)
    vip_contacts = vip_queue.get_top_contacts(5)

    # Get tree display data
    tree_data = get_tree_display_data(category_tree.root, contacts_list=contacts)

    return render_template('index.html',
                         contacts=contacts,
                         tree_data=tree_data,
                         vip_contacts=vip_contacts,
                         title=app.config['FLASK_TITLE'],
                         undo_available=not undo_stack.is_empty(),
                         redo_available=not redo_queue.is_empty())

@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact.
    Records the operation in the undo stack and adds to tree, BST, and VIP queue.
    Clears the redo queue when a new operation is performed.
    """
    global contacts

    name = request.form.get('name')
    category_str = request.form.get('category', '')
    priority = int(request.form.get('priority', 0))

    if name:
        # Parse category path
        category_path = [cat.strip() for cat in category_str.split('->')] if category_str else []

        # Create contact
        contact = Contact(name, category_path, priority)

        # Record the operation for undo
        operation = ContactOperation('add', contact)
        undo_stack.push(operation)

        # Clear redo queue when new operation is performed
        redo_queue.clear()

        # Add to tree
        category_tree.add_contact(contact)

        # Add to BST
        category_bst.insert(tuple(category_path), category_path)

        # Add to VIP queue if priority > 0
        if priority > 0:
            vip_queue.push(contact)

        # Update contacts list
        contacts = category_tree.get_all_contacts()

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
    Search for contacts by name.

    Performs a linear scan over contacts to find matches.
    Matches are treated case-insensitively.
    """
    raw_query = request.args.get('q', '')
    query = raw_query.strip().lower()

    search_results = []
    if query:
        # perform linear scan over contacts
        for i, contact in enumerate(contacts):
            if query in contact.name.lower():
                search_results.append((i, contact))
        # sort the results by contact name using quick sort
        if search_results:
            search_results = quick_sort(search_results, key=lambda pair: pair[1].name.lower())

    return render_template('search_results.html',
                         query=raw_query,
                         results=search_results,
                         result_count=len(search_results),
                         undo_available=not undo_stack.is_empty(),
                         redo_available=not redo_queue.is_empty())


@app.route('/delete/<int:idx>', methods=['POST'])
def delete_contact(idx):
    """
    Remove a contact from the tree by index and record it for undo.
    Records the deletion in the undo stack and removes from tree, BST, and VIP queue.
    """
    global contacts

    try:
        contact = contacts[idx]

        # Record the operation for undo
        operation = ContactOperation('delete', contact)
        undo_stack.push(operation)

        # Clear redo queue when new operation is performed
        redo_queue.clear()

        # Remove from tree
        category_tree.remove_contact(contact)

        # Remove from BST (if needed)
        # Note: BST removal is complex, we'll skip for now

        # Remove from VIP queue if present
        if contact.priority > 0:
            vip_queue.remove(contact)

        # Update contacts list
        contacts = category_tree.get_all_contacts()
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
    global contacts

    # Prefer form 'next' (from POST), then querystring 'next', otherwise go home
    next_url = request.form.get('next') or request.args.get('next') or url_for('index')

    if undo_stack.is_empty():
        return redirect(next_url)

    operation = undo_stack.pop()

    if operation.operation_type == 'add':
        # Undo an add: remove the contact
        try:
            category_tree.remove_contact(operation.contact)
            if operation.contact.priority > 0:
                vip_queue.remove(operation.contact)
            contacts = category_tree.get_all_contacts()
        except Exception:
            pass
    elif operation.operation_type == 'delete':
        # Undo a delete: restore the contact
        try:
            category_tree.add_contact(operation.contact)
            category_bst.insert(tuple(operation.contact.category_path), operation.contact.category_path)
            if operation.contact.priority > 0:
                vip_queue.push(operation.contact)
            contacts = category_tree.get_all_contacts()
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
    global contacts

    # Prefer form 'next' (from POST), then querystring 'next', otherwise go home
    next_url = request.form.get('next') or request.args.get('next') or url_for('index')

    if redo_queue.is_empty():
        return redirect(next_url)

    operation = redo_queue.dequeue()

    if operation.operation_type == 'add':
        # Redo an add: restore the contact
        try:
            category_tree.add_contact(operation.contact)
            category_bst.insert(tuple(operation.contact.category_path), operation.contact.category_path)
            if operation.contact.priority > 0:
                vip_queue.push(operation.contact)
            contacts = category_tree.get_all_contacts()
        except Exception:
            pass
    elif operation.operation_type == 'delete':
        # Redo a delete: remove the contact again
        try:
            category_tree.remove_contact(operation.contact)
            if operation.contact.priority > 0:
                vip_queue.remove(operation.contact)
            contacts = category_tree.get_all_contacts()
        except Exception:
            pass

    # Move back to undo stack
    undo_stack.push(operation)

    return redirect(next_url)


def get_tree_display_data(tree_node, path=[], contacts_list=None):
    """Get display data for tree visualization."""
    if contacts_list is None:
        contacts_list = []

    data = []
    current_path = path + [tree_node.name]

    # Add contacts at this level
    for contact in tree_node.contacts:
        contact_index = contacts_list.index(contact) if contact in contacts_list else -1
        data.append({
            'path': current_path[1:],  # Skip 'Root'
            'contact': contact,
            'level': len(current_path) - 1,
            'index': contact_index
        })

    # Recursively add children
    for child_name, child_node in sorted(tree_node.children.items()):
        data.extend(get_tree_display_data(child_node, current_path, contacts_list))

    return data

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
