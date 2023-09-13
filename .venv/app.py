from posixpath import split
from subprocess import check_output
from bson import ObjectId
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta , date
import os
import hashlib
import matplotlib.pyplot as plt
import numpy as np


import pymongo
import binascii
from db import database
from subprocess import Popen
from gevent.pywsgi import WSGIServer
import spacy
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
import inspect
import os
import PyPDF2
import pandas as pd
import re

# load default skills data base
from skillNer.general_params import SKILL_DB
# import skill extractor
from skillNer.skill_extractor_class import SkillExtractor
from  skillNer.matcher_class import SkillsGetter
from  skillNer.matcher_class import Matchers


# init params of skill extractor
import en_core_web_sm



app = Flask(__name__)

app.secret_key = "bonjour"

app.permanent_session_lifetime = timedelta(minutes=15)
nlp = en_core_web_sm.load()
    # init skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
db = database()
def extract_text_from_folder(folder_path, start_word, column_names, pdf_file_list):
    df = pd.DataFrame(columns=column_names)

    for filename in pdf_file_list:
        file_path = os.path.join(folder_path, filename)
        extracted_text = extract_text_from_pdf(file_path, start_word)
        df = df.append({'text': extracted_text, 'course': filename}, ignore_index=True)

    return df
def extract_text_from_pdf(file_path, start_word):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        extracted_text = ""

        for page in reader.pages:
            text = page.extract_text()
            start_index = text.find(start_word)
            if start_index != -1:
                extracted_text += text[start_index:]
            else:
                extracted_text += text

    return extracted_text




@app.route("/",methods=["POST","GET"])
def index():
    
  
    return render_template("index.html")

@app.route("/pb",methods=["POST","GET"])
def powerbi():
    
  
    return render_template("dashpb.html")




@app.route('/existing')
def exists():
    df=pd.read_excel('data_2.xlsx')
    client = pymongo.MongoClient("mongodb+srv://mohamedazizsouissi:07244341@cluster0.a51igi5.mongodb.net/?retryWrites=true&w=majority")
    db = client["edux"]  # Replace with your database name
    collection = db["data_fm"]  # Replace with your collection name

# Retrieve data from the collection
    cursor = collection.find({})
    df_fiche_module = pd.DataFrame(list(cursor))
    df_fiche_module = df_fiche_module[df_fiche_module['owner'] == session["user"]]
    # Assuming you have defined the 'df' and 'df_fiche_module' DataFrames
    
    # Find the common skill_names
    common_skill_names = pd.Series(list(set(df['skill_name']).intersection(set(df_fiche_module['skill_name']))))

    # Create a list to store the output
    output_list = []

    # Iterate over the course names in the second dataframe
    for course_name in df_fiche_module['Unnamed: 4'].unique():
        course_output = {
            'course_name': course_name,
            'matching_skills': []
        }
        matching_skills = df[df['course_unit'] == course_name]['skill_name']
        matching_skills = matching_skills[matching_skills.isin(common_skill_names)]

        if not matching_skills.empty:
            for skill in matching_skills.unique():
                skill_output = {
                    'skill_name': skill
                }
                course_output['matching_skills'].append(skill_output)
            output_list.append(course_output)
    print('aaaaaaaaaaaaaaaaaaa')
    print(output_list)

    return render_template('exists.html', output_list=output_list)







@app.route("/stat",methods=["POST","GET"])
def stat():
    df=pd.read_excel('data_2.xlsx')
    #df_fiche_module = pd.read_excel('data_fiche_ds_2.xlsx')
    client = pymongo.MongoClient("mongodb+srv://mohamedazizsouissi:07244341@cluster0.a51igi5.mongodb.net/?retryWrites=true&w=majority")
    db = client["edux"]  # Replace with your database name
    collection = db["data_fm"]  # Replace with your collection name

# Retrieve data from the collection
    cursor = collection.find({})
    df_fiche_module = pd.DataFrame(list(cursor))
    df_fiche_module = df_fiche_module[df_fiche_module['owner'] == session["user"]]

    # Find the common skill_names
    common_skill_names = pd.Series(list(set(df['skill_name']).intersection(set(df_fiche_module['skill_name']))))

# Create a list to store the output
    output_list = []

# Iterate over the course units in the second dataframe
    for course_unit in df_fiche_module['Unnamed: 4'].unique():

    # Skills in df that do not exist in df_fiche_module
        unmatched_skills = df[df['course_unit'] == course_unit]['skill_name']
        unmatched_skills = unmatched_skills[~unmatched_skills.isin(common_skill_names)]

        if not unmatched_skills.empty:
            course_output = {
            'course_unit': course_unit,
            'missing_skills': []
            }
            for skill in unmatched_skills.value_counts().head(7).index:
                skill_output = {
                'skill_name': skill,
                'frequency': df[df['skill_name'] == skill]['frequency'].values[0]  # Assuming there is only one frequency per skill in df
                }
                course_output['missing_skills'].append(skill_output)
        output_list.append(course_output)
    
  
    return render_template("stats.html",output_list=output_list)
