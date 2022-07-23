from flask import Flask, Blueprint, render_template, request, session, flash, redirect, url_for, Response
from database import mydb 
import mysql.connector
import itertools, g_api
import re ,math , random
from datetime import datetime , timedelta
import time
import io 
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")


# mycursor = mydb.cursor(dictionary=True)
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="mysql",
  database="HIS22"
)
mycursor = mydb.cursor(dictionary=True, buffered=True)



@admin.route('/login',methods=['GET','POST'])
def A_login():
   mycursor = mydb.cursor(dictionary=True)
   if request.method == 'POST':
      if 'loggedin' in session:
         session.clear()
         flash("Logout First")
         return render_template("SignIn.html")
      email = request.form['email']
      password = request.form['password']
      #check if user exists in the database
      sql = 'SELECT * FROM Admins WHERE Email = %s AND Password = %s'
      val = (email, password)
      mycursor.execute(sql, val)
      # Fetch user's record
      account = mycursor.fetchone()
      #check if account exists in the database
      if account:
         #create session data
         session['loggedin'] = True
         session['u_id'] = account['ID']
         session['email'] = account['Email']
         session['user']=account['Name']
         session['msg']='A'
         flash("signed in successfully!")
         return redirect(url_for('admin.adminDash'))
      else:
         #if account doesnt exist or email/password incorrect
         flash('Your email or password were incorrect')
         return render_template('SignIn.html')
   else:
      return render_template('SignIn.html')

@admin.route('/dashboard')
def adminDash():
   return render_template("dashboard.html")


# view profile
@admin.route('/profile', methods=['GET', 'POST'])
def profile():
    mycursor = mydb.cursor()
    a_id=session["u_id"]
    mycursor.execute("SELECT * FROM Admins where ID = '%s'" %(a_id)) 
    row_headers = [x[0] for x in mycursor.description]
    myresult = mycursor.fetchone()
    if request.method == 'GET':
        return render_template("profile.html", type=type, adminData=zip(row_headers, myresult), view=1)
    else:
        if 'edit' in request.form:  # requesting the edit form
            return render_template("profile.html", type=type, adminData=zip(row_headers, myresult), edit=1)
        elif 'change' in request.form: # requesting to change password
            return render_template("profile.html", type=type, adminData=zip(row_headers, myresult), change=1)
        else:
            flash("Bad request", "error")
            return render_template("profile.html", type=type, adminData=zip(row_headers, myresult), view=1)



# edit profile
@admin.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    mycursor = mydb.cursor()
    a_id = session["u_id"]
    if request.method == 'GET':
        mycursor.execute("SELECT * FROM Admins where ID = '%s'" %(a_id)) 
        row_headers = [x[0] for x in mycursor.description]
        myresult = mycursor.fetchone()
        return render_template("profile.html", type=type, adminData=zip(row_headers, myresult), edit=1)
    else:
        if 'edit' in request.form:
            name = request.form['Name']
            email = request.form['Email']
            phone = request.form['Phone']
            ssn = request.form['SSN']
            bday = request.form['Birthday']
            try:
                # print(name, email, phone, ssn, bday, a_id)
                mycursor.execute("UPDATE Admins SET Name = '%s', Email = '%s', Phone = '%s', SSN = '%s', Birthday = '%s' WHERE ID = '%s'" % (name, email, phone, ssn, bday, a_id))
                mydb.commit()
                flash("Profile updated successfully!", "info")
            except:
                flash("Something went wrong!", "error")
        elif 'change' in request.form: #for changing password
            old_pw = request.form['password']
            mycursor.execute("SELECT Password FROM Admins where ID = '%s'" %(a_id))
            myresult = mycursor.fetchone()
            pw = myresult[0]
            # print(pw, old_pw)
            if pw == old_pw:
                new_pw = request.form['newpassword']
                mycursor.execute("UPDATE Admins SET Password = '%s' WHERE ID = '%s'" % (new_pw, a_id))
                mydb.commit()
                flash("Password changed successfully!", "info")
            else:
                flash("Incorrect password!", "error")
        return redirect(url_for('admin.profile'))



