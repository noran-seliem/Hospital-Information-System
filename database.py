import mysql.connector
from datetime import datetime , timedelta
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="mysql",
    database="HIS22"
)
mycursor = mydb.cursor(dictionary=True , buffered=True)



# # Admins Table
# sql = "CREATE TABLE  IF NOT EXISTS Admins(ID INT NOT NULL AUTO_INCREMENT, Name VARCHAR(255), Email VARCHAR(255), Password VARCHAR(255), Phone VARCHAR(50), SSN VARCHAR(50) UNIQUE, Birthday DATE, PRIMARY KEY(id))"
# mycursor.execute(sql)

# # Inserting some data
# sql = "INSERT INTO Admins (Name, Email, Password, Phone, SSN, Birthday) VALUES (%s, %s, %s, %s, %s, %s)"
# val = [
#     ('Admin1', 'admin@hospital', '123', '01234567890', '234567','1976-06-02'),
#     ('Admin2', 'ad@aa.com', '123', '01234567890', '234577', '1985-12-02'),
#     ('m','m@gmail.com','1234','01234567890', '234578', '1985-12-02')
# ]


# mycursor.executemany(sql, val)
# mydb.commit()

# print(mycursor.rowcount, "was inserted.") 



# # Doctors Table
# sql = "CREATE TABLE IF NOT EXISTS Doctors( ID INT NOT NULL AUTO_INCREMENT, Name VARCHAR(255), Gender VARCHAR(10), Email VARCHAR(255),  Password VARCHAR(255),Phone VARCHAR(50),  SSN VARCHAR(50) UNIQUE, Birthday DATE, Join_date DATE, PRIMARY KEY(id))"
# mycursor.execute(sql)


# # Patients Table
# sql = "CREATE TABLE  IF NOT EXISTS Patients(ID INT NOT NULL AUTO_INCREMENT, Name VARCHAR(255), Gender VARCHAR(10), Email VARCHAR(255), Password VARCHAR(255), Phone VARCHAR(50), SSN VARCHAR(50) UNIQUE, Birthday DATE, Job VARCHAR(255), Join_date DATE, PRIMARY KEY(id), BloodType VARCHAR(10), Weight FLOAT, Height INT, Hypertension VARCHAR(5), ControlledHypertension VARCHAR(5), Diabetic VARCHAR(5), ControlledDiabetes VARCHAR(5), HeartStroke VARCHAR(5), Cholesterol VARCHAR(5))"
# mycursor.execute(sql)



# # Booked Appointments
# sql = "CREATE TABLE  IF NOT EXISTS Appointments(id INT NOT NULL AUTO_INCREMENT, patID INT NOT NULL, drID INT NOT NULL, bookedTime DATETIME, PRIMARY KEY(id), FOREIGN KEY (patID) REFERENCES Patients(id), FOREIGN KEY (drID) REFERENCES Doctors(id))"
# mycursor.execute(sql)


# # Questions from users
# sql = "CREATE TABLE IF NOT EXISTS ContactUsForms(id INT NOT NULL AUTO_INCREMENT, patID INT NOT NULL, is_solved TINYINT(1), subject VARCHAR(255), PRIMARY KEY(id), FOREIGN KEY (patID) REFERENCES Patients(id))"
# mycursor.execute(sql)


# # responses from admins and users on contact us forms questions 
# sql = "CREATE TABLE IF NOT EXISTS Messages(id INT NOT NULL AUTO_INCREMENT, msgTime TIMESTAMP, questionID INT NOT NULL, adminID INT, sender enum('A','p') NOT NULL, msg TEXT, PRIMARY KEY(id), FOREIGN KEY (questionID) REFERENCES ContactUsForms(id),  FOREIGN KEY (adminID) REFERENCES Admins(id))"
# mycursor.execute(sql)

# # #calendar table
# sql="CREATE TABLE IF NOT EXISTS Calendars(c_id  VARCHAR(500) ,drID INT NOT NULL , PRIMARY KEY(c_id) ,FOREIGN KEY (drID) REFERENCES Doctors(id))"
# mycursor.execute(sql)


# # #events table
# sql="CREATE TABLE IF NOT EXISTS Events(e_id  VARCHAR(500) ,cal_id  VARCHAR(500) , a_id INT, PRIMARY KEY(e_id) ,FOREIGN KEY (cal_id) REFERENCES Calendars(c_id),FOREIGN KEY (a_id) REFERENCES Appointments(id))"
# mycursor.execute(sql)