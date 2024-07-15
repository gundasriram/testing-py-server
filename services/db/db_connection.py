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
            print('*************** CLOSING DB CONNECTION ***************')
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
            # set_clause = ', '.join([f"{key} = %s" for key in analysis_data.keys()])
            # where_clause_str = ' AND '.join([f"{key} = %s" for key in where_clause.keys()])
            # query = f"UPDATE call_analysis SET {set_clause} WHERE {where_clause_str}"
            # values = list(analysis_data.values()) + list(where_clause.values())
            query = "UPDATE call_analysis SET segregated_conversations = %s, customer_meta_data = %s, call_summary = %s, call_objective = %s, product_discussed = %s, agent_actions = %s, overall_conversation_rating_for_agents = %s, overall_sentiment_of_the_call = %s, overall_customer_satisfaction_level = %s, overall_call_time = %s, individual_call_time = %s, WHERE call_id = %s"
            print('type of transcription_whisper', type(analysis_data['transcription_whisper']))
            data = {
                'segregated_conversations': analysis_data['segregated_conversations'],
                'customer_meta_data': analysis_data['customer_meta_data'],
                'call_summary': analysis_data['call_summary'],
                'call_objective': analysis_data['call_objective'],
                'product_discussed': analysis_data['product_discussed'],
                'agent_actions': analysis_data['agent_actions'],
                'overall_conversation_rating_for_agents': analysis_data['overall_conversation_rating_for_agents'],
                'overall_sentiment_of_the_call': analysis_data['overall_sentiment_of_the_call'],
                'overall_customer_satisfaction_level': analysis_data['overall_customer_satisfaction_level'],
                'overall_call_time': analysis_data['overall_call_time'],
                'individual_call_time': analysis_data['individual_call_time'],
                'call_id': where_clause['call_id']
                # 'issue_resolved': analysis_data['issue_resolved'],
                # 'called_more_than_once': analysis_data['called_more_than_once'],
                # 'transcription_whisper': analysis_data['transcription_whisper']
            }
            print('*************** data', data)
            print('*************** query', query),
            print('*************** analysis_data ', analysis_data)
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, (data, ))
            self.conn.commit()
            cursor.close()
            print('*************** updateFinalAnalysis END ***************')
        except Exception as e:
            print('Error in updateFinalAnalysis :::', e)
            raise Exception(f"Error in updateFinalAnalysis: {e}")

# Singleton instance to be used throughout the application
db = Database()
