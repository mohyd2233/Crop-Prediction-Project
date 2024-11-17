from flask import Flask, render_template, jsonify, request
import pickle as pkl
import sqlite3 as sql

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/prediction',methods = ['GET','POST'])
def prediction():
    if request.method=='POST':
        nitro = request.form.get('nitrogen')
        phos = request.form.get('phosphorus')
        pott = request.form.get('potassium')
        temp = request.form.get('temperature')
        hum = request.form.get('humidity')
        ph = request.form.get('ph')
        rf = request.form.get('rainfall')
        print(nitro,phos,pott,temp,hum,ph,rf)
        with open('model.pkl','rb') as model_file:
            mlmodel = pkl.load(model_file)
        res = mlmodel.predict([[float(nitro),float(phos),float(pott),float(temp),float(hum),float(ph),float(rf)]])
        conn = sql.connect('cropdata.db')
        cur = conn.cursor()
        cur.execute(f''' INSERT INTO CROP VALUES({nitro},{phos},{pott},{temp},{hum},{ph},{rf},'{res[0]}')''')
        conn.commit()
        return render_template("result.html",res=res[0])
    else:
        return render_template('/prediction.html')


@app.route('/showdata',methods = ['GET','POST'])
def showdata():
    conn = sql.connect('cropdata.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM CROP")
    x = cur.fetchall()

    lst = []
    for i in x:
        dict1 = {}
        dict1['Nitrogen']=i[0]
        dict1['Phosphorus']=i[1]
        dict1['Potassium']=i[2]
        dict1['Temparature']=i[3]
        dict1['Humidity']=i[4]
        dict1['Ph']=i[5]
        dict1['Rainfall']=i[6]
        dict1['Result']=i[7]
        lst.append(dict1)

    return render_template('showdata.html',data = lst)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 5050)
