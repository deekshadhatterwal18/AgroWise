# AgroWise — AI-Powered Agriculture Platform

AgroWise is an AI-powered agriculture platform that brings multiple agriculture-related solutions together in a single web application. The platform combines Machine Learning, Deep Learning, Retrieval-Augmented Generation (RAG), Large Language Models (LLMs), external APIs, Data Analysis, Flask, JavaScript, and PostgreSQL to provide farmers with data-driven agricultural support.

## Live Demo

https://agrowise-yyc1a.onrender.com

---

## Overview

Farmers often need different tools for crop selection, yield estimation, plant disease identification, weather information, market prices, agricultural schemes, and farming-related questions.

AgroWise integrates these requirements into one platform.

The application provides:

- Crop Recommendation
- Crop Yield Prediction
- Plant Disease Detection
- Weather Forecast
- Market Price Analysis
- Farmer Connect
- Government Schemes
- RAG-based Agricultural Chatbot

The project demonstrates an end-to-end application involving data preprocessing, machine learning, deep learning, API integration, database management, retrieval-augmented generation, backend development, frontend development, and cloud deployment.

---

## Problem Statement

Farmers need reliable information to make better agricultural decisions. However, information related to crop selection, expected yield, plant diseases, weather conditions, market prices, government schemes, and agricultural guidance is often available through separate sources.

AgroWise aims to provide these services through a single integrated platform.

---

## Objectives

- Recommend suitable crops based on soil and environmental conditions.
- Predict agricultural yield using farming and environmental data.
- Detect plant diseases from leaf images.
- Provide location-based weather information.
- Generate weather-based farming advisory.
- Analyze mandi market prices.
- Provide a farmer-to-farmer community platform.
- Provide agricultural government scheme information.
- Answer agriculture-related questions using RAG and an LLM.
- Integrate all modules into one web application.

---

# Features

## 1. Crop Recommendation

The Crop Recommendation module recommends suitable crops based on soil and environmental conditions.

### Input Features

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- Soil pH
- Rainfall

### Models Used

- Random Forest Classifier
- XGBoost Classifier

The models are evaluated and the better-performing model is selected for prediction.

The system can also return multiple top crop recommendations.

### Workflow

Soil and Environmental Conditions  
↓  
Data Preprocessing  
↓  
Random Forest / XGBoost  
↓  
Model Evaluation  
↓  
Best Performing Model  
↓  
Crop Prediction  
↓  
Top Crop Recommendations

---

## 2. Crop Yield Prediction

The Yield Prediction module predicts agricultural yield using crop, season, location, farming, and environmental information.

### Features

- Crop
- Season
- State
- Area
- Rainfall
- Temperature
- Fertilizer
- Pesticide

Categorical features are encoded before being passed to the regression models.

### Models Used

- Random Forest Regressor
- XGBoost Regressor

### Evaluation Metrics

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score

### Workflow

Historical Agricultural Data  
↓  
Data Cleaning  
↓  
Feature Preparation  
↓  
Categorical Encoding  
↓  
Train/Test Split  
↓  
Random Forest / XGBoost  
↓  
Model Evaluation  
↓  
Best Model  
↓  
Yield Prediction

---

## 3. Plant Disease Detection

AgroWise provides image-based plant disease detection using a MobileNetV2-based deep learning model implemented with PyTorch.

The current model supports 38 plant disease/healthy classes.

### Technologies

- PyTorch
- Torchvision
- MobileNetV2
- Pillow

### Image Processing Pipeline

Leaf Image  
↓  
Image Validation  
↓  
RGB Conversion  
↓  
Resize to 224 × 224  
↓  
Tensor Conversion  
↓  
Normalization  
↓  
MobileNetV2  
↓  
Softmax Probabilities  
↓  
Top 3 Predictions  
↓  
Disease Information

The application loads trained `.pth` model weights during inference.

### Output

The system provides:

- Predicted disease
- Confidence score
- Top 3 predictions
- Disease cause
- Symptoms
- Treatment
- Prevention

Disease-related information is maintained separately in a JSON knowledge file.

### Supported Image Formats

- JPG
- JPEG
- PNG
- WEBP

---

## 4. Weather Forecast

The Weather module provides location-based weather information and forecast data.

The application uses external APIs for geocoding and weather forecasting.

### Technologies

- Python
- Requests
- JSON
- Flask
- JavaScript
- Weather APIs
- Geocoding APIs

### Workflow

Farmer Enters Location  
↓  
Frontend JavaScript  
↓  
Flask Weather Endpoint  
↓  
Geocoding API  
↓  
Latitude + Longitude  
↓  
Weather Forecast API  
↓  
Current Weather + Forecast  
↓  
Rule-Based Farming Advisory  
↓  
JSON Response  
↓  
Frontend Display

