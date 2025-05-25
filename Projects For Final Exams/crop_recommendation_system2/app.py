from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import pickle
import pandas as pd
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from datetime import datetime
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import tempfile

app = Flask(__name__)

# Configure upload folders
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'models')
app.config['TIFF_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'tiff_data')
app.config['PREDICTION_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'predictions')

# Ensure upload directories exist
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)
os.makedirs(app.config['TIFF_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREDICTION_FOLDER'], exist_ok=True)

# Allowed TIFF file types
ALLOWED_TIFF_KEYS = [
    "Albedo", 
    "Annual_Temperature", 
    "Aspect", 
    "Clay_Content", 
    "DEM_Antalya", 
    "Land_Cover", 
    "LandUse", 
    "LST", 
    "NDVI_StdDev_Antalya", 
    "Precipitation_Antalya", 
    "Slope", 
    "Soil_Organic_Carbon", 
    "Soil_pH", 
    "SoilpH", 
    "SoilTexture"
]


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

@app.route('/upload_tiff', methods=['POST'])
def upload_tiff():
    if 'tiff_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})
    
    file = request.files['tiff_file']
    tiff_type = request.form.get('tiff_type')
    
    if not tiff_type or tiff_type not in ALLOWED_TIFF_KEYS:
        return jsonify({'status': 'error', 'message': 'Invalid TIFF type specified'})
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})
    
    if file and (file.filename.endswith('.tif') or file.filename.endswith('.tiff')):
        filename = f"{tiff_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.tif"
        filepath = os.path.join(app.config['TIFF_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'status': 'success', 'message': 'TIFF uploaded successfully', 'filename': filename, 'tiff_type': tiff_type})
    
    return jsonify({'status': 'error', 'message': 'Invalid file format. Please upload a .tif or .tiff file'})

def align_and_resample_tiffs(tiff_folder, reference_key="DEM_Antalya"):
    file_paths = {}
    image_data = []
    
    # Find all uploaded TIFFs and organize by type
    for filename in os.listdir(tiff_folder):
        for key in ALLOWED_TIFF_KEYS:
            if filename.startswith(key):
                file_paths[key] = os.path.join(tiff_folder, filename)
                break
    
    if not file_paths:
        raise ValueError("No valid TIFF files found")
    
    if reference_key not in file_paths:
        raise ValueError(f"Reference TIFF {reference_key} not found")
    
    # Open reference image
    with rasterio.open(file_paths[reference_key]) as reference:
        reference_profile = reference.profile
        height, width = reference.shape
        
        # Process each TIFF
        for key, input_path in file_paths.items():
            with rasterio.open(input_path) as src:
                # Create destination array
                dest = np.zeros((height, width), dtype=np.float32)
                
                # Reproject to match reference
                reproject(
                    source=rasterio.band(src, 1),
                    destination=dest,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=reference.transform,
                    dst_crs=reference.crs,
                    resampling=Resampling.bilinear
                )
                
                # Handle NaN values
                dest[dest == reference.nodata] = np.nan
                filled_data = np.nan_to_num(dest, nan=0.0)
                
                image_data.append(filled_data.flatten())
    
    # Stack into 2D array (pixels x variables)
    image_data_np = np.column_stack(image_data)
    
    # Create DataFrame
    resampled_df = pd.DataFrame(image_data_np, columns=list(file_paths.keys()))
    
    return resampled_df, reference_profile

@app.route('/predict', methods=['POST'])
def predict():
    try:
        model_filename = request.form.get('model_filename')
        if not model_filename:
            return jsonify({'status': 'error', 'message': 'Please select a model file'})
        
        # Load model
        model_path = os.path.join(app.config['MODEL_FOLDER'], model_filename)
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Process TIFFs
        resampled_df, reference_profile = align_and_resample_tiffs(app.config['TIFF_FOLDER'])
        
        # Make predictions
        predictors = ALLOWED_TIFF_KEYS
        y_prob = model.predict_proba(resampled_df[predictors])
        predictions = y_prob[:, 1]  # Probability of class 1
        
        # Reshape to original image dimensions
        prediction_image = predictions.reshape(reference_profile['height'], reference_profile['width'])
        
        # Save prediction as TIFF
        prediction_filename = f"prediction_{datetime.now().strftime('%Y%m%d%H%M%S')}.tif"
        prediction_path = os.path.join(app.config['PREDICTION_FOLDER'], prediction_filename)
        
        with rasterio.open(prediction_path, 'w', **reference_profile) as dst:
            dst.write(prediction_image, 1)
        
        # Create visualization
        viz_filename = f"viz_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        viz_path = os.path.join(app.config['PREDICTION_FOLDER'], viz_filename)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(prediction_image, cmap='viridis')
        plt.colorbar(label='Wildfire Probability')
        plt.title('Predicted Wildfire Risk')
        plt.axis('off')
        plt.savefig(viz_path, bbox_inches='tight', dpi=150)
        plt.close()
        
        return jsonify({
            'status': 'success',
            'prediction_tiff': f'/download_prediction/{prediction_filename}',
            'visualization': f'/download_prediction/{viz_filename}'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download_prediction/<filename>')
def download_prediction(filename):
    return send_from_directory(app.config['PREDICTION_FOLDER'], filename, as_attachment=True)

@app.route('/list_models')
def list_models():
    models = [f for f in os.listdir(app.config['MODEL_FOLDER']) if f.endswith('.pkl')]
    return jsonify({'status': 'success', 'models': models})

@app.route('/list_tiffs')
def list_tiffs():
    tiffs = {}
    for filename in os.listdir(app.config['TIFF_FOLDER']):
        for key in ALLOWED_TIFF_KEYS:
            if filename.startswith(key):
                tiffs[key] = filename
                break
    return jsonify({'status': 'success', 'tiffs': tiffs})

if __name__ == '__main__':
    app.run(debug=True)