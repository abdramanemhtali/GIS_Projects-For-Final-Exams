Project structure



crop_recommendation_system/
├── app.py                  # Flask backend
├── static/
│   └── style.css           # CSS for styling
├── templates/
│   └── index.html          # Frontend HTML
├── uploads/                # Folder for uploaded files
│   ├── models/             # Stores uploaded ML models
│   ├── data/               # Stores uploaded CSV files
│   └── predictions/        # Stores prediction results
└── requirements.txt        # Python dependencies


How to Use
Create the project structure as shown above
Install Python
Install the dependencies with pip install -r requirements.txt
Run the application with python app.py
cd C:\Users\User\Desktop\Sohaib\olds\crop_recommendation_system1\crop_recommendation_system
Access the application at http://localhost:5000




pip install -r requirements.txt
pip install flask pandas scikit-learn xgboost numpy
pip install rasterio
pip install matplotlib openpyxl



Features
Model Upload: Upload your trained XGBoost model in .pkl format

Data Upload: Upload your tabular data in CSV or Excel format

Prediction: Select the uploaded model and data to make predictions

Download Results: Download the prediction results as a text file

Responsive Design: Works on desktop and mobile devices

User-Friendly Interface: Clean, modern UI with intuitive controls

The application will save all uploaded files in the uploads directory, organized into subfolders for models, data, and predictions.