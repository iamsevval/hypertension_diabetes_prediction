import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import platform
import subprocess
from datetime import datetime
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PDF_DIR = BASE_DIR / "hasta_saglik_raporlari"
CSV_DIR = BASE_DIR / "hasta_saglik_kayitlari"

PDF_DIR.mkdir(exist_ok=True)
CSV_DIR.mkdir(exist_ok=True)

# --- IMPORT KONTROLU ---
try:
    from modules.veri_isleme import VeriIsleyici 
    from modules.grafikler import GrafikCizici
except ImportError:
    pass
# -----------------------

if platform.system() == "Windows":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass

class LoginPenceresi:
    def __init__(self, root):
        self.root = root
        self.root.title("Giriş")
        self.root.geometry("400x250")
        self.root.configure(bg="#2c3e50")
        
        tk.Label(root, text="Sağlık Risk\nAnaliz Sistemi", bg="#2c3e50", fg="white", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(root, text="Ad Soyad:", bg="#2c3e50", fg="#bdc3c7").pack()
        
        self.entry_ad = tk.Entry(root, font=("Arial", 12), justify='center', bg="white", fg="black", insertbackground="black")
        self.entry_ad.pack(pady=10, ipady=5)
        
        tk.Button(root, text="Giriş Yap", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), command=self.giris_yap).pack(pady=10)
        self.kullanici_adi = None

    def giris_yap(self):
        if self.entry_ad.get():
            self.kullanici_adi = self.entry_ad.get().replace(" ", "_")
            self.root.destroy()
        else:
            messagebox.showwarning("Uyarı", "Lütfen adınızı giriniz.")

