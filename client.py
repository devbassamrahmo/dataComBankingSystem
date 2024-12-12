import socket

HOST = "127.0.0.1"  
PORT = 8080       

RECEIVE_TIMEOUT = 3000  

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.settimeout(RECEIVE_TIMEOUT)  
        print("Connected to the server.")

        authenticated = False

        while True:
            if not authenticated:
                print("\nOptions:")
                print("1. Login")
                print("2. Signup")
                print("3. Exit")
                option = input("Choose an option: ").strip()

                if option == "1":
                    iban = input("Enter IBAN: ").strip()
                    password = input("Enter password: ").strip()
                    client.send(f"Login {iban} {password}".encode()) # "Login (Iban) (password)"

                    try:
                        response = client.recv(1024).decode()
                        print(response)
                        if "logged in" in response:
                            authenticated = True
                    except socket.timeout:
                        print("Timeout: No response from the server.")

                elif option == "2":
                    iban = input("Enter a new IBAN: ").strip()
                    password = input("Enter a new password: ").strip()
                    client.send(f"Signup {iban} {password}".encode())

                    try:
                        response = client.recv(1024).decode()
                        print(response)
                    except socket.timeout:
                        print("Timeout: No response from the server.")

                elif option == "3":
                    client.send("Exit".encode())
                    try:
                        response = client.recv(1024).decode()
                        print(response)
                    except socket.timeout:
                        print("Timeout: No response from the server.")
                    break

                else:
                    print("Invalid option. Please try again.")

            else:
                # Authenticated user options menu
                print("\nOptions:")
                print("1. Add Money")
                print("2. Remove Money")
                print("3. View Balance")
                print("4. Logout")
                option = input("Choose an option: ").strip()

                if option == "1":
                    try:
                        amount = float(input("Enter amount to add: ").strip())
                        client.send(f"AddMoney {amount}".encode())

                        response = client.recv(1024).decode()
                        print(response)
                    except ValueError:
                        print("Invalid amount. Please enter a valid number.")

                elif option == "2":
                    try:
                        amount = float(input("Enter amount to remove: ").strip())
                        client.send(f"RemoveMoney {amount}".encode())

                        response = client.recv(1024).decode()
                        print(response)
                    except ValueError:
                        print("Invalid amount. Please enter a valid number.")

                elif option == "3":
                    client.send("Balance".encode())

                    response = client.recv(1024).decode()
                    print(response)

                elif option == "4":
                    client.send("Logout".encode())
                    response = client.recv(1024).decode()
                    print(response)
                    authenticated = False

                else:
                    print("Invalid option. Please try again.")

        client.close()

    except socket.timeout:
        print("Connection timed out. Unable to connect to the server.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Client closed.")

if __name__ == "__main__":
    main()