# add a doctor
@admin.route("/add_doctor", methods=['GET', 'POST'])
def addDr():
    mycursor = mydb.cursor()

    if request.method == 'GET':
        return render_template("A_add_doctor.html")
    else:
        email = request.form['email']
        mycursor.execute("SELECT * FROM Doctors WHERE Email = '%s'" %(email))
        result = mycursor.fetchone()
        if result:
            return render_template("A_add_doctor.html", err="This email is already registered!")
        else:
            name = request.form['name']
            gender = request.form['gender']
            phone = request.form['phone']
            pw = request.form['password']
            # DATE format YYYY-MM-DD
            bdate = request.form['birthday']
            ssn = request.form['SSN']
            today = time.strftime('%Y-%m-%d')
            try:
                sql = "INSERT INTO Doctors (Name, Gender, Email, Password, Phone, SSN, Birthday, Join_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                val = (name, gender, email, pw, phone, ssn, bdate, today)
                mycursor.execute(sql, val)
                mydb.commit()
                return render_template("A_add_doctor.html", succ="Doctor registered successfully.")
            except:
                return render_template("A_add_doctor.html", err="Something went wrong.") #"please check your ssn"


# add a patient
@admin.route("/add_patient", methods=['GET', 'POST'])
def addPatient():
    mycursor = mydb.cursor()
    if request.method == 'GET':
        return render_template("A_addpatient.html")
    else:
        email = request.form['email']
        mycursor.execute("SELECT * FROM Patients WHERE Email = '%s'" %(email))
        result = mycursor.fetchone()
        if result:
            return render_template("A_addpatient.html", err="This email is already registered!")
        else:
            fname = request.form['fname']
            lname = request.form['lname']
            name = fname + " " + lname
            phone = request.form['phone']
            pw = request.form['password']
            # DATE format YYYY-MM-DD
            bdate = request.form['birthday']
            ssn = request.form['SSN']
            today = time.strftime('%Y-%m-%d')
            if ssn == "":
                ssn = None
            gender = request.form['gender']
            if gender == '0':
                gender = None
            job = request.form['job']
            bloodtype = request.form['bloodtype']
            if bloodtype == '0':
                bloodtype = None
            weight = request.form['weight']
            if weight == "":
                weight = None
            height = request.form['height']
            if height == "":
                height = None
            hypertension = request.form.get('hypertension')
            HyperControl = request.form.get('controlledH')
            diabetic = request.form.get('diabetic')
            diabetesControl = request.form.get('controlledDiabetes')
            heartStroke = request.form.get('heartStroke')
            cholesterol = request.form.get('cholesterol')
            # print(name, email, pw, phone, ssn,gender, bdate, job, bloodtype,
            #     weight, height, hypertension, HyperControl, diabetic, diabetesControl, heartStroke, cholesterol)
            try:
                sql = "INSERT INTO Patients (Name, Email, Password, Phone,Gender, Birthday,SSN,Job,BloodType,Weight,Height,Hypertension,ControlledHypertension,Diabetic,ControlledDiabetes,HeartStroke, Cholesterol, Join_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (name, email, pw, phone, gender, bdate, ssn, job, bloodtype,
                    weight, height, hypertension, HyperControl, diabetic, diabetesControl, heartStroke, cholesterol, today)
                mycursor.execute(sql, val)
                mydb.commit()
                return render_template("A_addpatient.html", succ="Patient added successfully.")
            except:
                return render_template("A_addpatient.html", err="Something went wrong.") #check your ssn


