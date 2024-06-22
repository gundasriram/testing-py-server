from flask import Flask, request, jsonify
from services.analysis import callAnalysis
app = Flask(__name__)
from dotenv import load_dotenv

@app.route('/api/analysis', methods=['POST'])
def handler():
    data = request.json
    finalresponse = callAnalysis(data)
    # Process the data as needed
    response = {
        'message': 'First API received the data!',
        'received_data': finalresponse
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
