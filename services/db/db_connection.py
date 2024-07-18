import os
import mysql.connector
import json

# MYSQL_HOST= os.environ['MYSQL_HOST']
# MYSQL_USER= os.environ['MYSQL_USER']
# MYSQL_PASSWORD= os.environ['MYSQL_PASSWORD']
# MYSQL_PORT= os.environ['MYSQL_PORT']
# MYSQL_DATABASE= os.environ['MYSQL_DATABASE']

# class Database:
#     def __init__(self):
#         self.conn = None
#     def connect(self):
#         try:
#             print('*************** CONNECTING TO DB ***************')
#             if self.conn is None:
#                 self.conn = mysql.connector.connect(
#                     auth_plugin='mysql_native_password',
#                     host="localhost",
#                     user="root",
#                     password="admin",
#                     port=3306,
#                     database="world",
#                 )
#             return self.conn
#         except Exception as e:
#             print('Error in connect DB init :::', e)
#             raise Exception(f"Error in connect init: {e}")
#     def close(self):
#         if self.conn is not None and self.conn.is_connected():
#             print('*************** CLOSING DB CONNECTION ***************')
#             self.conn.close()
#             self.conn = None

def get_db_connection():
    try:
        print('*************** CONNECTING TO DB ***************')
        return mysql.connector.connect(
                    auth_plugin='mysql_native_password',
                    host="localhost",
                    user="root",
                    password="admin",
                    port=3306,
                    database="world",
        )
    except Exception as e:
        print('Error in connect DB init :::', e)
        raise Exception(f"Error in connect init: {e}")

def getAllPendingTask(self):
    try:
        print('*************** getAllPending ***************')
        query = 'SELECT id, task_status, call_id, s3_file_path from call_analysis where task_status = "PENDING"'
        cursor = self.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        json_data = json.dumps(rows, indent=4) 
        cursor.close()
        return json.loads(json_data)
    except Exception as e:
        print('Error in getAllPending init :::', e)
        raise Exception(f"Error in getAllPending init: {e}")

def updateTaskStatusforCallId(self, status, call_id):
    try:
        print('*************** updateTaskStatusforCallId ***************')
        query = "UPDATE call_analysis SET task_status = %s where call_id = %s"
        print('query', query)
        cursor = self.cursor(dictionary=True)
        cursor.execute(query, (status, call_id))
        self.commit()
        cursor.close()
    except Exception as e:
        print('Error in updateTaskStatusforCallId :::', e)
        raise Exception(f"Error in updateTaskStatusforCallId: {e}")

def getOneAnalysis(self, call_id, id):
    try:
        print('*************** getOneAnalysis ***************')
        query = "SELECT * from call_analysis where call_id = %s and id = %s"
        print('query', query)
        cursor = self.cursor(dictionary=True)
        cursor.execute(query, (call_id, id,))
        rows = cursor.fetchone()
        json_data = json.dumps(rows, indent=4) 
        cursor.close()
        return json.loads(json_data)
    except Exception as e:
        print('Error in getOneAnalysis :::', e)
        raise Exception(f"Error in getOneAnalysis: {e}")

def updateFinalAnalysis(self, where_clause, analysis_data, transcription_whisper):
    try:
        print('*************** updateFinalAnalysis Start ***************')
        # analysis_data['transcription_whisper'] = transcription_whisper
        for key, value in analysis_data.items():
            if isinstance(value, (list, dict)):
                analysis_data[key] = json.dumps(value)
        # Prepare the SET clause and WHERE clause strings
        data = {
            'call_summary': analysis_data['call_summary'],
            'call_objective': analysis_data['call_objective'],
            'product_discussed': analysis_data['product_discussed'],
            'overall_conversation_rating_for_agents': analysis_data['overall_conversation_rating_for_agents'],
            'overall_sentiment_of_the_call': analysis_data['overall_sentiment_of_the_call'],
            'overall_customer_satisfaction_level': analysis_data['overall_customer_satisfaction_level'],
            'overall_call_time': analysis_data['overall_call_time']
        }
        set_clause = ', '.join([f"{key} = %s" for key in analysis_data.keys()])
        where_clause_str = ' AND '.join([f"{key} = %s" for key in where_clause.keys()])
        query = f"UPDATE call_analysis SET {set_clause} WHERE {where_clause_str}"
        # Combine the values from analysis_data and where_clause
        values = list(analysis_data.values()) + list(where_clause.values())
        # print('type of transcription_whisper', type(analysis_data['transcription_whisper']))
        print('*************** data', data)
        print('*************** query', query)
        print('*************** analysis_data ', analysis_data)
        print('*************** values', values)
        cursor = self.cursor()
        cursor.execute(query, values)
        self.commit()
        cursor.close()
        print('*************** updateFinalAnalysis END ***************')
    except Exception as e:
        print('Error in updateFinalAnalysis :::', e)
        raise Exception(f"Error in updateFinalAnalysis: {e}")

def updateWhisperTimeTaken(self, timeTaken, call_id):
    try:
        print('*************** updateTaskStatusforCallId ***************')
        query = "UPDATE call_analysis SET transcription_timetaken = %s where call_id = %s"
        print('query', query)
        cursor = self.cursor(dictionary=True)
        cursor.execute(query, (timeTaken, call_id))
        self.commit()
        cursor.close()
    except Exception as e:
        print('Error in updateTaskStatusforCallId :::', e)
        raise Exception(f"Error in updateTaskStatusforCallId: {e}")

def promptResponseTimeTaken(self, timeTaken, call_id):
    try:
        print('*************** promptResponseTimeTaken ***************')
        query = "UPDATE call_analysis SET llm_timetaken = %s where call_id = %s"
        print('query', query)
        cursor = self.cursor(dictionary=True)
        cursor.execute(query, (timeTaken, call_id))
        self.commit()
        cursor.close()
    except Exception as e:
        print('Error in promptResponseTimeTaken :::', e)
        raise Exception(f"Error in promptResponseTimeTaken: {e}")

def updateTranscription(self, transcription, call_id):
    try:
        print('*************** updateTranscription ***************')
        query = "UPDATE call_analysis SET transcription_whisper = %s where call_id = %s"
        print('query', query)
        cursor = self.cursor(dictionary=True)
        cursor.execute(query, (transcription, call_id))
        self.commit()
        cursor.close()
    except Exception as e:
        print('Error in updateTranscription :::', e)
        raise Exception(f"Error in updateTranscription: {e}")

def update_llm_raw_response(self, response, call_id):
    try:
        print('*************** update_llm_raw_response ***************')
        query = "UPDATE call_analysis SET llm_raw_response = %s where call_id = %s"
        print('query', query)
        cursor = self.cursor(dictionary=True)
        cursor.execute(query, (response, call_id))
        self.commit()
        cursor.close()
    except Exception as e:
        print('Error in update_llm_raw_response :::', e)
        raise Exception(f"Error in update_llm_raw_response: {e}")


# Singleton instance to be used throughout the application
# db = Database()
