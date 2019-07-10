from flask import Flask
import json
from flask_cors import CORS
from flask import request
import os,sys
import databaseapi
import readdata
import dev_processor
import pro_processor

app = Flask(__name__, static_url_path='')
app._static_folder = "static"
CORS(app)
DEV_MODE = False

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/usersequencebyuidpid',methods=['GET'])
def getOneSequence():
    problemid = request.args["pid"]
    userid = request.args["uid"]
    if DEV_MODE:
        return dev_processor._getUserSequenceByUidPid(problemid, userid)
    else:
        return pro_processor._getUserSequenceByUidPid(problemid, userid)

@app.route('/problemsequence',methods=['GET'])
def getProblemSequence():
    problemid = request.args["pid"]
    if DEV_MODE:
        return dev_processor._getProblemSequence(problemid)
    else:
        return pro_processor._getProblemSequence(problemid)

@app.route('/setimportantarea', methods=['POST'])
def setImportantArea():
    problemid = request.args["pid"]
    result = json.loads(request.data)
    dev_processor._setImportantArea(problemid,result)
    return "true"

@app.route('/getimportantarea', methods=['GET'])
def getImportantArea():
    problemid = request.args["pid"]
    return pro_processor._getImpotantArea(problemid)

@app.route('/usersequencebyproblem',methods=['GET'])
def getUserSequenceByProblem():
    problemid = request.args["pid"]
    if DEV_MODE:
        return dev_processor._getUserSequenceByProblem(problemid)
    else:
        return pro_processor._getUserSequenceByProblem(problemid)

@app.route('/userclustersbyproblem',methods=['GET'])
def getUserClustersByProblem():
    problemid = request.args["pid"]
    if DEV_MODE:
        return dev_processor._getUserClustersByProblem(problemid)
    else:
        return pro_processor._getUserClustersByProblem(problemid)

@app.route('/problemdetails',methods=['GET'])
def getProblemDetails():
    problemid = request.args["pid"]
    if DEV_MODE:
        return dev_processor._getProblemInfomation(problemid, 1000)
    else:
        return pro_processor._getProblemInfomation(problemid, 1000)

if __name__ == '__main__':
    app.run(host='0.0.0.0')