@app.route("/colldata",methods=["POST","GET"])
def colldata():
    dd=[
    'Data science', 'Web Development']
    if request.method == "POST":
        category = request.form["sel"]
        if category == "Web Development":
            df=pd.read_excel('data_3_twin.xlsx')
        if category =="Data science":
            df=pd.read_excel('data_2.xlsx')
        return render_template("scrapdata.html",skill_name=df["skill_name"],freq=df["frequency"],course=df["course_unit"])

    return render_template("form_categ.html",dd=dd)





@app.route("/courbe",methods=["POST","GET"])
def aaaaa():
    df=pd.read_excel('data_2.xlsx')

    dd=[
    'Python (Programming Language)', 'Machine Learning','Deep Learning','Power BI','SQL (Programming Language)','R (Programming Language)','MongoDB','Apache Hive']
    if request.method == "POST":
        v = request.form["sel"]
        df=pd.read_excel('fff.xlsx')
        filtered_df = df[df['skills'] == v]

# Count the occurrences of each skill in the filtered DataFrame
        skill_counts = filtered_df['skills'].value_counts()

# Create a Series with the skill name and its count
        top_skills = pd.Series(skill_counts.iloc[0], index=[v])


# Filter the DataFrame to include only the rows with the top skills
        df_top_skills = df[df['skills'].isin(top_skills.index)]

# Convert first_year and last_year columns to integer
        df_top_skills['first_year'] = df_top_skills['first_year'].astype(int)
        df_top_skills['last_year'] = df_top_skills['last_year'].astype(int)

# Concatenate the 'first_year' and 'last_year' columns to form a single date column
        df_top_skills['date'] = df_top_skills['first_year'].astype(str) + ' - ' + df_top_skills['last_year'].astype(str)

# Create a list of years from the minimum first_year to the maximum last_year in the dataset
        years = np.arange(df_top_skills['first_year'].min(), df_top_skills['last_year'].max() + 1)

# Initialize a dictionary to store skill counts for each year
        skill_counts_by_year = {skill: np.zeros(len(years), dtype=int) for skill in top_skills.index}

# Calculate skill counts for each year
        for i, year in enumerate(years):
            for skill in top_skills.index:
                count = df_top_skills[(df_top_skills['first_year'] <= year) & (df_top_skills['last_year'] >= year) & (df_top_skills['skills'] == skill)].shape[0]
                skill_counts_by_year[skill][i] = count

# Plot the variation of each skill over the years
        plt.figure(figsize=(12, 6))  # Increase the figure size

        for skill in top_skills.index:
            plt.plot(years, skill_counts_by_year[skill], marker='o', label=skill)

# Customize the plot
        plt.xlabel('Year')
        plt.ylabel('Skill Count')
        plt.title('Variation of Top 20 Skills over the Years')
        plt.legend(loc='upper right')
        plt.grid(True)

# Set x-axis tick positions and labels
        plt.xticks(years)  # Set the tick positions
        plt.locator_params(axis='x', nbins=len(years))  # Set the number of tick labels

# Show the plot
        plt.show()



        
        return render_template("form_courbe.html",dd=dd)

    return render_template("form_courbe.html",dd=dd)





  

@app.route("/matching",methods=["POST","GET"])
def matching():
    client = pymongo.MongoClient("mongodb+srv://mohamedazizsouissi:07244341@cluster0.a51igi5.mongodb.net/?retryWrites=true&w=majority")
    db = client["edux"]  # Replace with your database name
    collection = db["data_fm"]  # Replace with your collection name

# Retrieve data from the collection
    cursor = collection.find({})
    df = pd.DataFrame(list(cursor))
    print(df["skill_name"])
    print(session["user"])

    
    df = df[df['owner'] == session["user"]]
    print(df["skill_name"])
    df = df.reset_index()
    

    return render_template("matching.html",course=df['course'],skill_name=df['skill_name'],categ=df['Unnamed: 4'],skill_type=df['skill_type'])






@app.route("/delete")
def delete():
    if "user" in session:
        user = session["user"]
        x=db.find("users",{"Username": user})
        db.delete(x,"users")

        

        flash("deleted successfully!")

    else:
        flash("Unable to delete record!")
    return redirect(url_for("logout"))


@app.route("/view")
def view():
    if "user" in session:
        x=db.view("users")
        
        return render_template("view.html", values=x)
        

    else: 
        flash("you must login first !!!")
        return redirect(url_for("login"))


    