# viewing all doctors' records
@admin.route('/view_doctors', methods=['GET', 'POST'])
def view_drs():
    mycursor = mydb.cursor()
    if request.method == 'GET':
        mycursor.execute("SELECT * FROM Doctors")
        # this will extract row headers
        row_headers = [x[0] for x in mycursor.description]
        myresult = mycursor.fetchall()
        return render_template("A_view_doctors.html", AllDoctors=myresult, headers=row_headers)
    else:
        if 'edit' in request.form:
            drid = request.form['edit']
            # print(drid)
            mycursor.execute("SELECT * FROM Doctors WHERE ID = '%s'" %(drid))
            row_headers = [x[0] for x in mycursor.description] 
            myresult = mycursor.fetchone() 
            return render_template("A_update_doctors.html", type=type, Data=zip(row_headers, myresult))
        else: #delete
            drid = request.form['del']
            # print(drid)
            try:
                mycursor.execute("DELETE FROM Doctors WHERE ID = '%s'" %(drid))
                mydb.commit()
                #delete calendar of the doctor
                mycursor.execute("SELECT c_id FROM Calendars WHERE drID ='%s'" %(drid))
                c_id=mycursor.fetchone()
                g_api.delete_calendar(c_id['c_id'])
                mycursor.execute("DELETE FROM Calendars WHERE c_id='%s'" %(c_id['c_id']))
                mydb.commit()
                ##
                mycursor.execute("SELECT * FROM Doctors")
                row_headers = [x[0] for x in mycursor.description]
                myresult = mycursor.fetchall()
                return render_template("A_view_doctors.html", AllDoctors=myresult, headers=row_headers, succ = "Doctor deleted successfully.")
            except:
                mycursor.execute("SELECT * FROM Doctors")
                row_headers = [x[0] for x in mycursor.description]
                myresult = mycursor.fetchall()
                return render_template("A_view_doctors.html", AllDoctors=myresult, headers=row_headers, err = "Something went wrong.")


# viewing all patients' records
@admin.route('/view_patients', methods=['GET', 'POST'])
def view_patients():
    mycursor = mydb.cursor()
    if request.method == 'GET':
        mycursor.execute("SELECT ID, Name, Email, Password, Phone, Gender, SSN, Birthday, Job , Join_date FROM Patients")
        # this will extract row headers
        row_headers = [x[0] for x in mycursor.description]
        myresult = mycursor.fetchall()
        return render_template("A_view_patients.html", AllPatients=myresult, headers=row_headers)
    else:
        if 'edit' in request.form:
            patid = request.form['edit']
            mycursor.execute("SELECT * FROM Patients WHERE ID = '%s'" %(patid))
            row_headers = [x[0] for x in mycursor.description] 
            myresult = mycursor.fetchone() 
            return render_template("A_update_patients.html", type=type, Data=zip(row_headers, myresult))
        else: #delete
            patid = request.form['del']
            try:
                mycursor.execute("DELETE FROM Patients WHERE ID = '%s'" %(patid))
                mydb.commit()
                mycursor.execute("SELECT * FROM Patients")
                row_headers = [x[0] for x in mycursor.description]
                myresult = mycursor.fetchall()
                return render_template("A_view_patients.html", AllPatients=myresult, headers=row_headers, succ = "Patient deleted successfully.")
            except:
                mycursor.execute("SELECT * FROM Patients")
                row_headers = [x[0] for x in mycursor.description]
                myresult = mycursor.fetchall()
                return render_template("A_view_patients.html", AllPatients=myresult, headers=row_headers, err = "Something went wrong.")


# viewing and editing a doctor's profile
@admin.route('/edit/d', methods=['POST'])
def editDr():
    mycursor = mydb.cursor()
    dr_id = request.form['ID']
    name = request.form['Name']
    gender = request.form['Gender']
    email = request.form['Email']
    phone = request.form['Phone']
    pw = request.form['Password']
    # DATE format YYYY-MM-DD
    bdate = request.form['Birthday']
    ssn = request.form['SSN']
    try:
        sql = "UPDATE Doctors SET Name = %s, Gender = %s, Email = %s, Password = %s, Phone = %s, SSN = %s, Birthday = %s WHERE ID = %s"
        val = (name, gender, email, pw, phone, ssn, bdate, dr_id)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.execute("SELECT * FROM Doctors WHERE ID = '%s'" %(dr_id))
        row_headers = [x[0] for x in mycursor.description] 
        myresult = mycursor.fetchone() 
        return render_template("A_update_doctors.html", type=type, Data=zip(row_headers, myresult), succ ="Doctor's profile updated successfully.")
    except:
        mycursor.execute("SELECT * FROM Doctors WHERE ID = '%s'" %(dr_id))
        row_headers = [x[0] for x in mycursor.description] 
        myresult = mycursor.fetchone() 
        return render_template("A_update_doctors.html", type=type, Data=zip(row_headers, myresult), err = "Something went wrong.")

