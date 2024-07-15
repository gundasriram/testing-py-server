
import boto3
from services.db.db_connection import db
from services.analysis import callAnalysis

def checkTaskStatus(call_id):
    res = db.getOneAnalysis(call_id)
    if data['task_status'] == 'INPROGRESS':
        return False
    else:
        return True

def init():
    print('*************** CALL ANALYSIS INIT ***************')
    try:
        db.connect()
        pending_call_analysis = db.getAllPendingTask()
        print('*************** Pending Calls START ***************')
        print(pending_call_analysis)
        print('pending_call_analysis type ::', type(pending_call_analysis))
        print('*************** Pending Calls END***************')
        for call in pending_call_analysis:
            print('type of call', type(call))
            print('call', call)
            file = call['s3_file_path']
            call_id = call['call_id']
            print('*************** Started Process for Call_id :::', call_id)
            taskStatus = checkTaskStatus(call_id)
            print('*************** taskStatus :::', taskStatus)
            if(taskStatus):
                db.updateTaskStatusforCallId('INPROGRESS', call_id)
                print('*************** Making Call to CallAnalysis with File and Call data ***************')
                callAnalysis(file, call)
        db.close()
    except Exception as e:
        print('Error in callAnalysis init :::', e)
        raise Exception(f"Error in callAnalysis init: {e}")

init()
