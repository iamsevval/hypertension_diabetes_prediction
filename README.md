# 🩺 Hypertension & Diabetes Prediction System

Bu proje, kullanıcıların temel sağlık verilerini (yaş, cinsiyet, BMI, tuz tüketimi vb.) analiz ederek hipertansiyon ve diyabet risklerini yapay zeka destekli modellerle tahmin eden bir masaüstü uygulamasıdır.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Proje Hakkında

**Hypertension & Diabetes Prediction**, erken teşhisin öneminden yola çıkarak geliştirilmiş bir sağlık asistanıdır. Kaggle veri setleri ile eğitilen Lojistik Regresyon modeli, kullanıcıdan alınan girdileri işler ve olası risk durumlarını yüzdesel olarak sunar.

### Temel Özellikler
* **Anlık Risk Analizi:** Girilen verilere göre hipertansiyon ve diyabet riskini saniyeler içinde hesaplar.
* **Kullanıcı Dostu Arayüz (GUI):** Tkinter ile tasarlanmış, herkesin kolayca kullanabileceği sade bir arayüz.
* **Görselleştirme:** Matplotlib grafikleri ile sağlık verilerinin analizi.
* **Veri Kaydı:** Kullanıcı verilerini CSV formatında saklayarak geçmiş takibi yapma imkanı.

## 🛠️ Kullanılan Teknolojiler

* **Python:** Ana programlama dili.
* **Tkinter:** Grafiksel kullanıcı arayüzü (GUI).
* **Scikit-learn:** Makine öğrenmesi modeli (Logistic Regression).
* **Pandas & NumPy:** Veri işleme ve analizi.
* **Matplotlib:** Grafik ve veri görselleştirme.

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

