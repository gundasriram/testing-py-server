import boto3
from services.db.db_connection import get_db_connection, updateTaskStatusforCallId, getOneAnalysis, getAllPendingTask
from services.analysis import callAnalysis

def checkTaskStatus(call_id, db):
    res = getOneAnalysis(db, call_id)
    if res['task_status'] != 'PENDING':
        return False
    else:
        return True

def init():
    print('*************** CALL ANALYSIS INIT ***************')
    try:
        db = get_db_connection()
        pending_call_analysis = getAllPendingTask(db)
        print('*************** Pending Calls START ***************')
        print(pending_call_analysis)
        print('*************** Pending Calls END***************')
        for call in pending_call_analysis:
            try:
                print('call', call)
                file = call['s3_file_path']
                call_id = call['call_id']
                print('*************** Started Process for Call_id :::', call_id)
                taskStatus = checkTaskStatus(call_id, db)
                print('*************** taskStatus :::', taskStatus)
                if(taskStatus):
                    updateTaskStatusforCallId(db, 'INPROGRESS', call_id)
                    print('*************** Making Call to CallAnalysis with File and Call data ***************')
                    callAnalysis(file, call, db)
            except Exception as e:
                print('Error in loop of pending task for init :::', e)
                print('Error in loop for call_id', call_id)
                updateTaskStatusforCallId(db, 'FAILED', call_id)
                # raise Exception(f"Error in callAnalysis init: {e}")
        db.close()
    except Exception as e:
        print('Error in callAnalysis init :::', e)
        raise Exception(f"Error in callAnalysis init: {e}")

init()
