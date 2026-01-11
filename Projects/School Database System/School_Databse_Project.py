import sqlite3
import getpass
import hashlib

def hash_password(ProvPass):
    hash_object = hashlib.sha256(ProvPass.encode())
    hex_dig = hash_object.hexdigest()
    ProvPass=hex_dig
    return ProvPass

def Menu():
    print("Welcome to the School Database System!\n Enter 1-3 to be take to the function of your choice!\n 1. Enter Student, Enrollment, Professor or Course Data\n 2. Query a table from Students, Enrollments, Courses or Professors\n 3. Join tables\n")
    SubMenuChoice=int(input())
    print(SubMenuChoice)
    if(SubMenuChoice == 1):
        print("You have chosen to enter Student, Professor, Course or Enrollment data. Now starting...\n")
        SubMenuChoice1()
    elif(SubMenuChoice == 2):
        print("You have chosen to select a range of data from a specific table. Now starting...\n")
        SubMenuChoice2()
    elif(SubMenuChoice == 3):
        print("You have chosen to join two tables together and query that range. Now starting...\n")
        SubMenuChoice3()
    else:
        print("MMM Wrong! try again BRAINIAC")
        Menu()

#Defines the function called based on user input from function Menu()
def SubMenuChoice1():
    FunctionChoice=int(input("Enter number 1-4 to take you to the correct function:\n1. Enter Student Data\n2. Enter Enrollment Data\n3. Enter Professor Data\n4. Enter Course Data\n"))
    if(FunctionChoice == 1):
        print("You have chosen to enter Student data. Now starting...\n")
        StudentAmount=int(input("How many students are being entered?\n"))
        insert_StudentData(conn,StudentAmount)

    elif(FunctionChoice == 2):
        print("You have chosen to enter Enrollment data. Now starting...\n")
        EnrollmentAmount=int(input("How many students are being Enrolled?\n"))
        insert_EnrollmentData(conn,EnrollmentAmount)

    elif(FunctionChoice == 3):
        print("You have chosen to enter Professor data. Now starting...\n")
        ProfessorAmount=int(input("How many professors are being entered?\n"))
        insert_ProfessorData(conn,ProfessorAmount)

    elif(FunctionChoice == 4):
        print("You have chosen to enter Course data. Now starting...\n")
        CourseAmount=int(input("How many courses are being entered?\n"))
        insert_CourseData(conn,CourseAmount)
    else:
        print("MMM Wrong!")
        SubMenuChoice1()

def SubMenuChoice2():
    print("THIS FUNCTION MUST ONLY BE USED FOR LEGITIMATE BUSINESS PURPOSES, MISUSE RESULTS IN LEGAL ACTION.")
    ProvID=input("Enter your Professor ID to continueL\n")
    ProvPass=input("Enter your Password to continue:\n")
    loginValidate(ProvID,ProvPass)

def SubMenuChoice3():
    print("HAHAHAHAHHAHAA")

def SelectDatafunction():
    select_data(conn)
    print("Press Any Key To Return To Menu\n")
    input()

def loginValidate(ProvID, ProvPass):
    connection = sqlite3.connect('SchoolDatabase.db')
    cursor = connection.cursor()

    cursor.execute('SELECT HASHEDPASSWORDS FROM ProfPass WHERE ProfessorID={ProvID}')
    check = cursor.fetchall()
    for i in check:
        if ProvID in i and hash_password(ProvPass) in i:
            print(f"Welcome Professor {ProvID}, you are logged into the system now")
            SelectDatafunction()
        else: 
            print("Login Failed, Incorrect ID or Password")
            SubMenuChoice2()



def build_table(conn):
    #Students table which has StudentID which is a foreign key for Enrollments
    conn.execute("""CREATE TABLE IF NOT EXISTS Students(
                 StudentID INTEGER PRIMARY KEY,
                 Firstname TEXT NOT NULL,
                 Surname TEXT NOT NULL,
                 EmailAddress TEXT NOT NULL
    );""")
    
    #Professors table which contains ProfID which is a foreign key for Courses
    conn.execute("""CREATE TABLE IF NOT EXISTS Professors(
                 ProfID INTEGER PRIMARY KEY,
                 Firstname TEXT NOT NULL,
                 Surname TEXT NOT NULL,
                 EmailAddress TEXT NOT NULL
    );""")
    
    #Courses table which contains a foregin key for Enrollments(CourseID) and a foreign key from Professors(ProfID)
    conn.execute("""CREATE TABLE IF NOT EXISTS Courses( 
                 CourseID INTEGER PRIMARY KEY,
                 CourseName TEXT NOT NULL,
                 CourseDesc TEXT NOT NULL,
                 ProfID INTEGER NOT NULL,
                 FOREIGN KEY (ProfID) REFERENCES Professors(ProfID)
    );""")
    
    #Enrollments table which contains a foreign key for Courses and a foreign key from Students
    conn.execute("""CREATE TABLE IF NOT EXISTS Enrollments(
                 EnrollmentID INTEGER PRIMARY KEY,
                 EnrollmentDate DATE NOT NULL,
                 StudentID INTEGER NOT NULL,
                 CourseID INTEGER NOT NULL,
                 FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
                 FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
    );""")
    conn.execute("""CREATE TABLE IF NOT EXISTS ProfPass(
                 ProfessorID INTEGER PRIMARY KEY,
                 HASHEDPASSWORD TEXT NOT NULL,
                 PASSWORDAGE INTEGER NOT NULL
    );""")

    conn.commit()

