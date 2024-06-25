from flask import Flask, request, jsonify
from services.analysis import callAnalysis
app = Flask(__name__)
from dotenv import load_dotenv

@app.route('/api/analysis', methods=['POST'])
def handler():
    try:
        data = request.json
        finalresponse = callAnalysis(data)
        # Process the data as needed
        response = {
            'message': 'First API received the data!',
            'received_data': finalresponse
        }
        return jsonify(response), 200
    expect ClientError as e:
        return jsonify({'message' : 'Internal Server Error'}), 500
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
