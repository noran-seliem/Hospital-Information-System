import mysql.connector , os
from flask import Flask, render_template , request,abort, session , redirect , url_for ,flash
from werkzeug.utils import secure_filename
from auto_bp import auto , auto_2, auto_3
from patient import patient
from doctor import doctor
from admin import admin
from database import mydb
import datetime
import g_api

mycursor = mydb.cursor(dictionary=True, buffered=True)



app= Flask(__name__)
app.secret_key = 'your secret key'

#bluprints
app.register_blueprint(patient, url_prefix="/p")
app.register_blueprint(doctor, url_prefix="/d")
app.register_blueprint(auto, url_prefix='/browse/prescriptions')
app.register_blueprint(auto_2, url_prefix='/browse/scans')
app.register_blueprint(auto_3, url_prefix='/browse/reports')
app.register_blueprint(admin, url_prefix="/A")


app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.gif','.txt','.pdf','.jpeg','.gif','.csv','.eps','.bmp','.raw','.xml','.doc','.docs','.xls']
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 2592000
app.config['UPLOAD_PATH'] = './static/uploads'



@app.route('/')
@app.route('/home')
def home():
   return render_template("Test_home.html")   

@app.route('/upload',methods=['GET','POST'])
def upload_files():
   if request.method == 'POST':
      for uploaded_file in request.files.getlist("prescription"):
         p_id=request.form['p_id1']
         if not p_id:
            flash("Patient ID Cannot be empty")
            return render_template('files.html')
         filename = secure_filename(uploaded_file.filename)
         if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
               abort(400)
            #filename = '/prescriptions/'+filename
            #constructing substring of patient_id
            if file_ext in ['.jpg','.png','.gif','.jpeg','.gif']:
               filename=p_id+"-+-"+filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH']+'/prescriptions/', filename))
            flash("done uploading successfully")
         else:
               flash("something wrong!")
      for uploaded_file in request.files.getlist("scan"):
         p_id=request.form['p_id2']
         if not p_id:
            flash("Patient ID Cannot be empty")
            return render_template('files.html')
         filename = secure_filename(uploaded_file.filename)
         if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
               abort(400)
            #filename = '/scans/'+filename
            #constructing substring of patient_id
            if file_ext in ['.jpg','.png','.gif','jpeg','gif']:
               filename=p_id+"-+-"+filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH']+'/scans/', filename))
            flash("done uploading successfully")
         else:
               flash("something wrong!")
      for uploaded_file in request.files.getlist("report"):
         p_id=request.form['p_id3']
         if not p_id:
            flash("Patient ID Cannot be empty")
            return render_template('files.html')
         filename = secure_filename(uploaded_file.filename)
         if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
               abort(400)
            #filename = '/reports/'+filename
            #constructing substring of patient_id
            if file_ext in ['.jpg','.png','.gif','jpeg','gif']:
               filename=p_id+"-+-"+filename
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH']+'/reports/', filename))
            flash("done uploading successfully")
         else:
               flash("something wrong!")
      return render_template('files.html')
   else:
      return render_template('files.html')




@app.route('/upcoming_app',methods=['GET','POST'])
def upcoming_app():
   mydb.commit()
   now = datetime.datetime.now()
   if session['msg']=='A':
      sql = 'SELECT * FROM Patients AS T1 JOIN ( SELECT a.id , bookedTime, drID,patID, d.ID AS d_id , Name AS dname, Birthday AS dbday , Email AS demail , Phone AS dphone FROM Appointments AS a JOIN Doctors AS d on drID = d.ID WHERE bookedTime >= %s ) AS T2 ON T1.ID = T2.patID'
      val=(now,)
      # mycursor.close()
   elif session['msg']=='p':
      sql = 'SELECT a.id , bookedTime, drID ,patID, name AS dname FROM Appointments AS a JOIN Doctors on a.drID = Doctors.ID WHERE bookedTime >= %s AND patID = %s'
      val=(now,session['u_id'])
      # print("HHHHHHHHHHHH")
      # mycursor.close()
   else:
      sql = 'SELECT * FROM Appointments JOIN Patients on Appointments.patID = Patients.ID WHERE bookedTime >= %s AND drID = %s'
      val=(now,session['u_id'])
      # mycursor.close()
   mycursor.execute(sql,val)
   data = mycursor.fetchall()
   # print(data)
   return render_template("upcoming_appointments.html",data=data)

@app.route('/delApp/<int:id_data>',methods=['GET'])
def delApp(id_data):
   sql="SELECT * FROM Events WHERE a_id = %s"
   val=(id_data,)
   mycursor.execute(sql,val)
   Event=mycursor.fetchone()
   print(Event)
   g_api.delete_event(Event['cal_id'],Event['e_id'])
   sql = "DELETE FROM Events WHERE a_id = %s "
   val=(id_data,)
   mycursor.execute(sql,val)
   mydb.commit()
   sql ='DELETE FROM Appointments WHERE id=%s'
   val=(id_data,)
   mycursor.execute(sql,val)
   mydb.commit()
   return redirect(url_for("upcoming_app"))



@app.route('/logout')
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"you have been logged out!{user}")
    #Remove session data
    session.clear()
    #Redirect to home page
    return redirect(url_for('home'))

if __name__ == '__main__':
   app.run()
