#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                                     Imported Libraries
#
#
#                                                                                     
#
#______________________________________________________________________________________________________________________________________________________________________________________________________
import sqlite3
import getpass
import hashlib

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#                                                                                       MENU FUNCTIONS
#
#
#_______________________________________________________________________________________________________________________________________________________________________

def main():
    try:
        conn = sqlite3.connect(("SchoolDatabase.db"))
        build_table(conn)
        Menu()
        conn.close()
    except:
        print("An error occurred while connecting to the database.")
def Menu():
    try:
        if (loginValidate() == True):
            SubMenu()
        else:
            Menu()
    except ValueError:
        print("Unacceptable Input, Please Try Again.\n")
        Menu()
def SubMenu():
    try:
        while True:
            SubMenu = {"1": SubMenuChoice1, "2": SubMenuChoice2, "3": SubMenuChoice3}
            SubMenuChoice=int(input("Welcome to the School Database System!\n Enter 1-3 to be take to the function of your choice!\n 1. Enter Student, Enrollment, Professor or Course Data\n 2. Query a table from Students, Enrollments, Courses or Professors\n 3. Join tables\n"))
            SubMenu.get(str(SubMenuChoice), lambda: "Invalid choice")()
    except ValueError:
            print("Unacceptable Input, Please Try Again.\n")

def SubMenuChoice1():
    try:
        SubMenu1 = {"1": insert_StudentData, "2": insert_EnrollmentData, "3": insert_ProfessorData, "4": insert_CourseData}
        UserChoice=int(input("THIS FUNCTION MUST ONLY BE USED FOR LEGITIMATE BUSINESS PURPOSES, MISUSE RESULTS IN LEGAL ACTION.\nEnter your Professor ID to continue\n"))
        UserPass=getpass.getpass(prompt = str("Enter your Password to continue:\n"))
        if loginValidate(UserChoice,UserPass) == True:
            SubMenu1.get(str(UserChoice), lambda: "Invalid choice")()
        else:
            SubMenuChoice1()
    except ValueError:
        print("Unacceptable Input, Please Try Again.\n")
        SubMenuChoice1()
def SubMenuChoice2():
    try:
        loginValidate()
        if (loginValidate() == True):
            SelectDatafunction()
        else:
            SubMenuChoice2()

    except ValueError:
        print("Unacceptable Input, Please Try Again.\n")
        SubMenuChoice2()
def SubMenuChoice3():
    pass

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#                                                                                    Security Functions
#
#
#______________________________________________________________________________________________________________________________________________________________________

def hash_password(ProvPass):
    try:
        hash_object = hashlib.sha256(ProvPass.encode())
        hex_dig = hash_object.hexdigest()
        ProvPass=hex_dig
        return ProvPass
    except:
        print("An error occurred during password hashing.")
        return None
def loginValidate():
    try:
        connection = sqlite3.connect('SchoolDatabase.db')
        cursor = connection.cursor()
        ProvID=int(input("THIS PROGRAM MUST ONLY BE USED FOR LEGITIMATE BUSINESS PURPOSES, MISUSE RESULTS IN LEGAL ACTION.\nEnter your Professor ID to continue\n"))
        ProvPass=getpass.getpass(prompt = str("Enter your Password to continue:\n"))
        cursor.execute(f'SELECT HASHEDPASSWORD FROM ProfPass WHERE ProfessorID={ProvID}')
        StoredCred = cursor.fetchone()[0]
        connection.close()
        if (ProvID <= 30 and ProvID >= 0) and (hash_password(ProvPass) == StoredCred):
            print(f"Welcome Professor {ProvID}, you are logged into the system now")
            return True
        else: 
            print("Login Failed, Incorrect ID or Password")
            Menu()
            return False
    except Exception as e:
        print("An error occurred during login:", e)
        Menu()
        return False

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#                                                                      Database Functions(uncallable directly by user)
#
#
#______________________________________________________________________________________________________________________________________________________________________


