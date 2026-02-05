import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import os

class VeriIsleyici:
    def __init__(self):
        self.model_htn = None 
        self.model_dm = None  
        self.scaler_htn = StandardScaler()
        self.scaler_dm = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean') 
        self.df = None
        
        self.features = [
            'Age', 'BMI', 'Systolic_BP', 'Diastolic_BP', 
            'Cholesterol', 'LDL', 'HDL', 'Triglycerides', 
            'Glucose', 'Heart_Rate', 
            'Salt_Intake', 'Alcohol_Intake', 'Sleep_Duration', 
            'Physical_Activity_Level', 
            'Gender_Male', 'Smoking_Num', 'Family_History_Num'
        ]
        
        self.egit()

    def egit(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, 'data', 'hypertension_data.csv')
            
            if not os.path.exists(file_path):
                return False

            try:
                self.df = pd.read_csv(file_path)
                if len(self.df.columns) < 2:
                    self.df = pd.read_csv(file_path, sep=';')
            except Exception as e:
                print(f"Hata: {e}")
                return False

            self.df.columns = self.df.columns.str.strip()

            # Dönüşümler
            if 'Gender' in self.df.columns:
                self.df['Gender_Male'] = self.df['Gender'].astype(str).apply(
                    lambda x: 1 if 'male' in x.lower() and 'female' not in x.lower() else (1 if x.strip() == '1' else 0)
                )
            else: self.df['Gender_Male'] = 0

            if 'Smoking_Status' in self.df.columns:
                def clean_smoke(x):
                    s = str(x).lower()
                    if 'current' in s or 'smoker' in s or 'yes' in s: return 2
                    if 'former' in s or 'past' in s: return 1
                    return 0
                self.df['Smoking_Num'] = self.df['Smoking_Status'].apply(clean_smoke)
            else: self.df['Smoking_Num'] = 0

            if 'Family_History' in self.df.columns:
                self.df['Family_History_Num'] = self.df['Family_History'].astype(str).apply(
                    lambda x: 1 if 'yes' in x.lower() or '1' in x or 'true' in x.lower() else 0
                )
            else: self.df['Family_History_Num'] = 0

            if 'Physical_Activity_Level' in self.df.columns:
                def map_activity(x):
                    s = str(x).lower()
                    if 'low' in s: return 1
                    elif 'moderate' in s: return 2
                    elif 'high' in s: return 3
                    return 2
                self.df['Physical_Activity_Level'] = self.df['Physical_Activity_Level'].apply(map_activity)

            if 'BMI' not in self.df.columns and 'Weight' in self.df.columns:
                self.df['BMI'] = self.df['Weight'] / ((self.df['Height']/100)**2)

            if 'Hypertension' in self.df.columns:
                self.df['Target_HTN'] = self.df['Hypertension'].astype(str).apply(
                    lambda x: 1 if 'high' in x.lower() or 'yes' in x.lower() or '1' in x else 0
                )
            else:
                self.df['Target_HTN'] = self.df['Systolic_BP'].apply(lambda x: 1 if float(x) >= 140 else 0)

            if 'Diabetes' in self.df.columns:
                self.df['Target_DM'] = self.df['Diabetes'].astype(str).apply(
                    lambda x: 1 if 'yes' in x.lower() or '1' in x or 'true' in x.lower() else 0
                )
            else:
                self.df['Target_DM'] = self.df['Glucose'].apply(lambda x: 1 if float(x) >= 126 else 0)

            for col in self.features:
                if col not in self.df.columns: self.df[col] = 0
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            self.df[self.features] = self.imputer.fit_transform(self.df[self.features])

            # HTN Modeli
            X_htn = self.df[self.features + ['Target_DM']]
            y_htn = self.df['Target_HTN']
            self.scaler_htn.fit(X_htn)
            self.model_htn = LogisticRegression(max_iter=5000, class_weight='balanced')
            self.model_htn.fit(self.scaler_htn.transform(X_htn), y_htn)
            
            # DM Modeli
            X_dm = self.df[self.features + ['Target_HTN']]
            y_dm = self.df['Target_DM']
            self.scaler_dm.fit(X_dm)
            self.model_dm = LogisticRegression(max_iter=5000, class_weight='balanced')
            self.model_dm.fit(self.scaler_dm.transform(X_dm), y_dm)
            
            print("✅ Modeller hazır.")
            return True

        except Exception as e:
            print(f"Hata: {e}")
            return False

    def get_benzer_kisiler(self, age, gender, limit=500):
        if self.df is None: return None
        df_filter = self.df[
            (self.df['Age'] >= age - 5) & 
            (self.df['Age'] <= age + 5) & 
            (self.df['Gender_Male'] == gender)
        ]
        if len(df_filter) < 20:
            df_filter = self.df[(self.df['Age'] >= age - 10) & (self.df['Age'] <= age + 10)]
        return df_filter.sample(min(len(df_filter), limit), random_state=42) if not df_filter.empty else self.df.sample(limit)

    # --- (DataFrame Kullanarak Uyarıyı Çözer) ---
    def tahmin_et_htn(self, user_dict, diabetes_status):
        if not self.model_htn: return 0.0
        
        # Veriyi DataFrame olarak hazırla
        input_data = {f: float(user_dict.get(f, 0)) for f in self.features}
        input_data['Target_DM'] = 1 if diabetes_status else 0
        df_input = pd.DataFrame([input_data])
        
        # Sütun sırasını garantiye al
        X = df_input[self.features + ['Target_DM']]
        
        scaled = self.scaler_htn.transform(X)
        return self.model_htn.predict_proba(scaled)[0][1] * 100

    def tahmin_et_dm(self, user_dict, htn_status):
        if not self.model_dm: return 0.0
        
        input_data = {f: float(user_dict.get(f, 0)) for f in self.features}
        input_data['Target_HTN'] = 1 if htn_status else 0
        df_input = pd.DataFrame([input_data])
        
        X = df_input[self.features + ['Target_HTN']]
        
        scaled = self.scaler_dm.transform(X)
        return self.model_dm.predict_proba(scaled)[0][1] * 100

    def get_etki_analizi(self, user_dict, target='htn', existing_condition=0):
        if target == 'htn':
            model = self.model_htn
            scaler = self.scaler_htn
            feature_order = self.features + ['Target_DM']
            col_condition = 'Target_DM'
            feat_names_out = self.features + ['Mevcut Diyabet']
        else:
            model = self.model_dm
            scaler = self.scaler_dm
            feature_order = self.features + ['Target_HTN']
            col_condition = 'Target_HTN'
            feat_names_out = self.features + ['Mevcut Hipertansiyon']
            
        if not model: return {}

        input_data = {f: float(user_dict.get(f, 0)) for f in self.features}
        input_data[col_condition] = existing_condition
        df_input = pd.DataFrame([input_data])
        X = df_input[feature_order]

        row_scaled = scaler.transform(X)[0]
        coefs = model.coef_[0]
        
        etkiler = {}
        label_map = {
            'Age': 'Yaş', 'BMI': 'Kilo (BMI)', 'Systolic_BP': 'Büyük Tansiyon',
            'Diastolic_BP': 'Küçük Tansiyon', 'Cholesterol': 'Kolesterol', 'LDL': 'LDL',
            'HDL': 'HDL', 'Triglycerides': 'Trigliserit', 'Glucose': 'Şeker',
            'Heart_Rate': 'Nabız', 'Salt_Intake': 'Tuz', 'Alcohol_Intake': 'Alkol',
            'Sleep_Duration': 'Uyku', 'Physical_Activity_Level': 'Hareketsizlik',
            'Gender_Male': 'Cinsiyet', 'Smoking_Num': 'Sigara', 'Family_History_Num': 'Genetik',
            'Mevcut Diyabet': 'Diyabet Hastalığı', 'Mevcut Hipertansiyon': 'Tansiyon Hastalığı',
            'Target_DM': 'Diyabet Hastalığı', 'Target_HTN': 'Tansiyon Hastalığı'
        }

        for i, val in enumerate(row_scaled):
            if i < len(coefs):
                impact = val * coefs[i]
                if abs(impact) > 0.001: 
                    # Sütun ismini bul
                    if i < len(self.features):
                        raw_name = self.features[i]
                    else:
                        raw_name = col_condition
                    
                    name = label_map.get(raw_name, raw_name)
                    etkiler[name] = impact
        
        return etkiler

    def get_dataframe(self):
        return self.df