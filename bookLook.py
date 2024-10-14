# Project: Library Database
# Author: Jack Fraley
# Date: 10/14/24
# Description: This program is capable of handling a library database. It stores user login
# information and is able to handle logins. It is also able to store book information and 
# gives users the ability to view and checkout books if available. It also has root commands
# such as user deletions, book additions and deletions. All data is stored in a single file using
# sqLite to manage the data securely. 

import sqlite3
import datetime
import sys

con = sqlite3.connect("books.db")
cur = con.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS books (
            bookId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            subject TEXT,
            author TEXT,
            details TEXT,
            available INT 
        )
    ''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS userIds (
                userId INTEGER PRIMARY KEY AUTOINCREMENT,
                firstName TEXT,
                lastName TEXT,
                userName TEXT UNIQUE,
                password TEXT,
                access INTEGER)
                ''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS checkouts (
            checkoutId INTEGER PRIMARY KEY,
            userId INTEGER,
            bookId INTEGER,
            checkoutDate TEXT,
            dueDate TEXT,
            FOREIGN KEY (userId) REFERENCES userIds(userId),
            FOREIGN KEY (bookId) REFERENCES books(bookId))''')
con.commit()

def userLogin():
    print("Please Login:\n1. Sign In\n2. Sign Up\n3. Quit")
    option = input("\nSelection: ")
    if option == "1":
        sign_in()
        return
    elif option == "2":
        sign_up()
        return
    elif option == "3":
        sys.exit()
    else:
        print("Invalid Input")

def sign_in():
    print("\nPlease Enter Login Info:")
    userName = input("\nUserName: ")
    password = input("\nPassword: ")

    cur.execute('''SELECT userId, firstName, lastName, userName, password, access FROM userIds 
                WHERE userName = ? COLLATE NOCASE
                AND password = ? 
                ''', (userName, password))
    
    login = cur.fetchone()

    if not login:
        print("\nIncorrect Login Info.\n Would you like to create an account?\n1. Yes\n2. No")
        while True:
            option = input("Selection: ")
            if option == "1":
                sign_up()
                return
            elif option == "2":
                sign_in()
                return
            else:
                print("Invalid Input")

    else:
        userId, firstName, lastName, userName, password, access = login
        print(f"Successfully Logged {firstName} ({userId}) In")
        getValidInput(login)

    return

def userEdit():
    print("Search Users by Name:")
    searchTerm = input("Search: ")
    search = f"%{searchTerm}%"
    cur.execute('''SELECT firstName, lastName, userName, password, access FROM userIds
                WHERE firstName LIKE ? COLLATE NOCASE
                OR lastName LIKE ? COLLATE NOCASE
                OR userName LIKE ? COLLATE NOCASE
                ''', (search, search, search))
    results = cur.fetchall()

    if not results:
        print("No users found.")

    else:
        print("Users found:")
        for idx, (firstName, lastName, userName, password, access) in enumerate(results, start=1):
            print(f"{idx}. First: {firstName}, Last: {lastName}, User: {userName}, Access: {access}")

        while True:
            try:
                selection = int(input(f"\nEnter Desired User Number (1-{len(results)}): ")) -1
                if 0 <= selection < len(results):
                    break
                else:
                    print("Invalid Input")
            except ValueError:
                print("Invalid Input")
            
        selectedUser = results[selection][0]

        cur.execute("SELECT userId, firstName, lastName, userName, access FROM userIds WHERE firstName = ? COLLATE NOCASE", (selectedUser,))
        userInfo = cur.fetchone()

        if userInfo:
            userId, firstName, lastName, userName, access = userInfo
            cur.execute("SELECT bookId, checkoutDate, dueDate FROM checkouts WHERE userId = ?", (userId,))
            checkedOutBooks = cur.fetchone()

            print(f"\nDetails for {lastName}, {firstName}:")
            print(f"\nUserName: {userName}")
            print(f"Access: {access}")

            if checkedOutBooks:
                bookId, checkoutDate, dueDate = checkedOutBooks
                cur.execute("SELECT title, subject, author FROM books WHERE bookId = ?", (bookId,))
                results = cur.fetchall()
                print("Books Checked Out:")
                for idx, results in enumerate(results, start=1):
                    title, subject, author = results[:3]
                    print(f"{idx}. Title: {title}, Subject: {subject}, Author: {author}, Due Date: {dueDate}")
            else:
                print("No books checked out")

            print("\nOptions:")
            print("1. Delete User")
            print("2. Change Access")
            print("3. Cancel")

        while True:
            action = input("\nEnter the action: ")
            if action == "1":
                delete_user(userName)
                return
            elif action == "2":
                change_access(userName)
                return
            elif action == "3":
                print("Action has been cancelled")
                return
            else:
                print("Invalid input")

def delete_user(userName):
    cur.execute("DELETE FROM userIds WHERE userName = ? COLLATE NOCASE", (userName,))
    print(f"{userName} deleted successfully")
    con.commit()
    return

def change_access(userName):
    while True:
        print("Enter the new access level:\n1. Root\n2. User")
        option = input("Selection: ")
        if option == "1" or option == "2":
            cur.execute('''
                UPDATE userIds
                SET access = ?
                WHERE userName = ? COLLATE NOCASE''', (option, userName)) 
            con.commit()
            print(f"Access level updated to {option} for {userName}")
            return
        else:
            print("Access Unavailable")
            return


def sign_up():
    print("Please Enter Login Info:")
    firstName = input("\nFirst Name: ")
    lastName = input("Last Name: ")
    userName = input("UserName: ")
    password = input("Password: ")

    if not firstName or not lastName or not userName or not password:
        print("Please Fill all fields")
        sign_up()
        return
    
    cur.execute('''
            INSERT INTO userIds (firstName, lastName, userName, password, access)
                VALUES (?, ?, ?, ?, 2)
            ''', (firstName, lastName, userName, password))
    con.commit()
    sign_in()
    return

def addBook():
        title = input("Title: ")
        subject = input("Subject: ")
        author = input("Author: ")
        details = input("Description: ")
        cur.execute('''
            INSERT INTO books (title, subject, author, details, available)
            VALUES (?, ?, ?, ?, 2)
            ''', (title, subject, author, details))
        con.commit()

def lookupBook(userId, access):
    search = input("Search: ").lower()
    searchTerm = f"%{search}%"
    cur.execute('''SELECT title, subject, author FROM books 
                WHERE title LIKE ? COLLATE NOCASE
                OR subject LIKE ? COLLATE NOCASE
                OR author LIKE ? COLLATE NOCASE
                OR details LIKE ? COLLATE NOCASE
                ''', (searchTerm, searchTerm, searchTerm, searchTerm))
    results = cur.fetchall()
    
    if not results:
        print("No Books Found \nWould you like to add a book?\n1. Yes\n2. No")
        while True:
            addQuery = input("\nSelection: ")
            if addQuery == "1":
                addBook(access)
                return
            elif addQuery == "2":
                return None
            else:
                print("Invalid Input")

                

    else:
        print("\nBooks Found:")
        for idx, (title, subject, author) in enumerate(results, start=1):
            print(f"{idx}. Title: {title}, Subject: {subject}, Author: {author}")

        while True:
            try:
                selection = int(input(f"\nEnter Desired Book Number (1-{len(results)}): ")) -1
                if 0 <= selection < len(results):
                    break
                else:
                    print("Invalid Input")
            except ValueError:
                print("Invalid Input")
        
        selectedBook = results[selection][0]

        cur.execute("SELECT bookId, title, subject, author, details, available FROM books WHERE title = ? COLLATE NOCASE", (selectedBook,))
        bookInfo = cur.fetchone()

        if bookInfo:
            bookId, title, subject, author, details, available = bookInfo
            print(f"\nDetails for {title}:")
            print(f"\nSubject: {subject if subject else 'No Subject available'}")
            print(f"Author: {author if author else 'No Author available'}")
            print(f"Description: {details if details else 'No Description Available'}")
            print(f"available: {available}")
            if access == 1:
                print("Checked out to:")

                cur.execute("SELECT userId FROM checkouts WHERE bookId = ?", (bookId,))
                users = cur.fetchall()

                user_ids = [user[0] for user in users]

                if user_ids:

                    placeholders = ','.join(['?'] * len(user_ids))

                    cur.execute(f"SELECT firstName, lastName FROM userIds WHERE userId IN ({placeholders})", user_ids)
                    names = cur.fetchall()

                    for idx, (firstName, lastName) in enumerate(names, start=1):
                        print(f"{idx}. {lastName}, {firstName}")
                
                else:
                    print("No users have checked out this book.")

                print("\nOptions:")
                print("1. Delete Book")
                print("2. Check Out Book")
                print("3. Return Book")
                print("4. Cancel")

                while True:
                    action = input("\nEnter the action: ")
                    if action == "1":
                        delete_book(bookId, access)
                        return
                    elif action == "2":
                        if available <= 0:
                            print("No copies avaliable")
                            
                        else:
                            check_out_book(userId, bookId)
                            return
                    elif action == "3":
                        return_book(userId, bookId)
                        return
                    elif action == "4":
                        print("Action has been cancelled")
                        return
                    else:
                        print("Invalid input")
            else:
                print("\nOptions:")
                print("1. Check Out Book")
                print("2. Return Book")
                print("3. Cancel")
                while True:
                    action = input("\nEnter the action: ")
                    if action == "1":
                        if available <= 0:
                            print("No copies avaliable")
                            
                        else:
                            check_out_book(userId, bookId)
                            return
                    elif action == "2":
                        return_book(userId, bookId)
                        return
                    elif action == "3":
                        print("Action has been cancelled")
                        return
                    else:
                        print("Invalid input")

        else:
            print("No books found")


def delete_book(bookId, access):
    if access == 1:
        cur.execute("DELETE FROM books WHERE bookId = ?", (bookId,))
        print(f"{bookId} deleted successfully")
        con.commit()
    else:
        print("Access Unavailable")

def check_out_book(userId, bookId):
    cur.execute('''
                SELECT available FROM books
                WHERE bookId = ?''', (bookId,))
    book = cur.fetchone()

    if book and book[0] > 0:
        checkoutDate = datetime.date.today().strftime("%Y-%m-%d")
        dueDate = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")

        cur.execute('''
                INSERT INTO checkouts (userId, bookId, checkoutDate, dueDate)
                VALUES (?, ?, ?, ?)''', (userId, bookId, checkoutDate, dueDate))
        
        cur.execute('''
                UPDATE books SET available = available - 1 WHERE bookId = ?''', (bookId,))
        con.commit()

        print(f"Book {bookId} checked out successfully to {userId}, due date: {dueDate}")

    else:
        print("Book not available for checkout")

def return_book(userId, bookId):
    cur.execute('''
            SELECT checkoutId FROM checkouts
            WHERE userId = ?
            AND bookId = ?''', (userId, bookId))
    
    checkout = cur.fetchone()

    if checkout:
        cur.execute('''
                DELETE FROM checkouts 
                WHERE checkoutId = ?''', (checkout[0],))
        cur.execute('''
                UPDATE books SET available = available + 1 
                WHERE bookId = ?''', (bookId,))
        con.commit()

        print(f"Book {bookId} returned by User {userId}")

    else:
        print("This book was not checked out by user")
        

def getValidInput(login):
    userId, firstName, lastName, userName, password, access = login
    if access == 1:
        while True:
            print("\nWhat would you like to do? \n\n1. Add Book \n2. Lookup Book \n3. Lookup User \n4. Logout ")
            command  = input("\nEnter the action: ")
            if command == "1":
                addBook()
            elif command == "2":
                lookupBook(userId, access)
            elif command == "3":
                userEdit()
            elif command == "4":
                userLogin()
            else:
                print("Please Try Again")
    else:
        while True:
            print("\nWhat would you like to do? \n\n1. Lookup Book\n2. Logout ")
            command  = input("\nEnter the action: ")
            if command == "1":
                lookupBook(userId, access)
            elif command == "2":
                userLogin()
            else:
                print("Please Try Again")


userLogin()
con.close()