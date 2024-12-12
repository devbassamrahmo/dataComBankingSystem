#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <stdbool.h>

#pragma comment(lib, "ws2_32.lib")

#define BUFFER_SIZE 1024
#define RECEIVE_TIMEOUT 3000

void clean_newline(char *str) {
    str[strcspn(str, "\n")] = 0;
}

void communicate_with_server(SOCKET sock, const char *message, char *response) {
    send(sock, message, strlen(message), 0);
    memset(response, 0, BUFFER_SIZE);
    int bytes_received = recv(sock, response, BUFFER_SIZE, 0);

    if (bytes_received == SOCKET_ERROR) {
        if (WSAGetLastError() == WSAETIMEDOUT) {
            printf("Timeout: No response from the server.\n");
        } else {
            printf("Error receiving data. Error Code: %d\n", WSAGetLastError());
        }
    } else if (bytes_received == 0) {
        printf("Server disconnected.\n");
    }
}

int main() {
    WSADATA wsa;
    SOCKET client_sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    char input[BUFFER_SIZE];
    bool authenticated = false;

    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("Winsock initialization failed. Error Code: %d\n", WSAGetLastError());
        return 1;
    }

    if ((client_sock = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        printf("Socket creation failed. Error Code: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    int timeout = RECEIVE_TIMEOUT;
    if (setsockopt(client_sock, SOL_SOCKET, SO_RCVTIMEO, (const char *)&timeout, sizeof(timeout)) < 0) {
        printf("Failed to set timeout. Error Code: %d\n", WSAGetLastError());
        closesocket(client_sock);
        WSACleanup();
        return 1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    if (connect(client_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        printf("Connection failed. Error Code: %d\n", WSAGetLastError());
        closesocket(client_sock);
        WSACleanup();
        return 1;
    }

    printf("Connected to the server.\n");

    while (1) {
        if (!authenticated) {
            printf("\nOptions:\n");
            printf("1. Login\n");
            printf("2. Signup\n");
            printf("3. Exit\n");
            printf("Choose an option: ");
            fgets(input, sizeof(input), stdin); 
            clean_newline(input);

            if (strcmp(input, "1") == 0) {
                // Login
                char iban[BUFFER_SIZE], password[BUFFER_SIZE];

                printf("Enter IBAN: ");
                fgets(iban, sizeof(iban), stdin);
                clean_newline(iban);

                printf("Enter password: ");
                fgets(password, sizeof(password), stdin);
                clean_newline(password);

                snprintf(buffer, sizeof(buffer), "Login %s %s", iban, password); 
                communicate_with_server(client_sock, buffer, buffer);

                printf("%s\n", buffer);
                if (strstr(buffer, "logged in")) {
                    authenticated = true;
                }

            } else if (strcmp(input, "2") == 0) {
                // Signup
                char iban[BUFFER_SIZE], password[BUFFER_SIZE];

                printf("Enter a new IBAN: ");
                fgets(iban, sizeof(iban), stdin);
                clean_newline(iban);

                printf("Enter a new password: ");
                fgets(password, sizeof(password), stdin);
                clean_newline(password);

                snprintf(buffer, sizeof(buffer), "Signup %s %s", iban, password);
                communicate_with_server(client_sock, buffer, buffer);

                printf("%s\n", buffer);

            } else if (strcmp(input, "3") == 0) {
                // Exit
                communicate_with_server(client_sock, "Exit", buffer);
                printf("%s\n", buffer);
                break;

            } else {
                printf("Invalid option. Please try again.\n");
            }

        } else {
            printf("\nOptions:\n");
            printf("1. Add Money\n");
            printf("2. Remove Money\n");
            printf("3. View Balance\n");
            printf("4. Logout\n");
            printf("Choose an option: ");
            fgets(input, sizeof(input), stdin);
            clean_newline(input);

            if (strcmp(input, "1") == 0) {
                // Add Money
                char amount[BUFFER_SIZE];
                printf("Enter amount to add: ");
                fgets(amount, sizeof(amount), stdin);
                clean_newline(amount);

                snprintf(buffer, sizeof(buffer), "AddMoney %s", amount);
                communicate_with_server(client_sock, buffer, buffer);
                printf("%s\n", buffer);

            } else if (strcmp(input, "2") == 0) {
                // Remove Money
                char amount[BUFFER_SIZE];
                printf("Enter amount to remove: ");
                fgets(amount, sizeof(amount), stdin);
                clean_newline(amount);

                snprintf(buffer, sizeof(buffer), "RemoveMoney %s", amount);
                communicate_with_server(client_sock, buffer, buffer);
                printf("%s\n", buffer);

            } else if (strcmp(input, "3") == 0) {
                // View Balance
                communicate_with_server(client_sock, "Balance", buffer);
                printf("%s\n", buffer);

            } else if (strcmp(input, "4") == 0) {
                // Logout
                communicate_with_server(client_sock, "Logout", buffer);
                printf("%s\n", buffer);
                authenticated = false;

            } else {
                printf("Invalid option. Please try again.\n");
            }
        }
    }

    closesocket(client_sock);
    WSACleanup();
    printf("Disconnected from the server.\n");

    return 0;
}
