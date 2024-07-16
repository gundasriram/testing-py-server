
import boto3
from services.db.db_connection import get_db_connection, updateTaskStatusforCallId, getOneAnalysis, getAllPendingTask
from services.analysis import callAnalysis
import concurrent.futures

def checkTaskStatus(call_id, db):
    res = getOneAnalysis(db, call_id)
    if res['task_status'] == 'INPROGRESS':
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
        # Function to process a single call
        def process_call(call):
            db = get_db_connection()
            print('call', call)
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
        # Use ThreadPoolExecutor to run calls in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Group pending calls in pairs of two
            for i in range(0, len(pending_call_analysis), 2):
                calls_to_process = pending_call_analysis[i:i+2]
                # Submit tasks to the executor
                futures = [executor.submit(process_call, call) for call in calls_to_process]
                # Wait for the futures to complete
                concurrent.futures.wait(futures)
        db.close()
    except Exception as e:
        db.close()
        print('Error in callAnalysis init :::', e)
        raise Exception(f"Error in callAnalysis init: {e}")

init()
