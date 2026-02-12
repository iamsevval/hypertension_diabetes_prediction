# 🩺 Hypertension & Diabetes Prediction System

Bu proje, kullanıcıların temel sağlık verilerini (yaş, cinsiyet, BMI, tuz tüketimi vb.) analiz ederek hipertansiyon ve diyabet risklerini yapay zeka destekli modellerle tahmin eden bir masaüstü uygulamasıdır.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Proje Hakkında

**Hypertension & Diabetes Prediction**, erken teşhisin hayat kurtarıcı öneminden yola çıkarak; kullanıcıların temel sağlık verilerini ve yaşam tarzı alışkanlıklarını analiz edip, olası Hipertansiyon (HTN) ve Diyabet (DM) risklerini yapay zeka destekli modellerle tahmin eden masaüstü tabanlı bir Karar Destek Sistemidir.  Kaggle veri setleri ile eğitilen Lojistik Regresyon modeli, kullanıcıdan alınan girdileri işler ve olası risk durumlarını yüzdesel olarak sunar.
<img width="1512" height="982" alt="1" src="https://github.com/user-attachments/assets/179076ef-f34e-4697-9b01-0f4c17351bb8" />


### Temel Özellikler
* **Anlık Risk Analizi:** Girilen verilere göre hipertansiyon ve diyabet riskini saniyeler içinde hesaplar.
* **Senaryo Bazlı Simülasyon:** Sistem, kullanıcının mevcut durumunu (Tam Sağlıklı, Sadece HTN vb.) algılar ve buna göre "Hipertansiyon var ama Diyabet riski nedir?" gibi çapraz sorgulamalar yapar. 
* **Kullanıcı Dostu Arayüz (GUI):** Tkinter ile tasarlanmış, herkesin kolayca kullanabileceği sade bir arayüz.
* **Görselleştirme:** Matplotlib grafikleri ile sağlık verilerinin analizi.
* **Veri Kaydı:** Kullanıcı verilerini CSV formatında saklayarak geçmiş takibi yapma imkanı.
<img width="1512" height="982" alt="2" src="https://github.com/user-attachments/assets/6abe6fea-44df-4ae4-a5be-e0d440cb485a" />


## 🛠️ Kullanılan Teknolojiler

* **Python:** Ana programlama dili.
* **Tkinter:** Grafiksel kullanıcı arayüzü (GUI).
* **Scikit-learn:** Makine öğrenmesi modeli (Logistic Regression, Class Weighting).
* **Pandas & NumPy:** Veri işleme ve analizi.
* **Matplotlib:** Grafik ve veri görselleştirme.
* **ReportLab:** Dinamik PDF rapor üretimi.

Sadece matematiksel bir olasılık hesabı yapmakla kalmayıp, kullanıcının "Tuz tüketimim riski ne kadar artırıyor?"sorusuna görsel yanıtlar veren bu çalışma, teorik makine öğrenmesi algoritmalarının son kullanıcıya hitap eden pratik bir yazılıma dönüşümünü temsil etmektedir.
<img width="1512" height="982" alt="4" src="https://github.com/user-attachments/assets/bc32d333-a5de-4494-a0cd-2837d293bf64" />


## 📂 Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1.  **Projeyi Klonlayın:**
    ```bash
    git clone [https://github.com/iamsevval/hypertension_diabetes_prediction.git](https://github.com/iamsevval/hypertension_diabetes_prediction.git)
    cd hypertension_diabetes_prediction
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install pandas numpy scikit-learn matplotlib
    ```

3.  **Uygulamayı Başlatın:**
    ```bash
    python main.py
    ```

## 📊 Veri Seti

Modelin eğitiminde Kaggle platformundan alınan [Hypertension Risk Prediction Dataset](https://www.kaggle.com/datasets/ankushpanday1/hypertension-risk-prediction-dataset) kullanılmıştır. Model şu parametreleri dikkate alır:
* Yaş & Cinsiyet
* Vücut Kitle İndeksi (BMI)
* Günlük Tuz ve Su Tüketimi
* Sigara ve Alkol Kullanımı

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak isterseniz:
1.  Bu repoyu **Fork** edin.
2.  Yeni bir **Branch** oluşturun (`git checkout -b feature/yeni-ozellik`).
3.  Değişikliklerinizi **Commit** edin (`git commit -m 'Yeni özellik eklendi'`).
4.  Branch'inizi **Push** edin (`git push origin feature/yeni-ozellik`).
5.  Bir **Pull Request** açın.

