from flask import Blueprint , render_template , session ,redirect,url_for ,flash,request
import mysql.connector
import datetime , re 
from database import mydb

doctor = Blueprint("doctor",__name__ , static_folder="static" , template_folder = "templates")


@doctor.route('/dashboard')
def doctorDash():
   return render_template("dashboard.html")



@doctor.route('/login',methods=['GET','POST'])
def d_login():
   #check if user submitted login form (POST) 
   mycursor = mydb.cursor(dictionary=True, buffered=True)
   if request.method == 'POST':
      if 'loggedin' in session:
         session.clear()
         flash("Logout First")
         return render_template("SignIn.html")
      email = request.form['email']
      password = request.form['password']
      #check if user exists in the database
      sql = 'SELECT * FROM Doctors WHERE Email = %s AND Password = %s'
      val = (email, password)
      mycursor.execute(sql, val)
      # Fetch user's record
      account = mycursor.fetchone()
      ##print("11")
      #check if account exists in the database
      if account:
         #create session data
         session['loggedin'] = True
         session['u_id'] = account['ID']
         session['email'] = account['Email']
         session['user']=account['Name']
         session['msg']='d'
         #print(session['username'])
         #msg = f"{session['user']},signed in successfully!"
         flash(f"you have been logged successfully, {session['user']}")
         return redirect(url_for('doctor.doctorDash'))
      else:
         #if account doesnt exist or email/password incorrect
         flash("Your email or password were incorrect")
         return render_template('SignIn.html')
   else:
      return render_template('SignIn.html')

# view profile
@doctor.route('/profile', methods=['GET', 'POST'])
def display_profile():
    mycursor = mydb.cursor()
    d_id = session['u_id']
    # d_id = 1
    sql = 'SELECT * FROM Doctors WHERE ID =%s'
    val = (d_id,)
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
@doctor.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    mycursor = mydb.cursor()
    d_id = session['u_id']
    if request.method == 'GET':
        sql = 'SELECT * FROM Doctors WHERE ID =%s'
        val = (d_id,)
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
            # dep = request.form['DepartmentID']
            try:
                # print(name, email, phone, ssn, bday, d_id)
                mycursor.execute("UPDATE Doctors SET Name = '%s', Gender = '%s', Email = '%s', Phone = '%s', SSN = '%s', Birthday = '%s' WHERE id = '%s'" % (name,gender, email, phone, ssn, bdate, d_id))
                mydb.commit()
                flash("Profile updated successfully!", "info")
            except:
                flash("Something went wrong!", "error")

        elif 'change' in request.form: #for changing password
            old_pw = request.form['password']
            mycursor.execute("SELECT Password FROM Doctors where ID = '%s'" %(d_id))
            myresult = mycursor.fetchone()
            pw = myresult[0]
        #   print(pw, old_pw)
            if pw == old_pw:
                new_pw = request.form['newpassword']
                mycursor.execute("UPDATE Doctors SET Password = '%s' WHERE ID = '%s'" % (new_pw, d_id))
                mydb.commit()
                flash("Password changed successfully!", "info")
            else:
                flash("Incorrect password!", "error")
        return redirect(url_for('doctor.display_profile'))