# viewing and editing a patient's profile
@admin.route('/edit/p', methods=['POST'])
def editpat():
    mycursor = mydb.cursor()
    pat_id =  request.form['ID']
    name = request.form['Name']
    gender = request.form['Gender']
    email = request.form['Email']
    pw = request.form['Password']
    phone = request.form['Phone']
    # DATE format YYYY-MM-DD
    bdate = request.form['Birthday']
    ssn = request.form['SSN']
    job = request.form['Job']
    bloodtype = request.form['BloodType']
    weight = request.form['Weight']
    height = request.form['Height']
    hyper = request.form['Hypertension']
    hypercont = request.form['ControlledHypertension']
    diabetic = request.form['Diabetic']
    diacont = request.form['ControlledDiabetes']
    stroke = request.form['HeartStroke']
    cholesterol = request.form['Cholesterol']

    try:
        sql = "UPDATE Patients SET Name = %s, Gender = %s, Email = %s, Password = %s, Phone = %s, SSN = %s, Birthday = %s, Job = %s, BloodType = %s, Weight = %s, Height = %s, Hypertension = %s, ControlledHypertension = %s, Diabetic = %s, ControlledDiabetes = %s, HeartStroke = %s, Cholesterol = %s WHERE ID = %s"
        val = (name, gender, email, pw, phone, ssn, bdate, job, bloodtype, weight, height, hyper, hypercont,diabetic, diacont, stroke, cholesterol, pat_id)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.execute("SELECT * FROM Patients WHERE ID = '%s'" %(pat_id))
        row_headers = [x[0] for x in mycursor.description] 
        myresult = mycursor.fetchone() 
        return render_template("A_update_patients.html", type=type, Data=zip(row_headers, myresult), succ ="Patient's profile updated successfully.")
    except:
        mycursor.execute("SELECT * FROM Patients WHERE ID = '%s'" %(pat_id))
        row_headers = [x[0] for x in mycursor.description] 
        myresult = mycursor.fetchone() 
        return render_template("A_update_patients.html", type=type, Data=zip(row_headers, myresult), err = "Something went wrong.")



# view contact us form questions
@admin.route('/messages')
def msg():
   mycursor = mydb.cursor(dictionary=True)
   sql = "SELECT id, subject FROM ContactUsForms WHERE is_solved IS NULL"
   mycursor.execute(sql)
   unsolved = mycursor.fetchall()

   sql = "SELECT id, subject FROM ContactUsForms WHERE is_solved IS NOT NULL"
   mycursor.execute(sql)
   solved = mycursor.fetchall()
   return render_template("all_questions.html", unsolved=unsolved, solved=solved) 


@admin.route('/unsolved/<Qid>', methods=['GET', 'POST'])
def unsolved(Qid):
    mycursor = mydb.cursor(dictionary=True)
    if request.method == 'GET':
        mycursor.execute("SELECT msgTime, sender, msg FROM Messages WHERE questionID = %s" %(Qid))
        messages = mycursor.fetchall()
        mycursor.execute("SELECT id, subject FROM ContactUsForms WHERE id = %s" %(Qid))
        msg = mycursor.fetchone()
        return render_template("question_thread.html", messages=messages,msg=msg, unsolved=1)
    else:
       if 'send' in request.form:
            msg = request.form['msg']
            sql = "INSERT INTO Messages (msgTime, questionID, adminID, sender, msg) VALUES (%s,%s,%s,%s,%s)"
            msgtime = datetime.now()
            a_id=session["u_id"]
            val = (msgtime, Qid, a_id, 'A', msg)
            mycursor.execute(sql,val)
            mydb.commit()
            return redirect(url_for('admin.unsolved', Qid=Qid))

       elif 'solved' in request.form:
          mycursor.execute("UPDATE ContactUsForms SET is_solved = 1 WHERE id = %s" %(Qid))
          mydb.commit()
          return redirect(url_for('admin.msg'))