@app.route("/signin", methods=["POST", "GET"])
def sign():
    if request.method == "POST":

        name = request.form["nm"]
       
        passwd = hash_pass(request.form["pw"])

        if name  and passwd:
            found_user = db.find("users",{"Username": name})
            if found_user:

                flash("Already signed up ! ")
                return redirect(url_for("login"))

            else:
                user = {"Username": name, "Password": passwd}
                db.insert(user,"users")

                flash("sign up Succesfull !")

                return redirect(url_for("login"))
        else:
            flash("there is something missing")
            return redirect(url_for("sign"))

    else:
        if "user" in session:
            flash("Already loged In !")
            return redirect(url_for("user"))
        return render_template("form.html")


@app.route("/main", methods=["POST", "GET"])
def main():
    
    dd=['Web Development', 'Data Visualization', 'Artificial Intelligence',
       'Financial Analysis', 'Database Administration',
       'Operations research', 'Cloud Computing', 'Project Management',
       'Mathematics and Probability']
   
    today=str(date.today())
    
    if "user" in session:
        user=session["user"]
        if request.method == "POST":
           files  = request.files.getlist('pdf_files')
           file_names = [file.filename for file in files]
           category = request.form["sel"]
           folder_path = 'C:/Users/MSi/Desktop/comp_based/OptionDS'
           start_word = 'Acquis d’apprentissage'
           column_names = ['text', 'course', 'Unnamed: 4']

           result_df = extract_text_from_folder(folder_path, start_word, column_names,file_names)
           result_df['Unnamed: 4'] = category

           print(result_df)
           result_df['text'] = result_df['text'].apply(lambda x: re.sub('\t','', x))
           result_df['text'] = result_df['text'].apply(lambda x: re.sub('\uf02d',' ', x))
           result_df['text'] = result_df['text'].apply(lambda x: re.sub('\n',' ', x))

           result_df['text'] = result_df['text'].apply(lambda x: re.sub(']','', x))
           html = re.compile(r"<*?X>|&([a-z0-9]+|[0-9]{1,6}|x[0-9a-f]{1,6});")
           result_df['text'] = result_df['text'].apply(lambda x: re.sub(html,' ', x))
           special_chars = r"[*\/\[\]\(\)\?:;.&%,X'']"
           #result_df['text'] = result_df['text'].str.replace(special_chars, '')
           data_frames = []
           for i in range(len(result_df)):
            annotations = skill_extractor.annotate(result_df['text'][i])
            data = skill_extractor.describe(annotations)
            print(type(data))
            print('aaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
            data['Unnamed: 4']=result_df['Unnamed: 4'][i]
            data['course']=result_df['course'][i]
            data_frames.append(data)
           final_data = pd.concat(data_frames)
           final_data.drop_duplicates(subset=['skill_name', 'course'], inplace=True)  
           final_data["owner"]=session["user"]





           documents = final_data.to_dict(orient='records')
           client = pymongo.MongoClient("mongodb+srv://mohamedazizsouissi:07244341@cluster0.a51igi5.mongodb.net/?retryWrites=true&w=majority")
           db = client["edux"]  # Replace with your database name
           collection = db["data_fm"]
           collection.insert_many(documents)
           
           


    
           
           
           return render_template("work.html",dd=dd)
        else:
            return render_template("work.html",dd=dd)
    else:
        flash("You must login first !!!")
        return redirect(url_for("login"))




@app.route("/login", methods=["POST", "GET"])
def login():
    session.permanent = True
    if request.method == "POST":
        name = request.form["nnmm"]
        password = request.form["pww"]
        found_user = db.find("users",{"Username": name})

        if found_user:
            if verify_pass(password, found_user["Password"]):
                session["user"] = name
                
                flash("Login Succesfull !")
                return redirect(url_for("user"))
            else:
                flash("wrong password")
                return redirect(url_for("login"))

        else:
            flash("you must sign in first")
            return redirect(url_for("sign"))
    else:
        if "user" in session:
            flash("Already Logged In !")
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user", methods=["POST", "GET"])
def user():
    name = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            name = request.form["name"]
            pwd = request.form["pwd"]
            
            if name:
                session["user"] = name
                db.update("$set",{"Username":user},{"Username": name},"users")
                user=name
            if pwd :
                pw=hash_pass(pwd)
                db.update("$set",{"Username":user},{"Password": pw},"users")

            flash("Your Username was saved")
            
        

        return render_template("user.html", user=user)
    else:
        flash("You must login")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"you have been logged out ! {user} ", "info")
        session.pop("user", None)
        
        return redirect(url_for("login"))
    else:
        flash("you are not logged in")
        return redirect(url_for("login"))

def hash_pass(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash)


def verify_pass(provided_password, stored_password):
    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode(
        'utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()

    #app.run(debug=True)
