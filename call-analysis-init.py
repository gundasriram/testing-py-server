import boto3
from services.db.db_connection import get_db_connection, updateTaskStatusforCallId, getOneAnalysis, getAllPendingTask
from services.analysis import callAnalysis
import concurrent.futures

def checkTaskStatus(call_id, db):
    res = getOneAnalysis(db, call_id)
    return res['task_status'] != 'INPROGRESS'

def process_call(call):
    db = get_db_connection()
    file = call['s3_file_path']
    call_id = call['call_id']
    print('*************** Started Process for Call_id :::', call_id)
    taskStatus = checkTaskStatus(call_id, db)
    print('*************** taskStatus :::', taskStatus)
    if taskStatus:
        updateTaskStatusforCallId(db, 'INPROGRESS', call_id)
        print('*************** Making Call to CallAnalysis with File and Call data ***************')
        callAnalysis(file, call, db)
    db.close()

def init():
    print('*************** CALL ANALYSIS INIT ***************')
    try:
        db = get_db_connection()
        pending_call_analysis = getAllPendingTask(db)
        print('*************** Pending Calls START ***************')
        print(pending_call_analysis)
        print('*************** Pending Calls END***************')
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            future_to_call = {executor.submit(process_call, call): call for call in pending_call_analysis}
            for future in concurrent.futures.as_completed(future_to_call):
                call = future_to_call[future]
                try:
                    future.result()
                except Exception as e:
                    print(f'Call analysis generated an exception for call {call["call_id"]}: {e}')
        db.close()
    except Exception as e:
        print('Error in callAnalysis init :::', e)
        raise Exception(f"Error in callAnalysis init: {e}")
init()