@admin.route('/solved/<Qid>')
def solved(Qid):
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT msgTime, sender, msg FROM Messages WHERE questionID = %s" %(Qid))
    messages = mycursor.fetchall()
    mycursor.execute("SELECT id, subject FROM ContactUsForms WHERE id = %s" %(Qid))
    msg = mycursor.fetchone()
    return render_template("question_thread.html", messages=messages,msg=msg)
@admin.route('/manage_cal')
def manage_cal():
    return render_template("calendar.html")
@admin.route('/add_cal', methods=['GET', 'POST'])
def add_cal():
    if request.method=='POST':
        doctor_id=request.form['drID']
        mycursor.execute("SELECT * From Calendars")
        c = mycursor.fetchall()
        if c:
            flash("Dr Already has a calendar , Remove the calendar first")
            return render_template("calendar.html")
        mycursor.execute("SELECT Email FROM Doctors WHERE ID ='%s'" %(doctor_id))
        doctor_email=mycursor.fetchone()
        ID = g_api.create_calendar("Cardiology Department","Africa/Cairo")
        g_api.give_access(ID,doctor_email['Email'])
        sql="INSERT INTO Calendars (c_id,drID) VALUES (%s,%s)"
        val=(ID,doctor_id)
        print(val)
        mycursor.execute(sql,val)
        mydb.commit()
        flash("Calendar is aded Successfully!")
    return render_template("calendar.html")

@admin.route('/remove_cal', methods=['GET', 'POST'])
def remove_cal():
    if request.method=='POST':
        doctor_id=request.form['drID']
        mycursor.execute("SELECT c_id FROM Calendars WHERE drID ='%s'" %(doctor_id))
        c_id=mycursor.fetchone()
        if c_id:
            g_api.delete_calendar(c_id['c_id'])
            mycursor.execute("DELETE FROM Calendars WHERE c_id='%s'" %(c_id['c_id']))
            mydb.commit()
            flash("Calendar is Removed Successfully!")
        else:
            flash("Doctor has no Calendar")
    return render_template("calendar.html")



