from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import pickle
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Configure upload folders
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'models')
app.config['DATA_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'data')
app.config['PREDICTION_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'predictions')

# Ensure upload directories exist
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREDICTION_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_model', methods=['POST'])
def upload_model():
    if 'model_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})
    
    file = request.files['model_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})
    
    if file and file.filename.endswith('.pkl'):
        filename = f"model_{datetime.now().strftime('%Y%m%d%H%M%S')}.pkl"
        filepath = os.path.join(app.config['MODEL_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'status': 'success', 'message': 'Model uploaded successfully', 'filename': filename})
    
    return jsonify({'status': 'error', 'message': 'Invalid file format. Please upload a .pkl file'})

@app.route('/upload_data', methods=['POST'])
def upload_data():
    if 'data_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})
    
    file = request.files['data_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})
    
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        filename = f"data_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(file.filename)[1]}"
        filepath = os.path.join(app.config['DATA_FOLDER'], filename)
        file.save(filepath)
        
        # Convert .xlsx to .csv if needed
        if filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
            csv_filename = filename.replace('.xlsx', '.csv')
            csv_path = os.path.join(app.config['DATA_FOLDER'], csv_filename)
            df.to_csv(csv_path, index=False)
            filename = csv_filename
        
        return jsonify({'status': 'success', 'message': 'Data uploaded successfully', 'filename': filename})
    
    return jsonify({'status': 'error', 'message': 'Invalid file format. Please upload a .csv or .xlsx file'})

@app.route('/get_models')
def get_models():
    try:
        models = [f for f in os.listdir(app.config['MODEL_FOLDER']) if f.endswith('.pkl')]
        return jsonify({'status': 'success', 'models': models})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_data')
def get_data():
    try:
        files = [f for f in os.listdir(app.config['DATA_FOLDER']) if f.endswith('.csv')]
        return jsonify({'status': 'success', 'files': files})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        model_filename = request.form.get('model_filename')
        data_filename = request.form.get('data_filename')
        
        if not model_filename or not data_filename:
            return jsonify({'status': 'error', 'message': 'Please select both a model and data file'})
        
        # Load model
        model_path = os.path.join(app.config['MODEL_FOLDER'], model_filename)
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Load data
        data_path = os.path.join(app.config['DATA_FOLDER'], data_filename)
        data = pd.read_csv(data_path)
        
        # Make predictions
        predictions = model.predict(data)
        
        # Save predictions
        prediction_filename = f"predictions_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        prediction_path = os.path.join(app.config['PREDICTION_FOLDER'], prediction_filename)
        
        with open(prediction_path, 'w') as f:
            for pred in predictions:
                f.write(f"{pred}\n")
        
        return jsonify({
            'status': 'success',
            'predictions': predictions.tolist(),
            'download_url': f'/download_prediction/{prediction_filename}'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download_prediction/<filename>')
def download_prediction(filename):
    return send_from_directory(app.config['PREDICTION_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)