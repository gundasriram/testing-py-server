import mysql.connector
import json
class Database:
    def __init__(self):
        self.conn = None
    def connect(self):
        try:
            print('*************** CONNECTING TO DB ***************')
            if self.conn is None:
                self.conn = mysql.connector.connect(
                    auth_plugin='mysql_native_password',
                    host="localhost",
                    user="root",
                    password="admin",
                    port=3306,
                    database="world",
                )
            return self.conn
        except Exception as e:
            print('Error in connect DB init :::', e)
            raise Exception(f"Error in connect init: {e}")
    def close(self):
        if self.conn is not None and self.conn.is_connected():
            self.conn.close()
            self.conn = None

    def getAllPendingTask(self):
        try:
            print('*************** getAllPending ***************')
            query = 'SELECT * from call_analysis where task_status = "PENDING" LIMIT 100'
            cursor = self.conn.cursor(dictionary=True)
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
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, (status, call_id))
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print('Error in updateTaskStatusforCallId :::', e)
            raise Exception(f"Error in updateTaskStatusforCallId: {e}")

    def getOneAnalysis(self, call_id):
        try:
            print('*************** getOneAnalysis ***************')
            query = "SELECT * from call_analysis where call_id = %s"
            print('query', query)
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, (call_id,))
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
            analysis_data['transcription_whisper'] = transcription_whisper
            set_clause = ', '.join([f"{key} = %s" for key in analysis_data.keys()])
            where_clause_str = ' AND '.join([f"{key} = %s" for key in where_clause.keys()])
            query = f"UPDATE call_analysis SET {set_clause} WHERE {where_clause_str}"
            values = list(analysis_data.values()) + list(where_clause.values())
            print('query', query)
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, tuple(values))
            mydb.commit()
            cursor.close()
            print('*************** updateFinalAnalysis END ***************')
        except Exception as e:
            print('Error in updateFinalAnalysis :::', e)
            raise Exception(f"Error in updateFinalAnalysis: {e}")

# Singleton instance to be used throughout the application
db = Database()
