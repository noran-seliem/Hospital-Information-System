from flask import Blueprint , render_template , session ,redirect,url_for ,flash,request, send_from_directory
import re ,math , random
import mysql.connector, os
from database import mydb
from datetime import datetime
import g_api
import time 

patient = Blueprint("patient",__name__ , static_folder="static" , template_folder = "templates")
def convert (x):
   if x:
      return 'yes'
   else:
      return 'no'

mycursor = mydb.cursor(dictionary=True, buffered=True)



@patient.route('/register',methods=['GET','POST'])
def register():

   #check if user submitted form (POST)
   if request.method == 'POST':
         firstName = request.form['fname']
         lastName = request.form['lname']
         ssn = request.form['ssn']
         job = request.form['job']
         bdate = request.form['dob']
         sex = request.form['gender']
         bloodType = request.form['bt']
         weight = request.form['weight']
         phone = request.form['phone']
         hyperTension = convert('hyperTension' in request.form)
         ht_controlled = convert('ht_controlled' in request.form)
         diabetes = convert('diabetes' in request.form)
         diabetes_control = convert('dcontrol' in request.form)
         heartstroke = convert('heartstroke' in request.form)
         cholesterol = convert('ch' in request.form)
         email = request.form['email']
         password = request.form['pw'] 
         today = time.strftime('%Y-%m-%d')
         #check if account exists already
         sql = 'SELECT * FROM Patients WHERE email = %s'
         val = (email,)
         mycursor.execute(sql, val)
         # Fetch user's record
         account = mycursor.fetchone()
         # If account exists show error and validation checks
         if account:
            flash('Account already exists!')
            return render_template('SignIn_p.html')
         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
            return render_template('Test_home.html')
         elif not email or not password or not firstName or not ssn or not bloodType:
            flash('Fill out the Registration Form!')
            return render_template('Test_home.html')
         else:
            format_str = '%d/%m/%Y' # The format
            bday_datetime = datetime.strptime(bdate, format_str)
            #registration succed, create patient account
            Name = firstName + " " + lastName
            sql_ ='INSERT INTO Patients (Name,Birthday, Job, Email, Password, Phone, Gender, SSN , BloodType,Weight,Hypertension,ControlledHypertension,Diabetic,ControlledDiabetes,HeartStroke,Cholesterol, Join_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            val_ = (Name,bday_datetime,job,email,password,phone,sex,ssn,bloodType,weight,hyperTension,ht_controlled,diabetes,diabetes_control,heartstroke,cholesterol,today)
            mycursor.execute(sql_ , val_)
            mydb.commit()
            sql = 'SELECT id FROM Patients WHERE Email = %s AND Password = %s'
            val = (email, password)
            mycursor.execute(sql, val)
            # Fetch user's record
            account = mycursor.fetchone()
            session['loggedin'] = True
            session['user'] = Name
            session['u_id'] = account['id']
            session['email'] = email
            session['msg']='p'
            flash(f"you have been Registered successfully!,{Name}")
            return redirect(url_for('patient.patientDash'))
   else:
      return render_template('SignUp.html')


@patient.route('/login',methods=['GET','POST'])
def p_login():
   #check if user submitted login form (POST) 
   if request.method == 'POST':
      if 'loggedin' in session:
         session.clear()
         flash("Logout First")
         return render_template("SignIn_p.html")
      email = request.form['email']
      password = request.form['password']
      #check if user exists in the database
      sql = 'SELECT * FROM Patients WHERE Email = %s AND Password = %s'
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
         session['msg']='p'
         #print(session['username'])
         #msg = f"{session['user']},signed in successfully!"
         flash(f"you have been logged successfully, {session['user']}")
         return redirect(url_for('patient.patientDash'))
      else:
         #if account doesnt exist or email/password incorrect
         flash("Your email or password were incorrect")
         return render_template('SignIn_p.html')
   else:
      return render_template('SignIn_p.html')


@patient.route('/dashboard')
def patientDash():
   return render_template("dashboard.html")


# view profile
@patient.route('/profile', methods=['GET', 'POST'])
def display_profile():
    mycursor = mydb.cursor()
   #  p_id = session['u_id']
    p_id = session['u_id']
    sql = 'SELECT * FROM Patients WHERE ID =%s'
    val = (p_id,)
    #Fetch user's record
    mycursor.execute(sql,val)
    row_headers = [x[0] for x in mycursor.description]
    myresult = mycursor.fetchone()
    if request.method == 'GET':
        return render_template("profile.html", type=type, allData=zip(row_headers, myresult), view=1)
    else:
        if 'edit' in request.form:  # requesting the edit form
            return render_template("profile.html", type=type, allData=zip(row_headers, myresult), edit=1)
        elif 'change' in request.form: # requesting to change password
            return render_template("profile.html", type=type, allData=zip(row_headers, myresult), change=1)
        else:
            flash("Bad request", "error")
            return render_template("profile.html", type=type, allData=zip(row_headers, myresult), view=1)



