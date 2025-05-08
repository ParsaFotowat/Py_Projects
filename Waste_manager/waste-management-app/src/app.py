from flask import Flask, request, jsonify
from predictor import Predictor
import os

app = Flask(__name__)

# Load the trained model
model_path = os.path.join('models', 'trained_model.pkl')
predictor = Predictor(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Make prediction
    result = predictor.predict(file)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)