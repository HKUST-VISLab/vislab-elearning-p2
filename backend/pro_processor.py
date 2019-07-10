import json
import os,sys
import dev_processor
from pathlib import Path

def _getUserSequenceByUidPid(problemid, userid):
    if Path("./cache/" + problemid+"/" + userid).exists():
        with open("./cache/" + problemid+"/" + userid, "r") as f:
            return f.readline()
    else:
        return dev_processor._getUserSequenceByUidPid(problemid, userid)

def _getProblemSequence(problemid):
    if Path("./cache/" + problemid+"/problemsequence").exists():
        with open("./cache/" + problemid+"/problemsequence", "r") as f:
            return f.readline()
    else:
        return dev_processor._getProblemSequence(problemid)

def _getUserSequenceByProblem(problemid):
    if Path("./cache/" + problemid+"/userproblemsequence").exists():
        with open("./cache/" + problemid+"/userproblemsequence", "r") as f:
            return f.readline()
    else:
        return dev_processor._getUserSequenceByProblem(problemid)

def _getProblemInfomation(problemid, num):
    if Path("./cache/" + problemid+"/problemdetails").exists():
        with open("./cache/" + problemid+"/problemdetails", "r") as f:
            return f.readline()
    else:
        return dev_processor._getProblemInfomation(problemid, num)

def _getUserClustersByProblem(problemid):
        return ""

def _getImpotantArea(problemid):
    if Path("./cache/" + problemid+"/tmp").exists():
        with open("./cache/" + problemid + "/tmp", "r") as f:
            return f.readline()
    else:
        return str({})