# edit profile
@patient.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    mycursor = mydb.cursor()
    p_id = session['u_id']
    if request.method == 'GET':
      sql = 'SELECT * FROM Patients WHERE ID =%s'
      val = (p_id,)
      #Fetch user's record
      mycursor.execute(sql,val)
      row_headers = [x[0] for x in mycursor.description]
      myresult = mycursor.fetchone()
      return render_template("profile.html", type=type, allData=zip(row_headers, myresult), edit=1)
      
    else: 
      if 'edit' in request.form:
         name = request.form['Name']
         gender = request.form['Gender']
         email = request.form['Email']
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
            # print(name, email, phone, ssn, bday, p_id)
            sql = "UPDATE Patients SET Name = %s, Gender = %s, Email = %s, Phone = %s, SSN = %s, Birthday = %s, Job = %s, BloodType = %s, Weight = %s, Height = %s, Hypertension = %s, ControlledHypertension = %s, Diabetic = %s, ControlledDiabetes = %s, HeartStroke = %s, Cholesterol = %s WHERE ID = %s"
            val = (name, gender, email, phone, ssn, bdate, job, bloodtype, weight, height, hyper, hypercont,diabetic, diacont, stroke, cholesterol, p_id)
            mycursor.execute(sql, val)
            mydb.commit()
            flash("Profile updated successfully!", "info")
         except:
            flash("Something went wrong!", "error")

      elif 'change' in request.form: #for changing password
         old_pw = request.form['password']
         mycursor.execute("SELECT Password FROM Patients where id = '%s'" %(p_id))
         myresult = mycursor.fetchone()
         pw = myresult[0]
         #   print(pw, old_pw)
         if pw == old_pw:
               new_pw = request.form['newpassword']
               mycursor.execute("UPDATE Doctors SET Password = '%s' WHERE id = '%s'" % (new_pw, p_id))
               mydb.commit()
               flash("Password changed successfully!", "info")
         else:
               flash("Incorrect password!", "error")
      return redirect(url_for('patient.display_profile'))

@patient.route('/bookAppointment', methods=['GET','POST'])
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
      val = (doctor_id, bookedTime, id)
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
      dr_cal = mycursor.fetchone()
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



@patient.route('/contact_us', methods=['GET','POST'])
def contactus():
   if request.method=='POST':
      patid = session["u_id"] 
      subject = request.form['subject']
      msg = request.form['msg']

      sql = "INSERT INTO ContactUsForms (patID, subject) VALUES (%s,%s)"
      val = (patid,subject)
      mycursor.execute(sql, val)

      # get this question id to insert as foreign key in the messages table
      question_id = mycursor.lastrowid

      sql = "INSERT INTO Messages (msgTime, questionID, sender, msg) VALUES (%s,%s,%s,%s)"
      msgtime = datetime.now()
      val = (msgtime, question_id, 'p',msg)
      mycursor.execute(sql, val)
      mydb.commit()
      flash("Thanks for submitting, we well contact you as soon as possible!")            
   return render_template("contactus.html")



# view this patient questions and responses from admins
@patient.route('/messages')
def msg():
   patid = session["u_id"] 
   sql = "SELECT id, subject FROM ContactUsForms WHERE patid = %s AND is_solved IS NULL"
   val = (patid,)
   mycursor.execute(sql, val)
   unsolved = mycursor.fetchall()

   sql = "SELECT id, subject FROM ContactUsForms WHERE patid = %s AND is_solved IS NOT NULL"
   val = (patid,)
   mycursor.execute(sql, val)
   solved = mycursor.fetchall()
   return render_template("all_questions.html", unsolved=unsolved, solved=solved) 


@patient.route('/unsolved/<Qid>', methods=['GET', 'POST'])
def unsolved(Qid):
    if request.method == 'GET':
        mycursor.execute("SELECT msgTime, sender, msg FROM Messages WHERE questionID = %s" %(Qid))
        messages = mycursor.fetchall()
        mycursor.execute("SELECT id, subject FROM ContactUsForms WHERE id = %s" %(Qid))
        msg = mycursor.fetchone()
        return render_template("question_thread.html", messages=messages,msg=msg, unsolved=1)
    else:
       if 'send' in request.form:
          msg = request.form['msg']
          sql = "INSERT INTO Messages (msgTime, questionID, sender, msg) VALUES (%s,%s,%s,%s)"
          msgtime = datetime.now()
          val = (msgtime, Qid, 'p', msg)
          mycursor.execute(sql,val)
          mydb.commit()
          return redirect(url_for('patient.unsolved', Qid=Qid))

       elif 'solved' in request.form:
          mycursor.execute("UPDATE ContactUsForms SET is_solved = 1 WHERE id = %s" %(Qid))
          mydb.commit()
          return redirect(url_for('patient.msg'))


@patient.route('/solved/<Qid>')
def solved(Qid):
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT msgTime, sender, msg FROM Messages WHERE questionID = %s" %(Qid))
    messages = mycursor.fetchall()
    mycursor.execute("SELECT id, subject FROM ContactUsForms WHERE id = %s" %(Qid))
    msg = mycursor.fetchone()
    return render_template("question_thread.html", messages=messages,msg=msg)


@patient.route('/view/<T>')
def view_data (T):
   if T == 'Prescriptions':
      image_names = os.listdir('./static/uploads/prescriptions')
   elif T=='Scans':
      image_names = os.listdir('./static/uploads/scans')
   else:
      image_names = os.listdir('./static/uploads/reports')
   return render_template("patient_view.html", image_names=image_names,u=str(session['u_id']),T=T)

@patient.route('/presc/<image_name>')
def display_p(image_name):
   return send_from_directory('./static/uploads/prescriptions', image_name)

@patient.route('/scans/<image_name>')
def display_s(image_name):
   return send_from_directory('./static/uploads/scans', image_name)

@patient.route('/reports/<image_name>')
def display_r(image_name):
   return send_from_directory('./static/uploads/reports', image_name)


