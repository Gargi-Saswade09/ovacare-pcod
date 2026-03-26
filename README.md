# 🩺 OvaCare – PCOD Risk Prediction & Stress Detection

## 📌 Overview

OvaCare is a web-based healthcare application designed to **predict PCOD (Polycystic Ovarian Disease) risk** and **analyze stress levels** using machine learning and user input data.

The system collects health and lifestyle information such as BMI, menstrual patterns, and stress responses to provide:

* Early risk prediction
* Stress evaluation
* Personalized diet and lifestyle suggestions

It also includes a **chatbot support system** to guide users with basic health advice and stress management tips. The goal is to promote **preventive healthcare and awareness**.

---

## 🚀 Features

* 📊 PCOD Risk Prediction using ML
* 🧠 Stress Detection System
* 💬 Chatbot for user support
* 📈 Dashboard with health insights
* 🔐 User authentication system

---

## 🛠️ Tech Stack 

### 🎨 Frontend

* **HTML5** – Used for structuring web pages and creating forms for user input (health data, stress questionnaire).
* **CSS3** – Used for designing responsive and visually appealing UI (layout, colors, styling).
* **JavaScript** – Handles client-side logic, form validation, API calls, and dynamic updates (dashboard, results, charts).

---

### ⚙️ Backend

* **Python** – Core programming language used for building application logic and integrating machine learning models.
* **Flask** – Lightweight web framework used to:

  * Handle routing (API endpoints)
  * Manage client-server communication
  * Process user requests and responses

---

### 🗄️ Database

* **PostgreSQL** – Used to store:

  * User authentication data
  * Health records
  * Prediction results
* Ensures reliable and structured data storage.

---

### 🤖 Machine Learning

* **Scikit-learn** – Used for building and training ML models for PCOD prediction.
* **XGBoost** – Advanced machine learning algorithm used for accurate classification and prediction.
* **TF-IDF (Term Frequency–Inverse Document Frequency)** – Used in chatbot for text processing and intent recognition.

---

### 📊 Data Processing

* **Pandas** – Used for:

  * Data cleaning
  * Data preprocessing
  * Handling datasets efficiently

---

### 💾 Model Storage

* **Joblib** – Used to save and load trained machine learning models efficiently.

---

### 💬 Chatbot System

* Built using:

  * **Natural Language Processing (NLP)** techniques
  * TF-IDF vectorization for intent classification
* Helps users with:

  * Stress management tips
  * Basic health-related queries

---

### 🔐 Authentication & Security

* User login and registration system implemented using Flask
* Secure handling of user data

---

### 🛠️ Development Tools

* **VS Code** – Code editor used for development
* **Git & GitHub** – Version control and project hosting



## ⚙️ How to Run This Project

### 🔹 Step 1: Clone Repository

```bash
git clone https://github.com/Gargi-Saswade09/ovacare-pcod.git
cd ovacare-pcod/backend
```

---

#### 🔹 Step 2: Create Virtual Environment

```bash
python -m venv env
```

Activate it:

**Windows**
```bash
env\Scripts\activate
```

**Mac/Linux**
```bash
source env/bin/activate
```

### 🔹 Step 3: Install Dependencies

pip install -r requirements.txt

---

### 🔹 Step 4: Run Application

python app.py

---

### 🔹 Step 5: Open in Browser

http://127.0.0.1:5000

---

## 📊 How It Works

1. User enters health data
2. System predicts PCOD risk
3. Stress level is calculated
4. Dashboard displays results
5. Chatbot provides guidance

---

## ⚠️ Disclaimer

This project is for educational purposes only and does not replace professional medical advice.

---

## 👩‍💻 Author

**Gargi Saswade**

---

⭐ If you like this project, give it a star!
