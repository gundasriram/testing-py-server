import boto3
from services.db.db_connection import get_db_connection, updateTaskStatusforCallId, getOneAnalysis, getAllPendingTask
from services.analysis import callAnalysis
import concurrent.futures

def checkTaskStatus(call_id, db):
    res = getOneAnalysis(db, call_id)
    return res['task_status'] != 'INPROGRESS'

def process_call(call):
    db = get_db_connection()  # Establish a new database connection for each process
    try:
        file = call['s3_file_path']
        call_id = call['call_id']
        print('*************** Started Process for Call_id :::', call_id)
        taskStatus = checkTaskStatus(call_id, db)
        print('*************** taskStatus :::', taskStatus)
        if taskStatus:
            updateTaskStatusforCallId(db, 'INPROGRESS', call_id)
            print('*************** Making Call to CallAnalysis with File and Call data ***************')
            callAnalysis(file, call, db)
    except Exception as e:
        print(f'Error processing call {call["call_id"]}: {e}')
    finally:
        db.close()  # Close the database connection

def init():
    print('*************** CALL ANALYSIS INIT ***************')
    try:
        db = get_db_connection()  # Main database connection for fetching pending tasks
        pending_call_analysis = getAllPendingTask(db)
        print('*************** Pending Calls START ***************')
        print(pending_call_analysis)
        print('*************** Pending Calls END ***************')
        db.close()  # Close the main database connection after fetching pending tasks
        # Process tasks in chunks of 2
        for i in range(0, len(pending_call_analysis), 2):
            chunk = pending_call_analysis[i:i + 2]
            with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                future_to_call = {executor.submit(process_call, call): call for call in chunk}
                for future in concurrent.futures.as_completed(future_to_call):
                    call = future_to_call[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f'Call analysis generated an exception for call {call["call_id"]}: {e}')
    except Exception as e:
        print('Error in callAnalysis init :::', e)
        raise Exception(f"Error in callAnalysis init: {e}")
init()