### Weather Information

- Location
- Current weather
- Temperature
- Weather conditions
- Forecast
- Farming advisory

The advisory is generated using rule-based logic based on weather information.

---

## 5. Market Analysis

The Market Analysis module processes mandi price data and allows farmers to compare agricultural prices across different states.

The module uses Pandas for data processing and Chart.js for frontend visualization.

### Processing Workflow

Mandi Price Dataset  
↓  
Data Loading  
↓  
Data Cleaning  
↓  
Missing Value Handling  
↓  
Price Conversion  
↓  
State-wise Grouping  
↓  
Average Price Calculation  
↓  
State-wise Comparison  
↓  
Chart Visualization

### Operations

- Load mandi price dataset
- Handle missing values
- Convert price from ₹/quintal to ₹/kg
- Group prices by state
- Calculate average prices
- Find highest and lowest prices
- Compare prices across states
- Display graphical comparisons

This module is a data analysis feature rather than an ML prediction module.

---

## 6. Farmer Connect

Farmer Connect is a community discussion module integrated into AgroWise.

It allows farmers to share:

- Questions
- Farming experiences
- Suggestions
- Problems
- Agricultural information

### Features

- Create posts
- View posts
- Open individual posts
- Add comments
- View comment counts
- Participate in discussions

### Technologies

- Flask
- PostgreSQL
- Jinja2
- HTML
- CSS
- JavaScript

### Workflow

Farmer  
↓  
Create Post  
↓  
HTTP POST Request  
↓  
Flask Backend  
↓  
PostgreSQL  
↓  
Store Post  
↓  
Retrieve Post  
↓  
Jinja2 Template  
↓  
Display Post

---

## 7. Government Schemes

AgroWise provides a dedicated section for agricultural government schemes and related information.

The objective is to make useful agricultural support information available within the same platform.

---

## 8. RAG-Based Agricultural Chatbot

AgroWise includes a Retrieval-Augmented Generation (RAG) based agricultural chatbot.

The chatbot retrieves relevant information from the agricultural knowledge base and uses that information as context for generating answers through an LLM.

### Why RAG?

A traditional LLM generates an answer primarily from its learned knowledge.

RAG first retrieves relevant information and then provides that information as context to the LLM.

This allows the chatbot to generate responses based on the application's available agricultural knowledge.

### RAG Workflow

Agricultural Documents  
↓  
Document Processing  
↓  
Text Chunking  
↓  
Embedding Generation  
↓  
Relevant Retrieval  
↓  
User Question  
↓  
Relevant Context  
↓  
LLM  
↓  
Generated Answer

### Chatbot Response

The chatbot returns:

- Generated answer
- Retrieved sources
- Number of chunks used

### Request Flow

User Question  
↓  
Flask Chatbot Endpoint  
↓  
RAG Pipeline  
↓  
Retrieve Relevant Chunks  
↓  
Generate Answer  
↓  
JSON Response  
↓  
Frontend

---

# System Architecture

AgroWise follows a modular architecture where Flask acts as the central backend layer.

Farmer  
↓  
Web Interface  
↓  
Flask Backend  
↓  
Machine Learning / Deep Learning / APIs / Database / RAG  
↓  
Processed Result  
↓  
Frontend Display

### Detailed Architecture

Farmer  
│  
▼  
Web Interface  
HTML / CSS / JavaScript  
│  
▼  
Flask Backend  
│  
├── Crop Recommendation  
│   ├── Random Forest  
│   └── XGBoost  
│  
├── Yield Prediction  
│   ├── Random Forest Regressor  
│   └── XGBoost Regressor  
│  
├── Disease Detection  
│   └── MobileNetV2 / PyTorch  
│  
├── Weather  
│   ├── Geocoding API  
│   └── Weather API  
│  
├── Market Analysis  
│   └── Pandas / Chart.js  
│  
├── Farmer Connect  
│   └── PostgreSQL  
│  
├── Government Schemes  
│  
└── RAG Chatbot  
    ├── Retrieval  
    ├── Embeddings  
    └── LLM  
│  
▼  
Database / External Services  
│  
▼  
Response  
│  
▼  
Frontend

---

# Complete Application Workflow

1. Farmer opens the AgroWise web application.
2. The farmer selects the required agricultural service.
3. The frontend collects the required inputs.
4. JavaScript sends the request to the Flask backend.
5. Flask processes the request.
6. Depending on the module, Flask communicates with:
   - Machine Learning models
   - Deep Learning model
   - PostgreSQL database
   - External APIs
   - RAG pipeline
7. The processed result is returned to the frontend.
8. JavaScript displays the result to the farmer.

