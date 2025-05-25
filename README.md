# GIS_Projects-For-Final-Exams

# Advanced GIS-ML Based Crop Recommendation System for Sustainable Agriculture in Antalya, Turkey

## 🌍 Overview

This project develops a **GIS-integrated machine learning crop recommendation system** to support sustainable agriculture in Antalya, Turkey. It uses spatial analysis, remote sensing data, and advanced machine learning classifiers to generate suitability maps for greenhouse banana cultivation.

---

## 📁 Project Structure

├── Inputs.csv / .txt / .xlsx # Feature and label data extracted from GEE
├── Label.txt / .csv # Labels: 1 = Banana crop point, 0 = Other
├── *.tif # Raster layers and suitability prediction maps
├── *.png # Visualizations of model results and suitability maps
├── best_model.pkl # Trained best-performing model (XGBoost/LightGBM/etc.)
├── *.ipynb # Python notebook(s) for model training and mapping
├── Final_Report/ # Folder containing final PDF and PPT report
├── README.md # Project summary and navigation guide


---

## 🧪 Machine Learning Models Used

- **Random Forest**
- **XGBoost**
- **LightGBM**
- **Neural Network (MLP)**

Each model was trained using spatially-extracted features from 15 environmental and agricultural raster layers. Models were evaluated with metrics such as Accuracy, Precision, Recall, and ROC-AUC.

---

## 🗺️ Raster Layers Used (15 Bands)

Some examples include:
- NDVI Standard Deviation
- Precipitation
- Clay Content
- Soil pH
- Soil Organic Carbon
- DEM, Slope, Aspect
- Land Cover & Land Use
- Albedo
- Annual Temperature

All layers were prepared and visualized using **Google Earth Engine** and post-processed in **Python**.

---

## 🌐 Web Application

A simple web application was developed using **Flask** and **Leaflet** to:
- Upload model and raster data
- Visualize crop suitability maps
- Interact with field boundaries for localized recommendation

---

## 📄 Final Report

You can read the full project report detailing methodology, data sources, model comparison, and system design here:

📎 [**Final Project Report (PDF)**]([https://github.com/abdramanemhtali/GIS_Projects-For-Final-Exams/blob/main/Projects%20For%20Final%20Exams/Final_Report/Final_Exam_Projects_A1.pdf])

---

## 🔧 Tools & Technologies

- Google Earth Engine (GEE)
- Python (NumPy, Pandas, Rasterio, XGBoost, LightGBM, Scikit-learn, Matplotlib)
- Jupyter Notebooks / Google Colab
- Flask (for web app)
- Leaflet.js (for map visualization)
- ArcMap 10.8 (for shapefile generation and analysis)

---


📬 Contact
Author: Abdramane Mahamat Ali
Supervisor: Dr. Öğr. Üyesi Sohaib K. M. Abujayyab
University: Karabuk University
Email: abdramamemahamatali@gmail.com