#Inserts data based on a query

#Inserts Student Data into the Students table
def insert_StudentData(conn,StudentAmount):
    catagories_Students = ["StudentID","FirstName", "Surname", "EmailAddress"]
    StudentID=0
    for i in range (StudentAmount):
        StudentID= i+1
        FirstName = str(input("Enter First Name:\n"))
        Surname = str(input("Enter Surname:\n"))
        EmailAddress = str(input("Enter Email Address: \n"))
        conn.execute("""INSERT INTO STUDENTS (FirstName, Surname, EmailAddress)
        VALUES (?,?,?)""", (FirstName, Surname, EmailAddress))
    print("Commiting to Database. Press Any Key To Return To Menu\n")
    input()
    conn.commit()
    Menu()

#Inserts Professor Data into the Professors Table
def insert_ProfessorData(conn,ProfessorAmount):
    catagories_Professors = ["ProfID","FirstName","Surname","EmailAddress"]
    ProfessorID=0
    for i in range (ProfessorAmount):
        ProfID = i+1
        FirstName = str(input("Enter FirstName:\n "))
        Surname = str(input("Enter Surname:\n"))
        EmailAddress = str(input("Enter Email Address:\n"))
        conn.execute("""INSERT INTO Professors (FirstName, Surname, EmailAddress)
        VALUES (?,?,?)""", (FirstName, Surname, EmailAddress))
    print("Commiting to Database. Press Any Key To Return To Menu\n")
    input()
    conn.commit()
    Menu()

#Inserts Course Data into the Courses Table     
def insert_CourseData(conn,CourseAmount):
    catagories_Courses = ["CourseID","CourseName","CourseDesc","ProfID"]
    CourseID=0
    for i in range (CourseAmount):
        CourseID = i+1
        CourseName = str(input("Enter Course Name:\n "))
        CourseDesc = str(input("Enter Course Description:\n"))
        ProfID= int(input("Enter Professor ID:\n"))
        conn.execute("""INSERT INTO Courses (CourseName, CourseDesc, ProfID)
        VALUES (?,?,?)""", (CourseName, CourseDesc, ProfID))
    print("Commiting to Database. Press Any Key To Return To Menu\n")
    input()
    conn.commit()
    Menu()

#Inserts Enrollment Data into the Enrollments Table
def insert_EnrollmentData(conn,EnrollmentAmount):
    catagories_Enrollments = ["EnrollmentID","EnrollmentDate","StudentID","CourseID"]
    EnrollmentID=0
    for i in range (EnrollmentAmount):
        EnrollmentID = i+1
        EnrollmentDate = str(input("Enter Student's Enrollment Date:\n "))
        StudentID = str(input("Enter Student ID:\n"))
        CourseID = str(input("Enter their CourseID:\n"))
        conn.execute("""INSERT INTO Enrollments (EnrollmentDate, StudentID, CourseID)
        VALUES (?,?,?)""", (EnrollmentDate, StudentID, CourseID))
    print("Commiting to Database. Press Any Key To Return To Menu\n")
    input()
    conn.commit()
    Menu()


#Selects data from a table based on a query
def select_data(conn):
    try:

        cursor = conn.execute(str(input("Enter your SQL Query: \n")))
    finally:
        print("Placeholder")
    for row in cursor:
        print("ID = ", row[0])
        print("NAME = ", row[1])
        print("AGE = ", row[2])
        print("ADDRESS = ", row[3])
        print("SALARY = ", row[4], "\n")
#Joins two databases together based on a matched key
def join_data(conn):
    cursor = conn.execute(
        """SELECT * FROM JOB JOIN COMPANY ON JOB.bossID = COMPANY.ID;""")
    for i in cursor():
        print(i)


#Connects the SQL instance to all databases listed
conn = sqlite3.connect(("SchoolDatabase.db"))

build_table(conn)
#Menu()
conn.execute("""INSERT INTO LoginDetails (ProfessorID, Hashed, score)
          values(1, 99, 123)""")



















conn.close()