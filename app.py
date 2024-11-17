from flask import Flask, render_template, jsonify, request
import pickle
import psycopg2  # PostgreSQL library for Python
import os

app = Flask(__name__)

# Use your PostgreSQL connection URL from Railway
DATABASE_URL = "postgresql://postgres:sbDVQXkpAdraxnoPUXMKouKmzUoyPmNZ@junction.proxy.rlwy.net:44338/railway"
DATABASE_URL = os.getenv("DATABASE_URL")

# Function to create a new database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        # Get input data from the form
        nitro = request.form.get('nitrogen')
        phos = request.form.get('phosphorus')
        pott = request.form.get('potassium')
        temp = request.form.get('temperature')
        hum = request.form.get('humidity')
        ph = request.form.get('ph')
        rf = request.form.get('rainfall')
        print(nitro, phos, pott, temp, hum, ph, rf)

        # Load the machine learning model
        with open('model.pkl', 'rb') as model_file:
            mlmodel = pickle.load(model_file)

        # Make a prediction
        result = mlmodel.predict([[float(nitro), float(phos), float(pott), float(temp), float(hum), float(ph), float(rf)]])
        
        # Connect to PostgreSQL database and insert data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO CROP (Nitrogen, Phosphorus, Potassium, Temperature, Humidity, Ph, Rainfall, Result) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                    (nitro, phos, pott, temp, hum, ph, rf, result[0]))
        
        # Commit and close the connection
        conn.commit()
        cur.close()
        conn.close()
        
        # Display the result on the result page
        return render_template('result.html', result=result[0])
    else:
        return render_template('prediction.html')

@app.route('/showdata', methods=['GET', 'POST'])
def showdata():
    # Connect to PostgreSQL database and retrieve data
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM CROP")
    x = cur.fetchall()
    
    cur.close()
    conn.close()

    # Format data for displaying
    lst = []
    for i in x:
        dict1 = {}
        dict1['Nitrogen'] = i[0]
        dict1['Phosphorus'] = i[1]
        dict1['Potassium'] = i[2]
        dict1['Temparature'] = i[3]
        dict1['Humidity'] = i[4]
        dict1['Ph'] = i[5]
        dict1['Rainfall'] = i[6]
        dict1['Result'] = i[7]
        lst.append(dict1)

    # Show the data on the showdata page
    return render_template('showdata.html', data=lst)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
