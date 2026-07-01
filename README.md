# 🩺 Hypertension & Diabetes Prediction System

This project is a desktop application that analyzes users' basic health data (age, gender, BMI, salt consumption, etc.) to predict hypertension and diabetes risks using AI-powered models.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 About the Project

**Hypertension & Diabetes Prediction** is a desktop-based Decision Support System that, starting from the life-saving importance of early diagnosis, analyzes users' basic health data and lifestyle habits to predict possible Hypertension (HTN) and Diabetes (DM) risks using AI-powered models. A Logistic Regression model trained on Kaggle datasets processes the inputs received from the user and presents possible risk conditions as percentages.

<img width="1512" height="982" alt="1" src="https://github.com/user-attachments/assets/179076ef-f34e-4697-9b01-0f4c17351bb8" />

### Key Features

* **Instant Risk Analysis:** Calculates hypertension and diabetes risk within seconds based on the entered data.
* **Scenario-Based Simulation:** The system detects the user's current condition (Fully Healthy, HTN Only, etc.) and performs cross-queries accordingly, such as "There is hypertension, but what is the diabetes risk?"
* **User-Friendly Interface (GUI):** A simple interface designed with Tkinter that anyone can easily use.
* **Visualization:** Analysis of health data through Matplotlib charts.
* **Data Logging:** Ability to track history by storing user data in CSV format.

<img width="1512" height="982" alt="2" src="https://github.com/user-attachments/assets/6abe6fea-44df-4ae4-a5be-e0d440cb485a" />

## 🛠️ Technologies Used

* **Python:** Main programming language.
* **Tkinter:** Graphical user interface (GUI).
* **Scikit-learn:** Machine learning model (Logistic Regression, Class Weighting).
* **Pandas & NumPy:** Data processing and analysis.
* **Matplotlib:** Charts and data visualization.
* **ReportLab:** Dynamic PDF report generation.

Not merely performing a mathematical probability calculation, this work also provides visual answers to the user's question "How much does my salt consumption increase the risk?", representing the transformation of theoretical machine learning algorithms into practical software for the end user.

<img width="1512" height="982" alt="4" src="https://github.com/user-attachments/assets/bc32d333-a5de-4494-a0cd-2837d293bf64" />

## 📂 Installation and Running

Follow these steps to run the project on your local computer:

1.  **Clone the Project:**
```bash
    git clone [https://github.com/iamsevval/hypertension_diabetes_prediction.git](https://github.com/iamsevval/hypertension_diabetes_prediction.git)
    cd hypertension_diabetes_prediction
```
2.  **Install Required Libraries:**
```bash
    pip install pandas numpy scikit-learn matplotlib
```
3.  **Start the Application:**
```bash
    python main.py
```

## 📊 Dataset

The [Hypertension Risk Prediction Dataset](https://www.kaggle.com/datasets/ankushpanday1/hypertension-risk-prediction-dataset) from Kaggle was used to train the model. The model takes the following parameters into account:

* Age & Gender
* Body Mass Index (BMI)
* Daily Salt and Water Consumption
* Smoking and Alcohol Use

## 🤝 Contributing

If you would like to contribute to the project:

1.  **Fork** this repository.
2.  Create a new **Branch** (`git checkout -b feature/new-feature`).
3.  **Commit** your changes (`git commit -m 'Added new feature'`).
4.  **Push** your branch (`git push origin feature/new-feature`).
5.  Open a **Pull Request**.