class HipertansiyonApp:
    def __init__(self, root, kullanici_adi):
        self.root = root
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="white", background="white", foreground="black", arrowcolor="black")
        style.map('TCombobox', fieldbackground=[('readonly','white')])

        self.root.title(f"Analiz Paneli - {kullanici_adi.replace('_', ' ')}")
        self.root.geometry("1400x950") 
        self.kullanici_adi = kullanici_adi
        self.dosya_adi = CSV_DIR / f"{self.kullanici_adi}.csv"
        
        # --- TUZ DÖNÜŞÜM TABLOSU (Sınıf Özelliği Olarak Tanımlandı) ---
        self.tuz_donusum_tablosu = {
            "Gram (Direkt)": 1.0,
            "Çay Kaşığı (Silme)": 2.0,      
            "Çay Kaşığı (Tepeleme)": 4.0,   
            "Tatlı Kaşığı (Silme)": 5.0,    
            "Tatlı Kaşığı (Tepeleme)": 9.0, 
            "Yemek Kaşığı (Silme)": 10.0,   
            "Yemek Kaşığı (Tepeleme)": 18.0 
        }
        # -------------------------------------------------------------
        
        # Veri İşleyiciyi Başlat
        self.veri_isleyici = VeriIsleyici()
        
        if self.veri_isleyici.df is None:
            messagebox.showerror("Kritik Hata", "Veri seti (hypertension_data.csv) bulunamadı!\nLütfen data klasörünü kontrol edin.")
            self.root.destroy()
            return

        self.tab_control = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab1, text='📊 Veri Girişi ve Analiz')
        self.tab_control.add(self.tab2, text='📈 Geçmiş')
        self.tab_control.pack(expand=1, fill="both")
        
        self.son_analiz_sonuclari = {} 
        
        self.create_analysis_tab()
        self.create_history_tab()

        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_history_tab(self):
        self.graph_frame_gecmis = tk.Frame(self.tab2, bg="white")
        self.graph_frame_gecmis.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.grafik_yonetici_gecmis = GrafikCizici(self.graph_frame_gecmis)

    def create_analysis_tab(self):
        left_container = tk.Frame(self.tab1, width=330, bg="#f0f0f0") 
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        left_container.pack_propagate(False)

        canvas = tk.Canvas(left_container, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f0f0f0", padx=15, pady=20)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_mousewheel(event):
            if platform.system() == "Windows": delta = int(-1*(event.delta/120))
            else: delta = int(-1*event.delta)
            canvas.yview_scroll(delta, "units")
            
        left_container.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        left_container.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        tk.Label(self.scrollable_frame, text="Klinik ve Yaşam Verileri", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="black").pack(anchor="w", pady=10)
        
        self.entries = {}
        
        def create_entry(label_text, key):
            tk.Label(self.scrollable_frame, text=label_text, bg="#f0f0f0", fg="black").pack(anchor="w", pady=(5,0))
            e = tk.Entry(self.scrollable_frame, bg="white", fg="black", insertbackground="black")
            e.pack(pady=2, fill=tk.X)
            self.entries[key] = e

        create_entry("Yaş", "age")
        
        tk.Label(self.scrollable_frame, text="Cinsiyet", bg="#f0f0f0", fg="black").pack(anchor="w", pady=(5,0))
        self.cb_gender = ttk.Combobox(self.scrollable_frame, values=["Erkek", "Kadın"], state="readonly")
        self.cb_gender.set("Erkek")
        self.cb_gender.pack(pady=2, fill=tk.X)

        create_entry("Boy (cm)", "height")
        create_entry("Kilo (kg)", "weight")
        create_entry("Büyük Tansiyon (mmHg)", "sysBP")
        create_entry("Küçük Tansiyon (mmHg)", "diaBP")
        create_entry("Nabız (BPM)- Atım/Dakika", "heartRate")
        
        tk.Label(self.scrollable_frame, text="Kan Değerleri", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="#003366").pack(anchor="w", pady=(15,5))
        create_entry("Açlık Şekeri (Glukoz) - mg/dL", "glucose")
        create_entry("Toplam Kolesterol (mg/dL)", "totChol")
        create_entry("LDL (Kötü Kolesterol)- mg/dL", "LDL")
        create_entry("HDL (İyi Kolesterol)- mg/dL", "HDL")
        create_entry("Trigliserit (mg/dL)", "triglycerides")
        self.entries['triglycerides'].insert(0, "150.0")

        tk.Label(self.scrollable_frame, text="Yaşam Tarzı & Geçmiş", font=("Arial", 10, "bold"), bg="#f0f0f0", fg="#003366").pack(anchor="w", pady=(15,5))
        
        # ---  TUZ GİRİŞ ALANI ---
        tk.Label(self.scrollable_frame, text="Tuz Kullanımı", bg="#f0f0f0", fg="black").pack(anchor="w", pady=(5,0))
        
        frame_tuz = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        frame_tuz.pack(fill=tk.X, pady=2)

        # 1. Miktar Girişi (Entry) - SOLDA
        self.entry_tuz_miktar = tk.Entry(frame_tuz, width=8, bg="white", fg="black", insertbackground="black", font=("Arial", 11), justify="center")
        self.entry_tuz_miktar.insert(0, "1") # Varsayılan değer
        self.entry_tuz_miktar.pack(side=tk.LEFT, padx=(0, 5))

        # 2. Birim Seçimi (Combobox) - SAĞDA
        self.cb_tuz_birim = ttk.Combobox(frame_tuz, values=list(self.tuz_donusum_tablosu.keys()), state="readonly")
        self.cb_tuz_birim.set("Tatlı Kaşığı (Tepeleme)") # Varsayılan
        self.cb_tuz_birim.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 3. Bilgi Etiketi (Otomatik Hesaplama) - ALTTA
        self.lbl_tuz_gram = tk.Label(self.scrollable_frame, text="Toplam: 9.0 gram", bg="#f0f0f0", fg="gray", font=("Arial", 9, "italic"))
        self.lbl_tuz_gram.pack(anchor="w", pady=(0, 5))

        # Olayları Bağla (Her değişimde hesaplasın)
        self.entry_tuz_miktar.bind("<KeyRelease>", self.tuz_hesapla_guncelle)
        self.cb_tuz_birim.bind("<<ComboboxSelected>>", self.tuz_hesapla_guncelle)

        tk.Label(self.scrollable_frame, text="Sigara Kullanımı", bg="#f0f0f0", fg="black").pack(anchor="w")
        self.cb_smoking = ttk.Combobox(self.scrollable_frame, values=["İçmiyor", "Bırakmış", "İçiyor"], state="readonly")
        self.cb_smoking.set("İçmiyor")
        self.cb_smoking.pack(pady=2, fill=tk.X)

        create_entry("Günlük Ortalama Alkol (Bardak Sayısı)", "alcohol")
        self.entries['alcohol'].delete(0, tk.END)
        self.entries['alcohol'].insert(0, "0.0")

        create_entry("Günlük Uyku Süresi (Saat)", "sleep")
        self.entries['sleep'].insert(0, "7.0")

        create_entry("Günlük Aktivite Süresi (Dakika)", "activity_min")
        self.entries['activity_min'].insert(0, "30.0") 

        tk.Label(self.scrollable_frame, text="Ailede Kalp Hastalığı Var mı?", bg="#f0f0f0", fg="black").pack(anchor="w")
        self.cb_genetic = ttk.Combobox(self.scrollable_frame, values=["Hayır", "Evet"], state="readonly")
        self.cb_genetic.set("Hayır")
        self.cb_genetic.pack(pady=2, fill=tk.X)

        # --- MEVCUT DURUM SORULARI ---
        tk.Label(self.scrollable_frame, text="Hipertansiyon Hastası mısınız?", bg="#f0f0f0", fg="red").pack(anchor="w", pady=(10,0))
        self.cb_hypertension = ttk.Combobox(self.scrollable_frame, values=["Hayır", "Evet"], state="readonly")
        self.cb_hypertension.set("Hayır")
        self.cb_hypertension.pack(pady=2, fill=tk.X)

        tk.Label(self.scrollable_frame, text="Diyabet (Şeker) Hastası mısınız?", bg="#f0f0f0", fg="red").pack(anchor="w")
        self.cb_diabetes = ttk.Combobox(self.scrollable_frame, values=["Hayır", "Evet"], state="readonly")
        self.cb_diabetes.set("Hayır")
        self.cb_diabetes.pack(pady=2, fill=tk.X)
        # -----------------------------

        tk.Button(self.scrollable_frame, text="ANALİZİ BAŞLAT", bg="#2980b9", fg="white", font=("Arial", 11, "bold"), command=self.analiz_yap).pack(pady=20, fill=tk.X)
        self.btn_oneri = tk.Button(self.scrollable_frame, text="💡 İyileştirme Önerileri", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), state="disabled", command=self.oneri_goster)
        self.btn_oneri.pack(pady=5, fill=tk.X)
        self.btn_pdf = tk.Button(self.scrollable_frame, text="Detaylı Rapor (PDF)", bg="#c0392b", fg="white", state="disabled", command=self.pdf_rapor_olustur)
        self.btn_pdf.pack(pady=5, fill=tk.X)
        self.lbl_sonuc = tk.Label(self.scrollable_frame, text="", bg="#f0f0f0", fg="black", justify="left", font=("Arial", 10))
        self.lbl_sonuc.pack(pady=10)

        self.graph_frame = tk.Frame(self.tab1, bg="white")
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.grafik_yonetici = GrafikCizici(self.graph_frame)

    def tuz_hesapla_guncelle(self, event=None):
        """Kullanıcı giriş yaptıkça tuz miktarını canlı hesaplar"""
        try:
            miktar_text = self.entry_tuz_miktar.get()
            if not miktar_text:
                self.lbl_tuz_gram.config(text="Toplam: 0.0 gram")
                return

            miktar = float(miktar_text)
            secilen_birim = self.cb_tuz_birim.get()
            carpan = self.tuz_donusum_tablosu.get(secilen_birim, 1.0)
            
            toplam_tuz = miktar * carpan
            self.lbl_tuz_gram.config(text=f"Toplam: {toplam_tuz:.1f} gram", fg="gray")
        except ValueError:
            self.lbl_tuz_gram.config(text="Lütfen sayı giriniz", fg="red")

    def analiz_yap(self):
        try:
            # 1. VERİLERİ TOPLA
            vals = {}
            required_keys = ['age', 'height', 'weight', 'sysBP', 'diaBP', 'heartRate', 'glucose', 'totChol', 'LDL', 'HDL', 'triglycerides', 'alcohol', 'sleep', 'activity_min']

            # Standart verileri döngüyle al
            for k, entry in self.entries.items():
                val = entry.get()
                if not val and k in required_keys:
                    messagebox.showwarning("Eksik Veri", f"Alan boş bırakılamaz: {k}")
                    return
                elif val:
                    vals[k] = float(val)

            # --- TUZ HESAPLAMA  ---
            try:
                tuz_miktar = float(self.entry_tuz_miktar.get())
                secilen_birim = self.cb_tuz_birim.get()
                vals['salt'] = tuz_miktar * self.tuz_donusum_tablosu.get(secilen_birim, 1.0)
            except ValueError:
                messagebox.showwarning("Hata", "Lütfen tuz miktarını sayısal olarak girin.")
                return

            # Hesaplamalar
            bmi = vals['weight'] / ((vals['height']/100) ** 2)
            vals['BMI'] = bmi
            
            # Kategorik Dönüşümler
            gender_val = 1 if self.cb_gender.get() == "Erkek" else 0
            
            smk_map = {"İçmiyor": 0, "Bırakmış": 1, "İçiyor": 2}
            smoking_val = smk_map[self.cb_smoking.get()]
            
            genetic_val = 1 if self.cb_genetic.get() == "Evet" else 0
            
            # Aktivite Seviyesini Dakikadan 1-4 arasına çevir (Dataset uyumu için)
            act_min = vals['activity_min']
            if act_min < 30: act_lvl = 1
            elif act_min < 60: act_lvl = 2
            elif act_min < 90: act_lvl = 3
            else: act_lvl = 4

            # Hastalık Durumları
            has_htn = 1 if self.cb_hypertension.get() == "Evet" else 0
            has_dm = 1 if self.cb_diabetes.get() == "Evet" else 0

            # --- MODEL İÇİN SÖZLÜK OLUŞTURMA (Kaggle Dataset Sütun İsimleriyle) ---
            # Kullanıcıdan alınan tüm değerleri burada eşliyoruz
            user_data_for_model = {
                'Age': vals['age'],
                'BMI': bmi,
                'Systolic_BP': vals['sysBP'],
                'Diastolic_BP': vals['diaBP'],
                'Cholesterol': vals['totChol'],
                'LDL': vals['LDL'],
                'HDL': vals['HDL'],
                'Triglycerides': vals['triglycerides'],
                'Glucose': vals['glucose'],
                'Heart_Rate': vals['heartRate'],
                'Salt_Intake': vals['salt'],
                'Alcohol_Intake': vals['alcohol'] * 7.0,
                'Sleep_Duration': vals['sleep'],
                'Physical_Activity_Level': act_lvl,
                'Gender_Male': gender_val,
                'Smoking_Num': smoking_val,
                'Family_History_Num': genetic_val
            }

            sonuc_metni = ""
            risk_htn, risk_dm = 0, 0

            # ================= 4 SENARYO ANALİZİ =================

            df_benzer = self.veri_isleyici.get_benzer_kisiler(
                age=vals['age'], 
                gender=gender_val, 
                limit=500
            )

            # SENARYO 1: Hipertansiyon VAR, Diyabet YOK
            # Hedef: Diyabet riskini hesapla + Etki faktörleri
            if has_htn and not has_dm:
                risk_dm = self.veri_isleyici.tahmin_et_dm(user_data_for_model, htn_status=1)
                etkiler = self.veri_isleyici.get_etki_analizi(user_data_for_model, target='dm', existing_condition=1)
                
                sonuc_metni = f"Mevcut Durum: Hipertansiyon Hastası\n🛡️ DİYABET RİSKİ: %{risk_dm:.1f}"
                
                self.grafik_yonetici.ciz_tekil_risk_analizi(
                    df_similar=df_benzer, 
                    user_x=vals['age'], 
                    user_y=vals['glucose'], 
                    risk_score=risk_dm, 
                    etki_dict=etkiler, 
                    mod="dm"
                )

            # SENARYO 2: Hipertansiyon YOK, Diyabet VAR
            # Hedef: Hipertansiyon riskini hesapla + Etki faktörleri
            elif not has_htn and has_dm:
                risk_htn = self.veri_isleyici.tahmin_et_htn(user_data_for_model, diabetes_status=1)
                etkiler = self.veri_isleyici.get_etki_analizi(user_data_for_model, target='htn', existing_condition=1)
                
                sonuc_metni = f"Mevcut Durum: Diyabet Hastası\n🛡️ TANSİYON RİSKİ: %{risk_htn:.1f}"
                
                self.grafik_yonetici.ciz_tekil_risk_analizi(
                    df_similar=df_benzer, 
                    user_x=vals['age'], 
                    user_y=vals['sysBP'], 
                    risk_score=risk_htn, 
                    etki_dict=etkiler, 
                    mod="htn"
                )

            # SENARYO 3: İkisi de YOK (Sağlıklı Görünüyor)
            # Hedef: İkisinin de riskini hesapla + İkisinin de faktörlerini göster
            elif not has_htn and not has_dm:
                risk_htn = self.veri_isleyici.tahmin_et_htn(user_data_for_model, diabetes_status=0)
                risk_dm = self.veri_isleyici.tahmin_et_dm(user_data_for_model, htn_status=0)
                
                etkiler_htn = self.veri_isleyici.get_etki_analizi(user_data_for_model, target='htn', existing_condition=0)
                etkiler_dm = self.veri_isleyici.get_etki_analizi(user_data_for_model, target='dm', existing_condition=0)

                sonuc_metni = f"❤️ TANSİYON RİSKİ: %{risk_htn:.1f}\n🩸 DİYABET RİSKİ: %{risk_dm:.1f}"
                
                self.grafik_yonetici.ciz_ikili_risk_dashboard(
                    df_similar=df_benzer,
                    user_age=vals['age'],
                    user_bp=vals['sysBP'],
                    user_glc=vals['glucose'],
                    risk_htn=risk_htn,
                    risk_dm=risk_dm,
                    etki_htn=etkiler_htn,
                    etki_dm=etkiler_dm
                )
            # SENARYO 4: İkisi de VAR
            # Hedef: Risk hesabı anlamsız. "Sağlık Yönetimi Dashboard" göster.
            else:
                sonuc_metni = "⚠️ İki kronik rahatsızlık mevcut.\nRisk yerine değerlerinizin ideal aralıklara\nolan uzaklığı analiz edildi."
                self.grafik_yonetici.ciz_saglik_yonetimi(user_data_for_model)

            self.lbl_sonuc.config(text=sonuc_metni, fg="blue")
            
            # PDF ve CSV Kayıt için verileri sakla
            self.son_analiz_sonuclari = {
                'vals': vals, 
                'bmi': bmi, 
                'risk_htn': risk_htn, 
                'risk_dm': risk_dm, 
                'has_htn': has_htn, 
                'has_dm': has_dm,
                'msg': sonuc_metni
            }
            
            # --- BUTONLARI AKTİF ET ---
            self.btn_pdf.config(state="normal")   # PDF Butonunu aç
            try:
                self.btn_oneri.config(state="normal") # Öneri Butonunu aç 
            except AttributeError:
                pass # Eğer butonu henüz eklemediysen hata vermesin diye
            # --------------------------
            
            if max(risk_htn, risk_dm) > 0:
                self.kaydet(vals, max(risk_htn, risk_dm))

        except ValueError as ve:
             messagebox.showerror("Hata", f"Değer hatası: {ve}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Hata", f"Beklenmedik hata: {e}")
    
    def oneri_goster(self):
        if not self.son_analiz_sonuclari:
            return

        data = self.son_analiz_sonuclari
        vals = data['vals']
        bmi = data['bmi']
        oneriler = []

        # --- VERİ SETİ SÜTUNLARIYLA EŞLEŞEN KONTROLLER ---

        # 1. Kilo ve BMI (Dataset: BMI)
        if bmi > 30:
            oneriler.append("🔴 Obezite (BMI > 30): Kilo vermek, tansiyon riskini yönetmenin en etkili yoludur. Vücut ağırlığının %10'unu kaybetmek tansiyonu düşürebilir.")
        elif bmi > 25:
            oneriler.append("🟠 Fazla Kilo (BMI 25-30): İdeal kilonun üzerindesiniz. Sağlıklı beslenme ile kilo kontrolü sağlamalısınız.")

        # 2. Tansiyon (Dataset: Systolic_BP, Diastolic_BP)
        if vals['sysBP'] >= 140 or vals['diaBP'] >= 90:
            oneriler.append("🔴 Yüksek Tansiyon: Ölçümleriniz hipertansiyon sınırında. Mutlaka doktor kontrolü, tuz kısıtlaması ve düzenli ilaç kullanımı gerekebilir.")
        elif vals['sysBP'] >= 120 and vals['sysBP'] < 140:
            oneriler.append("🟠 Pre-Hipertansiyon: Tansiyonunuz sınıra yakın. Düzenli takip yapın ve stresi yönetmeye çalışın.")

        # 3. Tuz Tüketimi (Dataset: Salt_Intake)
        if vals['salt'] > 5.0:
            oneriler.append(f"🧂 Tuz Tüketimi: Günlük {vals['salt']:.1f} gr tuz alıyorsunuz. WHO önerisi max 5 gr'dır. Tuzu azaltmak tansiyonu doğrudan 5-10 mmHg düşürür.")

        # 4. Şeker ve Diyabet (Dataset: Glucose)
        if vals['glucose'] > 126:
             oneriler.append("🩸 Yüksek Şeker: Açlık şekeriniz diyabet sınırında veya üzerinde. Karbonhidratı azaltmalı ve endokrin kontrolüne gitmelisiniz.")
        elif vals['glucose'] > 100:
             oneriler.append("⚠️ İnsülin Direnci Riski: Şekeriniz 100-125 aralığında. Lifli gıdalar tüketin ve şekerli içecekleri bırakın.")

        # 5. Kolesterol ve Trigliserit (Dataset: Cholesterol, LDL, Triglycerides)
        if vals['LDL'] > 130 or vals['totChol'] > 200:
            oneriler.append("🍔 Yüksek Kolesterol: Damar tıkanıklığı riski. Doymuş yağlardan (margarin, sakatat, kızartma) uzak durun.")
        
        if vals['triglycerides'] > 150:
             oneriler.append("⚠️ Yüksek Trigliserit: Kan yağlarınız yüksek. Hamur işi, tatlı ve alkolü sınırlandırmalısınız.")

        # 6. Fiziksel Aktivite (Dataset: Physical_Activity_Level)
        # Not: Dataset level (1-4) tutar ama biz kullanıcıya dakika üzerinden öneri veriyoruz, bu daha anlaşılır.
        if vals['activity_min'] < 30:
            oneriler.append("🏃 Hareketsizlik: Günlük aktiviteniz yetersiz. Kalp sağlığı için günde en az 30 dakika orta tempolu yürüyüş şarttır.")

        # 7. Uyku Düzeni (Dataset: Sleep_Duration) 
        if vals['sleep'] < 6:
            oneriler.append("g😴 Yetersiz Uyku: Günde 6 saatten az uyumak stresi ve tansiyonu artırır. Günde 7-8 saat uyumaya özen gösterin.")
        elif vals['sleep'] > 9:
            oneriler.append("💤 Aşırı Uyku: 9 saatten fazla uyku da metabolizmayı yavaşlatabilir ve kalp riskini artırabilir.")

        # 8. Alkol (Dataset: Alcohol_Intake)
        if vals['alcohol'] > 0:
            oneriler.append("🍷 Alkol Tüketimi: Alkol kan basıncını ve trigliseridi yükseltir. Mümkünse bırakılmalı veya sınırlandırılmalıdır.")

        # 9. Sigara (Dataset: Smoking_Status)
        if self.cb_smoking.get() == "İçiyor":
            oneriler.append("🚬 Sigara: Sigara damar yapısını bozar ve pıhtı riskini artırır. Bırakmak için profesyonel destek alabilirsiniz.")

        # HİÇBİR SORUN YOKSA
        if not oneriler:
            oneriler.append("✅ Mükemmel: Tüm değerleriniz sağlıklı aralıklarda. Bu yaşam tarzını koruyarak düzenli kontrollere devam edin.")

        # --- PENCERE TASARIMI ---
        top = tk.Toplevel(self.root)
        top.title("Kişiselleştirilmiş Sağlık Önerileri")
        top.geometry("650x550")
        top.configure(bg="#ecf0f1")

        tk.Label(top, text=f"Sayın {self.kullanici_adi.replace('_', ' ')} için Analiz ve Öneriler", 
                 font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=10)

        # Scrollbar eklenmiş metin alanı 
        frame_txt = tk.Frame(top)
        frame_txt.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_txt)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(frame_txt, font=("Arial", 11), bg="white", fg="#2c3e50", 
                            padx=10, pady=10, yscrollcommand=scrollbar.set)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_area.yview)

        # Önerileri Yazdır
        for oneri in oneriler:
            text_area.insert(tk.END, "• " + oneri + "\n\n")
            
            # Renklendirme
            current_line = int(text_area.index('end-1c').split('.')[0]) - 2 # Son eklenen satırın indeksi
            if "🔴" in oneri:
                text_area.tag_add("red", f"{current_line}.0", f"{current_line}.end")
            elif "⚠️" in oneri or "🟠" in oneri:
                text_area.tag_add("orange", f"{current_line}.0", f"{current_line}.end")
            elif "✅" in oneri:
                text_area.tag_add("green", f"{current_line}.0", f"{current_line}.end")

        text_area.tag_config("red", foreground="#c0392b", font=("Arial", 11, "bold"))     # Koyu Kırmızı
        text_area.tag_config("orange", foreground="#d35400", font=("Arial", 11, "bold"))  # Turuncu
        text_area.tag_config("green", foreground="#27ae60", font=("Arial", 11, "bold"))   # Yeşil
        
        text_area.configure(state="disabled") 

        tk.Button(top, text="Kapat", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), command=top.destroy).pack(pady=10)
    
    def metin_temizle(self, text):
        """Türkçe karakterleri İngilizceye çevirir ve emojileri temizler."""
        if not isinstance(text, str):
            return str(text)
            
        # 1. Türkçe Karakter Dönüşümü
        tr_map = {
            'ı': 'i', 'İ': 'I', 'ş': 's', 'Ş': 'S', 'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
        }
        for tr, en in tr_map.items():
            text = text.replace(tr, en)
            
        # 2. Emojileri Temizle (Standart PDF fontları emojileri basamaz)
        emojis = ['🛡️', '🩸', '❤️', '⚠️', '🔴', '🟠', '✅', '🍔', '🏃', 'g😴', '😴', '💤', '🍷', '🚬', '💡', '■']
        for emoji in emojis:
            text = text.replace(emoji, "")
            
        return text.strip() 

    def pdf_rapor_olustur(self):
        if not self.son_analiz_sonuclari: return
        data = self.son_analiz_sonuclari
        vals = data['vals']
        
        # Dosya ismindeki Türkçe karakterleri de temizle
        clean_name = self.metin_temizle(self.kullanici_adi).replace(" ", "_")
        pdf_path = PDF_DIR / f"Rapor_{clean_name}.pdf"

        
        try:
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            width, height = A4
            
            # --- BAŞLIK ---
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width/2, 800, "SAGLIK RISK ANALIZI VE ONERI RAPORU")
            
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2, 780, f"Rapor Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            # İsim kısmını temizle
            c.drawCentredString(width/2, 765, f"Danisan: {self.metin_temizle(self.kullanici_adi).replace('_', ' ')}")
            
            c.line(50, 750, 550, 750) # Çizgi

            # --- 1. GİRİLEN KLİNİK DEĞERLER ---
            y = 720
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "1. KLINIK DEGERLERINIZ")
            y -= 25
            
            c.setFont("Helvetica", 10)
            # Değerleri yazdırırken metin temizlemeye gerek yok çünkü zaten sayısal veya ingilizce formatta
            # Ancak label kısımlarını garanti olsun diye ingilizce karakter kullanıyoruz
            c.drawString(50, y, f"Yas: {int(vals['age'])}")
            c.drawString(50, y-15, f"BMI (Kilo Indeksi): {data['bmi']:.1f}")
            c.drawString(50, y-30, f"Tansiyon: {int(vals['sysBP'])}/{int(vals['diaBP'])} mmHg")
            c.drawString(50, y-45, f"Nabiz: {int(vals['heartRate'])} bpm")
            
            c.drawString(220, y, f"Aclik Sekeri: {int(vals['glucose'])} mg/dL")
            c.drawString(220, y-15, f"T. Kolesterol: {int(vals['totChol'])} mg/dL")
            c.drawString(220, y-30, f"LDL / HDL: {int(vals['LDL'])} / {int(vals['HDL'])}(mg/dL)")
            c.drawString(220, y-45, f"Trigliserit: {int(vals['triglycerides'])} mg/dL")
            
            c.drawString(400, y, f"Tuz Tuketimi: {vals['salt']:.1f} g/gun")
            c.drawString(400, y-15, f"Uyku Suresi: {vals['sleep']} saat")
            c.drawString(400, y-30, f"Aktivite: {int(vals['activity_min'])} dk/gun")
            
            y -= 70
            c.line(50, y, 550, y)

            # --- 2. ANALİZ SONUCU VE RİSK DURUMU ---
            y -= 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "2. ANALIZ SONUCU")
            y -= 25
            
            # BURADA TEMİZLEME YAPIYORUZ
            # data['msg'] içindeki emojileri silip Türkçe karakterleri düzeltecek
            clean_msg = self.metin_temizle(data['msg'])
            
            c.setFont("Helvetica", 11)
            lines = clean_msg.split('\n')
            for line in lines:
                # Renklendirme mantığı (RISK kelimesini temizledikten sonra kontrol et)
                if "RISK" in line or "RISKI" in line: c.setFillColorRGB(0.8, 0, 0) 
                else: c.setFillColorRGB(0, 0, 0)
                
                c.drawString(50, y, line)
                y -= 15
            
            y -= 20
            c.setFillColorRGB(0, 0, 0)
            c.line(50, y, 550, y)

            # --- 3. KAPSAMLI ÖZET ---
            y -= 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "3. KAPSAMLI RISK DEGERLENDIRMESI")
            y -= 20
            
            c.setFont("Helvetica", 10)
            ozet_metni = []
            
            if vals['sysBP'] > 130 or vals['diaBP'] > 85:
                ozet_metni.append("- Tansiyon degerleriniz ideal sinirin uzerinde.")
            if vals['glucose'] > 100:
                ozet_metni.append("- Kan sekeri seviyeniz prediyabet veya diyabet sinirlarinda.")
            if data['bmi'] > 25:
                ozet_metni.append("- Kilo indeksiniz normalin uzerinde.")
            if vals['LDL'] > 130 or vals['triglycerides'] > 150:
                ozet_metni.append("- Kan yaglariniz (Kolesterol/Trigliserit) yuksek.")
            
            if not ozet_metni:
                ozet_metni.append("- Genel klinik tablonuz saglikli gorunuyor.")
            else:
                ozet_metni.append("- Yukaridaki risk faktorleri metabolik sendrom riski olusturabilir.")

            for madde in ozet_metni:
                # Burada da temizleme fonksiyonunu çağırıyoruz
                c.drawString(50, y, self.metin_temizle(madde))
                y -= 15

            y -= 20
            c.line(50, y, 550, y)

            # --- 4. YASAM TARZI NOTLARI ---
            y -= 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "4. YASAM TARZI VE ONERILER")
            y -= 20
            
            c.setFont("Helvetica", 10)
            oneri_metni = []
            
            if vals['salt'] > 5:
                oneri_metni.append("* Tuz kullanimini azaltin (Gunde 1 tatli kasigini gecmemeli).")
            if vals['sleep'] < 7:
                oneri_metni.append("* Uyku duzeninizi iyilestirin.")
            if vals['activity_min'] < 30:
                oneri_metni.append("* Fiziksel aktiviteniz yetersiz. Haftada en az 150 dk yuruyus yapin.")
            if data.get('smoking', 0) == 2: # Eğer smoking verisini kaydettiysen
                oneri_metni.append("* Sigara kullanimini birakmak icin destek alin.")
            if vals['sysBP'] > 120:
                oneri_metni.append("* DASH diyeti tansiyonu dengelemeye yardimci olur.")

            if not oneri_metni:
                oneri_metni.append("* Yasam tarzi aliskanliklariniz gayet iyi.")

            for oneri in oneri_metni:
                c.drawString(50, y, self.metin_temizle(oneri))
                y -= 15

            # --- DİPNOT ---
            c.setFont("Helvetica-Oblique", 8)
            c.drawCentredString(width/2, 50, "Bu rapor yapay zeka destekli bir analizdir. Kesin tani icin doktorunuza basvurunuz.")

            c.save()
            if platform.system() == 'Windows':
                os.startfile(str(pdf_path))
            else:
                subprocess.call(['open', str(pdf_path)])
            
        except Exception as e: messagebox.showerror("Hata", str(e))
    def kaydet(self, vals, risk):
        exists = os.path.exists(self.dosya_adi)
        try:
            with open(self.dosya_adi, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # DOKTOR İÇİN GENİŞLETİLMİŞ BAŞLIKLAR
                # Not: Grafiğin bozulmaması için 'SysBP' ve 'DiaBP' isimlerini koruduk.
                basliklar = [
                    "Tarih", 
                    "SysBP", "DiaBP", "Risk_Skoru",  # Temel Grafikler İçin
                    "Nabiz", "Seker", "BMI", "Kilo", # Klinik Önemli
                    "Kolesterol", "LDL", "HDL", "Trigliserit", # Kan Yağları
                    "Tuz_Gr", "Sigara", "Alkol", "Uyku", "Aktivite", # Yaşam Tarzı
                    "Yas", "Cinsiyet", "Aile_Oykusu" # Demografik
                ]
                
                if not exists: 
                    writer.writerow(basliklar)
                
                # VERİ SATIRINI HAZIRLA
                tarih_saat = datetime.now().strftime("%d.%m.%Y %H:%M")
                
                veri_satiri = [
                    tarih_saat,
                    int(vals['sysBP']),
                    int(vals['diaBP']),
                    f"{risk:.1f}",
                    int(vals['heartRate']),
                    int(vals['glucose']),
                    f"{vals['BMI']:.1f}",
                    vals['weight'],
                    vals['totChol'],
                    vals['LDL'],
                    vals['HDL'],
                    vals['triglycerides'],
                    f"{vals['salt']:.1f}",       # Tuz (Gram cinsinden)
                    self.cb_smoking.get(),       # Sigara Durumu (Yazı olarak)
                    vals['alcohol'],             # Alkol (Bardak)
                    vals['sleep'],               # Uyku (Saat)
                    vals['activity_min'],        # Aktivite (Dakika)
                    int(vals['age']),
                    self.cb_gender.get(),        # Cinsiyet (Yazı olarak)
                    self.cb_genetic.get()        # Aile Öyküsü (Yazı olarak)
                ]
                
                writer.writerow(veri_satiri)
                
        except Exception as e:
            print(f"Kayıt hatası: {e}")
            messagebox.showerror("Kayıt Hatası", str(e))

    def on_tab_change(self, event):
        if self.tab_control.index("current") == 1 and os.path.exists(self.dosya_adi):
            try:
                df = pd.read_csv(self.dosya_adi)
                self.grafik_yonetici_gecmis.ciz_gecmis_trend(df)
            except: pass

if __name__ == "__main__":
    root_login = tk.Tk()
    login = LoginPenceresi(root_login)
    root_login.mainloop()
    
    if login.kullanici_adi:
        root_main = tk.Tk()
        app = HipertansiyonApp(root_main, login.kullanici_adi)
        root_main.mainloop()