@admin.route('/bookAppointment', methods=['GET','POST'])
def book():
    mycursor = mydb.cursor(dictionary=True, buffered=True)
    mycursor.execute("SELECT * FROM Doctors")
    myresult = mycursor.fetchall()
    number_of_doctors= len(myresult)
    id_1_l= math.ceil((number_of_doctors/2))

    if request.method=='POST':
        selected_data= request.form['doctor']
        selected_date = request.form['date'] #in mm/dd/yyy
        selected_hour = request.form['hour']
        p_id=request.form['p_id']
        #check if date or time is empty
        if (not request.form['date']) or request.form['hour']=='Select Time': 
            # print("jjj"))
            flash("please select a date, a time and a doctor/Not Specific Doctor ")
            return render_template("p_book_appointment.html", doctorsData = myresult,  id_1_l=id_1_l )

        #get the values we need
        if selected_data != 'Not Specific Doctor':
            doctor_id , selected_doctor = selected_data.split('-') 
        else:
            doctor_id = random.randint(1, number_of_doctors)

        #get the values we need
        format_str = '%m/%d/%Y' # The format
        date_datetime = datetime.strptime(selected_date, format_str).date()
        time_datetime = datetime.strptime(selected_hour , '%H:%M').time()
        bookedTime = datetime.combine(date_datetime, time_datetime)
        #check if the time is booked already in doctor's schedule 
        sql = 'SELECT * FROM Appointments WHERE drID = %s AND bookedTime = %s'
        val = (doctor_id,bookedTime)
        mycursor.execute(sql, val)
        # Fetch user's record
        account = mycursor.fetchall()
        # If account exists show error and validation checks
        if account:
            flash('Doctor is not available in this time, choose another time!')
            return render_template("p_book_appointment.html", doctorsData = myresult,  id_1_l=id_1_l )
        # Nothing wrong with booking, insertingappointment details 
        id=session["u_id"] 
        sql = "INSERT INTO Appointments (drID,bookedTime, patID) VALUES (%s, %s, %s)"
        val = (doctor_id, bookedTime, p_id)
        # print(val)
        mycursor.execute(sql, val)
        mydb.commit()
        # mycursor.close()
        flash("Appointment is Booked Successfully!")

        #Synchronize with doctor's calendar
        #getting appointment id to add in events table
        sql = "SELECT id FROM Appointments WHERE drID =%s AND bookedTime =%s"
        val = (doctor_id, bookedTime)
        mycursor.execute(sql,val)
        a_id = mycursor.fetchone()
        #getting dr data
        doctor = next((doctor for doctor in myresult if doctor['ID'] == int(doctor_id)),False)
        doctor_email=doctor['Email']
        doctor_id=int(doctor_id)
        sql="SELECT * FROM Calendars WHERE drID = %s"
        mycursor.execute(sql,(doctor_id,))
        dr_cal = mycursor.fetchall()
        print(dr_cal)
        if not dr_cal:
            ID = g_api.create_calendar("Cardiology Department","Africa/Cairo")
            g_api.give_access(ID,doctor_email)
            sql="INSERT INTO Calendars (c_id,drID) VALUES (%s,%s)"
            val=(ID,doctor_id)
            print(val)
            mycursor.execute(sql,val)
            mydb.commit()
            mycursor.execute("SELECT * FROM Calendars WHERE drID = '%s'" %(doctor_id))
            dr_cal = mycursor.fetchone()
        event_id = g_api.create_event( bookedTime, dr_cal['c_id'])
        #insert event into Events table 
        sql="INSERT INTO Events (e_id,cal_id,a_id) VALUES (%s,%s,%s)"
        val=(event_id,dr_cal['c_id'],a_id['id'])
        mycursor.execute(sql,val)
        mydb.commit()
        print("EVENT CREATED")
        return render_template("p_book_appointment.html", doctorsData = myresult,  id_1_l=id_1_l )
    else:
        return render_template("p_book_appointment.html", doctorsData = myresult,  id_1_l=id_1_l )

@admin.route('/statistical')
def stat():
    mycursor = mydb.cursor(dictionary=True, buffered=True)
    mycursor.execute("SELECT * FROM Doctors")
    doctors=len(mycursor.fetchall())
    mycursor.execute("SELECT * FROM Patients")
    patients=len(mycursor.fetchall())
    x=["Solved_Requests", " Un_Solved_Requests"]
    sql= "SELECT * FROM ContactUsForms WHERE is_solved = %s"
    val_u=(0,)
    val_s=(1,)
    mycursor.execute(sql,val_u)
    unsolved=len(mycursor.fetchall())
    mycursor.execute(sql,val_s)
    solved=len(mycursor.fetchall())
    forms= [solved, unsolved]
    plt.style.use('ggplot')
    fig = plt.figure(figsize=(5, 5))
    plt.bar(x,forms, color="yellow")
    plt.savefig('./static/images/new_plot.png')

    ####
    mycursor = mydb.cursor(dictionary=True, buffered=True)
    plt.style.use('ggplot')
    fig = plt.figure(figsize=(5, 5))

    today = datetime.today()
    first = today.replace(day=1)
    last= first - timedelta(days=31)
    llast = last- timedelta(days=30)
    lllast = llast - timedelta(days=31)
    next= first + timedelta(days=30)

    x=[(first.strftime("%m/%Y")),(last.strftime("%m/%Y")),(llast.strftime("%m/%Y")),(lllast.strftime("%m/%Y"))]

    sql= "SELECT * FROM Appointments WHERE bookedTime >= %s And bookedTime < %s"
    val1=(first,next)
    val2=(last,first)
    val3=(llast,last)
    val4=(lllast,llast)
    mycursor.execute(sql,val1)
    app_this_month = len(mycursor.fetchall())

    mycursor.execute(sql,val2)
    app_last_month= len(mycursor.fetchall())

    mycursor.execute(sql,val3)
    app_llast_month= len(mycursor.fetchall())

    mycursor.execute(sql,val4)
    app_lllast_month= len(mycursor.fetchall())

    Appointments= [app_this_month,app_last_month,app_llast_month,app_lllast_month]
    ax = fig.add_subplot(1, 1, 1)

    plt.style.use('ggplot')
    fig = plt.figure(figsize=(5, 5))
    plt.bar(x,Appointments, color="yellow")
    plt.savefig('./static/images/new_plot2.png')

    return render_template("stat.html",patients=patients,doctors=doctors )