def build_table(conn):
    try:

        conn.execute("""CREATE TABLE IF NOT EXISTS Students(StudentID INTEGER PRIMARY KEY, Firstname TEXT NOT NULL, Surname TEXT NOT NULL, EmailAddress TEXT NOT NULL);""")

        conn.execute("""CREATE TABLE IF NOT EXISTS Professors(ProfID INT PRIMARY KEY, Firstname TEXT NOT NULL, Surname TEXT NOT NULL, EmailAddress TEXT NOT NULL);""")

        conn.execute("""CREATE TABLE IF NOT EXISTS Courses(CourseID INTEGER PRIMARY KEY, CourseName TEXT NOT NULL, CourseDesc TEXT NOT NULL, ProfID INT NOT NULL, FOREIGN KEY (ProfID) REFERENCES Professors(ProfID) );""")

        conn.execute("""CREATE TABLE IF NOT EXISTS Enrollments(EnrollmentID INTEGER PRIMARY KEY, EnrollmentDate DATE NOT NULL, StudentID INTEGER NOT NULL, CourseID INTEGER NOT NULL, FOREIGN KEY (StudentID) REFERENCES Students(StudentID), FOREIGN KEY (CourseID) REFERENCES Courses(CourseID));""")

        conn.execute("""CREATE TABLE IF NOT EXISTS ProfPass(ProfessorID INT PRIMARY KEY, HASHEDPASSWORD TEXT NOT NULL, PASSWORDAGE INTEGER NOT NULL);""")

        conn.commit()
    except:
        print("An error occurred while building the tables.")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#                                                                            Database functions users can callaa
#
#
#_____________________________________________________________________________________________________________________________________________________________________
def insert_StudentData(conn,StudentAmount):
    try:
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
    except:
        print("An error occurred while inserting student data.")
        Menu()

def insert_ProfessorData(conn,ProfessorAmount):
    try:
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
    except:
        print("An error occurred while inserting professor data.")
        Menu()

def insert_CourseData(conn,CourseAmount):
    try:
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
    except:
        print("An error occurred while inserting course data.")
        Menu()

def insert_EnrollmentData(conn,EnrollmentAmount):
    try:
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
    except:
        print("An error occurred while inserting enrollment data.")
        Menu()

def join_data(conn):
    try:
        cursor = conn.execute(
            """SELECT * FROM JOB JOIN COMPANY ON JOB.bossID = COMPANY.ID;""")
        for i in cursor():
            print(i)
    except:
        print("An error occurred while joining the data.")

def SelectDatafunction():
    try:
        print("Below are the tables you can query from:\n 1. Students\n 2. Professors\n 3. Courses\n 4. Enrollments\nEnter your selection below:\n")
        TableChoice=int(input(""))
        if(TableChoice == 1):
            select_StudentData(conn)
        elif(TableChoice == 2):
            select_ProfessorData(conn)
        elif(TableChoice ==3):
            select_CourseData(conn)
        elif(TableChoice ==4):
            select_EnrollData(conn)
        else:
            print("Unacceptable Input, Please Try Again.\n")
            SelectDatafunction()
    except ValueError:
        print("Unacceptable Input, Please Try Again.\n")
        SelectDatafunction()

def select_StudentData(conn):
    try:
        loginValidate()
        if(loginValidate() == True):
            cursor = conn.execute("""SELECT * FROM Students WHERE StudentID = ?;""", (int(input("Enter Student ID to query:\n")),))
            print(cursor.fetchall())
        else:
            Menu()
    except ValueError:
        print("Invalid input. Please enter a valid Student ID.")
        Menu()

def select_ProfessorData(conn):
    try:
        loginValidate()
        if(loginValidate() == True):
            cursor = conn.execute("""SELECT * FROM Professors WHERE ProfID = ?;""", (int(input("Enter Professor ID to query:\n")),))
            print(cursor.fetchall())
        else:
            Menu()
    except ValueError:
        print("Invalid input. Please enter a valid Professor ID.")

def select_CourseData(conn):
    try:
        loginValidate()   
        if(loginValidate() == True): 
            cursor = conn.execute("""SELECT * FROM Courses WHERE CourseID = ?;""", (int(input("Enter Course ID to query:\n")),))
            print(cursor.fetchall())
        else:
            Menu()
    except ValueError:
        print("Invalid input. Please enter a valid Course ID.")

def select_EnrollData(conn):
    try:
        loginValidate()
        if(loginValidate() == True):
            cursor = conn.execute("""SELECT * FROM Enrollments WHERE EnrollmentID = ?;""", (int(input("Enter Enrollment ID to query:\n")),))
            print(cursor.fetchall())
        else:
            Menu()
    except ValueError:
        print("Invalid input. Please enter a valid Enrollment ID.")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                                Program Starts Here
#_________________________________________________________________________________________________________________________________________________________________________
main()