---

# Backend Architecture

Flask acts as the main integration layer of AgroWise.

The backend handles:

- Web page routing
- API requests
- Machine learning predictions
- Image uploads
- Disease prediction
- Weather API calls
- Market data processing
- Database operations
- Farmer Connect operations
- Chatbot requests
- Session-based access
- JSON responses

---

# API Endpoints

## Crop Recommendation

`POST /api/crop/predict`

Receives crop recommendation inputs and returns crop predictions.

## Yield Prediction

`POST /api/yield/predict`

Receives agricultural inputs and returns predicted yield.

## Disease Detection

`POST /api/disease/predict`

Receives an uploaded plant image and returns disease predictions.

## Weather

`GET /api/weather`

Returns weather information based on the requested location.

## Market Commodities

`GET /api/market/commodities`

Returns available commodities.

## Market States

`GET /api/market/states`

Returns states available for a selected commodity.

## Market Prices

`GET /api/market/prices`

Returns processed market price information.

## Chatbot

`POST /api/chatbot/ask`

Receives an agriculture-related question and returns the RAG-generated response.

---

# Frontend–Backend Communication

The frontend communicates with Flask through HTTP requests and API calls.

User Input  
↓  
HTML Form / JavaScript  
↓  
Fetch Request  
↓  
Flask API Endpoint  
↓  
Processing  
↓  
ML Model / Deep Learning / Database / External API / RAG  
↓  
JSON Response  
↓  
JavaScript  
↓  
Dynamic UI Update

---

# Machine Learning Architecture

## Crop Recommendation Pipeline

Dataset  
↓  
Data Cleaning  
↓  
Feature Preparation  
↓  
Train/Test Split  
↓  
Random Forest + XGBoost  
↓  
Model Evaluation  
↓  
Best Performing Model  
↓  
Model Serialization  
↓  
Flask API  
↓  
Prediction

## Yield Prediction Pipeline

Historical Agricultural Dataset  
↓  
Data Cleaning  
↓  
Feature Preparation  
↓  
Categorical Encoding  
↓  
Train/Test Split  
↓  
Random Forest Regressor + XGBoost Regressor  
↓  
Model Evaluation  
↓  
Best Model  
↓  
Model Serialization  
↓  
Flask API  
↓  
Yield Prediction

---

# Model Serialization

The trained machine learning models and preprocessing components are saved using Joblib.

This allows the Flask application to load the trained models during prediction without retraining them for every request.

Training  
↓  
Model Training  
↓  
Model Evaluation  
↓  
Best Model Selection  
↓  
Joblib Serialization  
↓  
Saved Model  
↓  
Flask Application  
↓  
Prediction

---

# Deep Learning Architecture

The Plant Disease Detection module uses MobileNetV2 for image classification.

### Inference Pipeline

Input Image  
↓  
Image Validation  
↓  
RGB Conversion  
↓  
224 × 224 Resize  
↓  
Normalization  
↓  
MobileNetV2  
↓  
Class Probabilities  
↓  
Top Predictions  
↓  
Disease Information

The trained model weights are stored in `.pth` format and loaded during inference.

---

# Database Architecture

AgroWise uses PostgreSQL for structured application data.

The Flask backend connects to PostgreSQL using `psycopg2`.

Supabase can be used as the hosted PostgreSQL platform.

### Database Usage

The database is used for application information such as:

- User information
- Farmer Connect posts
- Comments
- Community-related data

### Database Configuration

The database connection is configured using the environment variable:

`DATABASE_URL`

Database credentials are not hard-coded in the application.

---

# Authentication and Sessions

The application uses session-based access control for protected functionality.

### Authentication Flow

User  
↓  
Login  
↓  
Credentials Verification  
↓  
Session Creation  
↓  
Protected Feature  
↓  
Database / Application Access

The backend can check the user's session before allowing access to protected pages or endpoints.

---

# Technology Stack

## Programming Languages

- Python
- JavaScript
- SQL

## Machine Learning

- Scikit-learn
- Random Forest
- XGBoost
- Pandas
- NumPy
- Joblib

## Deep Learning

- PyTorch
- Torchvision
- MobileNetV2
- Pillow

## Generative AI

- Retrieval-Augmented Generation (RAG)
- Large Language Models (LLMs)
- Sentence Transformers
- Embeddings

## Backend

- Flask
- Jinja2
- REST APIs
- Python Requests

## Frontend

- HTML
- CSS
- JavaScript
  

## Database

- PostgreSQL
  

## External Services

- Weather APIs
- Geocoding APIs

## Deployment

- Git
- GitHub
- Gunicorn
- Render

---

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/AgroWise.git
cd AgroWise
