import socket
import threading
from hashlib import sha256
import sqlite3

def create_db():
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                    iban TEXT PRIMARY KEY, 
                    password TEXT,
                    balance REAL DEFAULT 0)''')  # Added balance field
    conn.commit()
    conn.close()

def load_accounts_data():
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute("SELECT iban, password, balance FROM accounts")
    accounts = c.fetchall()
    conn.close()
    return accounts

def get_account_balance(iban):
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM accounts WHERE iban=?", (iban,))
    balance = c.fetchone()
    conn.close()
    return balance[0] if balance else None

def update_account_balance(iban, new_balance):
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute("UPDATE accounts SET balance=? WHERE iban=?", (new_balance, iban))
    conn.commit()
    conn.close()

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def add_account(iban, password):
    # First, check if the IBAN already exists
    conn = sqlite3.connect('bank_accounts.db')
    c = conn.cursor()
    c.execute("SELECT iban FROM accounts WHERE iban=?", (iban,))
    existing_account = c.fetchone()
    if existing_account:
        conn.close()
        return False
    
    # If the IBAN doesn't exist, add the new account
    hashed_password = hash_password(password)
    c.execute("INSERT INTO accounts (iban, password, balance) VALUES (?, ?, ?)", (iban, hashed_password, 0))
    conn.commit()
    conn.close()
    return True

def handle_client(client_socket):    
    authenticated = False
    current_iban = None
    while True:
        data = client_socket.recv(1024).decode().strip()
        if not data:
            break
        command, *args = data.split() # "Login B002 123456"

        if command == "Login" and len(args) == 2:
            iban, password = args
            hashed_password = hash_password(password)

            # Verify credentials
            accounts = load_accounts_data()
            found = False
            for account in accounts:
                if account[0] == iban and account[1] == hashed_password:
                    client_socket.send("You logged in!\n".encode())
                    authenticated = True
                    current_iban = iban
                    found = True
                    break

            if not found:
                client_socket.send("IBAN or password not match.\n".encode())

        elif command == "Signup" and len(args) == 2:
            iban, password = args
            if add_account(iban, password):
                client_socket.send("Account created successfully!\n".encode())
            else:
                client_socket.send("IBAN already exists. Please choose a different IBAN.\n".encode())

        elif command == "Logout":
            if authenticated:
                client_socket.send("You have logged out.\n".encode())
                authenticated = False
                current_iban = None
            else:
                client_socket.send("You are not logged in.\n".encode())

        elif authenticated:
            if command == "Balance":
                balance = get_account_balance(current_iban)
                client_socket.send(f"Your balance is: {balance}\n".encode())

            elif command == "AddMoney" and len(args) == 1: #"AddMoney 1000"
                try:
                    amount = float(args[0])
                    balance = get_account_balance(current_iban)
                    new_balance = balance + amount
                    update_account_balance(current_iban, new_balance)
                    client_socket.send(f"Added {amount} to your account. New balance: {new_balance}\n".encode())
                except ValueError:
                    client_socket.send("Invalid amount. Please enter a valid number.\n".encode())

            elif command == "RemoveMoney" and len(args) == 1:
                try:
                    amount = float(args[0])
                    balance = get_account_balance(current_iban)
                    if amount > balance:
                        client_socket.send("Insufficient funds.\n".encode())
                    else:
                        new_balance = balance - amount
                        update_account_balance(current_iban, new_balance)
                        client_socket.send(f"Removed {amount} from your account. New balance: {new_balance}\n".encode())
                except ValueError:
                    client_socket.send("Invalid amount. Please enter a valid number.\n".encode())

            else:
                client_socket.send("Invalid command. Try again.\n".encode())

        elif command == "Exit":
            client_socket.send("Goodbye!\n".encode())
            break

        else:
            client_socket.send("Invalid command. Try again.\n".encode())

    client_socket.close()

def start_server():
    create_db()  
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 8080))  
    server.listen(5)
    print("Server is running and waiting for clients...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection established with {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