# @admin.route('/plot.png')
# def plot_png1():
#     fig = create_figure()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')

# def create_figure():
#     mycursor = mydb.cursor(dictionary=True, buffered=True)
#     plt.style.use('ggplot')
#     fig = plt.figure(figsize=(5, 5))

#     today = datetime.today()
#     first = today.replace(day=1)
#     last= first - timedelta(days=31)
#     llast = last- timedelta(days=30)
#     lllast = llast - timedelta(days=31)
#     next= first + timedelta(days=30)

#     x=[(first.strftime("%m/%Y")),(last.strftime("%m/%Y")),(llast.strftime("%m/%Y")),(lllast.strftime("%m/%Y"))]

#     sql= "SELECT * FROM Appointments WHERE bookedTime >= %s And bookedTime < %s"
#     val1=(first,next)
#     val2=(last,first)
#     val3=(llast,last)
#     val4=(lllast,llast)
#     mycursor.execute(sql,val1)
#     app_this_month = len(mycursor.fetchall())

#     mycursor.execute(sql,val2)
#     app_last_month= len(mycursor.fetchall())

#     mycursor.execute(sql,val3)
#     app_llast_month= len(mycursor.fetchall())

#     mycursor.execute(sql,val4)
#     app_lllast_month= len(mycursor.fetchall())

#     Appointments= [app_this_month,app_last_month,app_llast_month,app_lllast_month]
#     ax = fig.add_subplot(1, 1, 1)

#     ax.bar(x,Appointments , color="blue",)
#     ax.plot()
#     ax.set_title('Appointments in 4 months')
#     ax.set_xlabel('months')
#     ax.set_ylabel('Appointments Number')
#     ax.set_xticklabels(x)
#     return fig


# @admin.route('/msg_plot.png')
# def plot_png2():
#     fig = create_figure2()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')

# def create_figure2():
#     mycursor = mydb.cursor(dictionary=True, buffered=True)
#     plt.style.use('ggplot')
#     fig = plt.figure(figsize=(5, 5))

#     today = datetime.today()
#     first = today.replace(day=1)
#     last= first - timedelta(days=31)
#     llast = last- timedelta(days=30)
#     lllast = llast - timedelta(days=31)

#     x=[(first.strftime("%Y-%m")),(last.strftime("%Y-%m")),(llast.strftime("%Y-%m")),(lllast.strftime("%Y-%m"))]

# # "SELECT Min(id),questionID, msgTime FROM Messages GROUP BY questionID JOIN ContactUsForms ON questionID = id WHERE is_solved is NULL"    
#     sql= "SELECT Min(id) FROM Messages WHERE msgTime >= %s And msgTime < %s GROUP BY questionID "

#     val2=(last,first)
#     val3=(llast,last)
#     val4=(lllast,llast)

#     mycursor.execute(sql,val2)
#     q_last_month= len(mycursor.fetchall())

#     mycursor.execute(sql,val3)
#     q_llast_month= len(mycursor.fetchall())

#     mycursor.execute(sql,val4)
#     q_lllast_month= len(mycursor.fetchall())

#     Questions= [q_last_month,q_llast_month,q_lllast_month]
#     ax = fig.add_subplot(1, 1, 1)

#     ax.bar(x,Questions , color="green",)
#     ax.plot()
#     ax.set_title('Questions in last 3 months')
#     ax.set_xlabel('months')
#     ax.set_ylabel('Questions Number')
#     ax.set_xticklabels(x)
#     return fig
