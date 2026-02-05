import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np
import platform
import matplotlib.dates as mdates
import pandas as pd

# Font ayarları
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Arial'
else:
    plt.rcParams['font.family'] = 'DejaVu Sans'

class GrafikCizici:
    def __init__(self, frame):
        self.frame = frame

    def temizle(self):
        for widget in self.frame.winfo_children(): 
            widget.destroy()
        plt.close('all')

    def goster(self, fig):
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------------------------------------------------------
    # YARDIMCI: UZUN ETİKETLERİ BÖLME FONKSİYONU
    # ---------------------------------------------------------
    def etiket_bol(self, metin):
        """Uzun etiketleri \n ile iki satıra böler."""
        mapping = {
            'Büyük Tansiyon': 'Büyük\nTansiyon',
            'Küçük Tansiyon': 'Küçük\nTansiyon',
            'Kilo (BMI)': 'Kilo\n(BMI)',
            'Tansiyon Hastalığı': 'Tansiyon\nHastalığı',
            'Diyabet Hastalığı': 'Diyabet\nHastalığı',
            'Genetik': 'Genetik\nÖykü',
            'Hareketsizlik': 'Fiziksel\nHareketsizlik',
            'Tuz': 'Tuz\nTüketimi'
        }
        return mapping.get(metin, metin)

    # ---------------------------------------------------------
    # SENARYO 1 & 2: TEKİL RİSK
    # ---------------------------------------------------------
    def ciz_tekil_risk_analizi(self, df_similar, user_x, user_y, risk_score, etki_dict, mod="dm"):
        self.temizle()
        fig = plt.figure(figsize=(12, 8))
        gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 0.8])

        ax1 = fig.add_subplot(gs[0, 0]) # Konum Grafiği
        ax2 = fig.add_subplot(gs[0, 1]) # Risk Göstergesi
        ax3 = fig.add_subplot(gs[1, :]) # Etki Faktörleri

        # 1. KONUM GRAFİĞİ
        x_label = "Yaş"
        if mod == "dm":
            y_col = "Glucose"
            y_label = "Açlık Şekeri"
            title = f"Sizin Gibi Kişiler Arasındaki Konumunuz"
            target_col = "Target_DM"
        else: # htn
            y_col = "Systolic_BP"
            y_label = "Büyük Tansiyon"
            title = f"Sizin Gibi Kişiler Arasındaki Konumunuz"
            target_col = "Target_HTN"

        if df_similar is not None and not df_similar.empty:
            sagliklilar = df_similar[df_similar[target_col] == 0]
            ax1.scatter(sagliklilar['Age'], sagliklilar[y_col], 
                        c='#2ecc71', alpha=0.5, s=40, label='Sağlıklı Benzerler')

            hastalar = df_similar[df_similar[target_col] == 1]
            ax1.scatter(hastalar['Age'], hastalar[y_col], 
                        c='#e74c3c', alpha=0.6, s=40, label='Hasta Benzerler')
        
        ax1.scatter(user_x, user_y, c='gold', s=400, marker='*', 
                    edgecolor='black', zorder=10, label='SİZ (Konumunuz)')
        
        ax1.set_xlabel(x_label)
        ax1.set_ylabel(y_label)
        ax1.set_title(title, fontsize=10, fontweight='bold')
        ax1.legend(loc='upper left', frameon=True, fontsize=9)
        ax1.grid(alpha=0.3, linestyle='--')

        # 2. RİSK GÖSTERGESİ
        risk_color = '#2ecc71' if risk_score < 40 else '#f39c12' if risk_score < 70 else '#c0392b'
        ax2.bar(["RİSK SKORU"], [risk_score], color=risk_color, width=0.4)
        ax2.set_ylim(0, 100)
        ax2.axhline(50, color='red', ls='--', label='Yüksek Risk Sınırı')
        ax2.text(0, risk_score + 2, f'%{risk_score:.1f}', ha='center', fontweight='bold', fontsize=14)
        ax2.set_title(f"HESAPLANAN {'DİYABET' if mod=='dm' else 'TANSİYON'} RİSKİ")

        # 3. ETKİ FAKTÖRLERİ 
        sorted_factors = sorted(etki_dict.items(), key=lambda x: x[1], reverse=True)
        keys = [self.etiket_bol(x[0]) for x in sorted_factors] # Etiketleri böl
        vals = [x[1] for x in sorted_factors]
        colors_bar = ['#e74c3c' if v > 0 else '#2ecc71' for v in vals] 

        ax3.bar(keys, vals, color=colors_bar)
        ax3.set_title("Sizin Verilerinizin Riske Olan NET KATKISI (Sıfırın üstü riski artırır)", fontsize=11)
        ax3.axhline(0, color='black', linewidth=1)
        # Etiketler alt alta olduğu için rotasyona gerek kalmayabilir ama hafif eğiklik iyidir
        plt.setp(ax3.get_xticklabels(), rotation=0, ha='center', fontsize=9) 
        ax3.grid(axis='y', alpha=0.3)

        self.goster(fig)

    # ---------------------------------------------------------
    # SENARYO 3: İKİLİ RİSK
    # ---------------------------------------------------------
    def ciz_ikili_risk_dashboard(self, df_similar, user_age, user_bp, user_glc, risk_htn, risk_dm, etki_htn, etki_dm):
        self.temizle()
        fig = plt.figure(figsize=(13, 9))
        gs = fig.add_gridspec(3, 2) 

        # A) TANSİYON GRAFİĞİ
        ax_pos_bp = fig.add_subplot(gs[0, 0])
        if df_similar is not None:
            bp_saglam = df_similar[df_similar['Target_HTN'] == 0]
            ax_pos_bp.scatter(bp_saglam['Age'], bp_saglam['Systolic_BP'], 
                              c='#2ecc71', alpha=0.4, s=30, label='Sağlıklı')
            bp_hasta = df_similar[df_similar['Target_HTN'] == 1]
            ax_pos_bp.scatter(bp_hasta['Age'], bp_hasta['Systolic_BP'], 
                              c='#e74c3c', alpha=0.4, s=30, label='Tansiyon Hastası')
            ax_pos_bp.scatter(user_age, user_bp, c='gold', s=300, marker='*', 
                              edgecolor='black', label='SİZ')
            
            ax_pos_bp.set_title("Benzer Grubunuzda Tansiyon")
            ax_pos_bp.set_ylabel("Büyük Tansiyon")
            ax_pos_bp.legend(loc='upper left', fontsize=8)

        # B) ŞEKER GRAFİĞİ
        ax_pos_gl = fig.add_subplot(gs[0, 1])
        if df_similar is not None:
            gl_saglam = df_similar[df_similar['Target_DM'] == 0]
            ax_pos_gl.scatter(gl_saglam['Age'], gl_saglam['Glucose'], 
                              c='#2ecc71', alpha=0.4, s=30, label='Sağlıklı')
            gl_hasta = df_similar[df_similar['Target_DM'] == 1]
            ax_pos_gl.scatter(gl_hasta['Age'], gl_hasta['Glucose'], 
                              c='#e74c3c', alpha=0.4, s=30, label='Diyabet Hastası')
            ax_pos_gl.scatter(user_age, user_glc, c='gold', s=300, marker='*', 
                              edgecolor='black', label='SİZ')
            
            ax_pos_gl.set_title("Benzer Grubunuzda Şeker")
            ax_pos_gl.set_ylabel("Açlık Şekeri")
            ax_pos_gl.legend(loc='upper left', fontsize=8)

        # C) RİSK BARLARI
        ax_risk = fig.add_subplot(gs[1, :])
        ax_risk.bar(["Tansiyon Riski", "Diyabet Riski"], [risk_htn, risk_dm], 
                    color=['#e74c3c', '#3498db'], width=0.3)
        ax_risk.set_ylim(0, 100)
        ax_risk.axhline(50, color='gray', ls='--')
        ax_risk.text(0, risk_htn+1, f"%{risk_htn:.1f}", ha='center', fontsize=12, fontweight='bold')
        ax_risk.text(1, risk_dm+1, f"%{risk_dm:.1f}", ha='center', fontsize=12, fontweight='bold')
        ax_risk.set_title("Hesaplanan Riskler")

        # D) ETKİLER 
        ax_fac_htn = fig.add_subplot(gs[2, 0])
        ax_fac_dm = fig.add_subplot(gs[2, 1])

        def plot_factors(ax, effects, title):
            # En etkili 7 faktörü al
            sorted_f = sorted(effects.items(), key=lambda x: abs(x[1]), reverse=True)[:7]
            
            k = [self.etiket_bol(x[0]) for x in sorted_f] 
            v = [x[1] for x in sorted_f]

            c = ['#e74c3c' if val > 0 else '#2ecc71' for val in v]
            ax.barh(k, v, color=c)
            ax.set_title(title)
            ax.axvline(0, color='black', lw=0.8)
            ax.invert_yaxis()
            ax.tick_params(axis='y', labelsize=9) 

        plot_factors(ax_fac_htn, etki_htn, "Tansiyon Riskini En Çok Etkileyenler")
        plot_factors(ax_fac_dm, etki_dm, "Diyabet Riskini En Çok Etkileyenler")

        self.goster(fig)

    # ---------------------------------------------------------
    # SENARYO 4: SAĞLIK YÖNETİMİ (İKİSİ DE VAR)
    # ---------------------------------------------------------
    def ciz_saglik_yonetimi(self, user_vals):
        self.temizle()
        fig, ax = plt.subplots(figsize=(10, 6))
        metrics = [
            ('Sys BP', user_vals['Systolic_BP'], 120, 140),
            ('Dia BP', user_vals['Diastolic_BP'], 80, 90),
            ('Açlık Şekeri', user_vals['Glucose'], 90, 120),
            ('BMI', user_vals['BMI'], 22, 25),
            ('LDL Kolesterol', user_vals['LDL'], 100, 130),
            ('Trigliserit', user_vals['Triglycerides'], 150, 200)
        ]
        y_pos = np.arange(len(metrics))
        for i, (name, val, target, limit) in enumerate(metrics):
            ax.barh(i, target, color='#2ecc71', alpha=0.3, height=0.6, align='center', 
                    label='İdeal Aralık' if i==0 else "")
            
            ax.barh(i, limit-target, left=target, color='#f1c40f', alpha=0.3, height=0.6, align='center', 
                    label='Dikkat' if i==0 else "")
            
            ax.barh(i, max(val, limit*1.5)-limit, left=limit, color='#e74c3c', alpha=0.2, height=0.6, align='center',
                    label='Yüksek Risk' if i==0 else "")
            
            color = 'green' if val <= target else 'orange' if val <= limit else 'red'
            ax.plot(val, i, 'o', color=color, markersize=12, markeredgecolor='black')
            ax.text(val, i + 0.2, f"{int(val)}", ha='center', fontweight='bold', color='black')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([m[0] for m in metrics])
        ax.set_title("MEVCUT SAĞLIK DURUMU vs İDEAL HEDEFLER")
        ax.legend(loc='upper right')
        self.goster(fig)
    
    # ---------------------------------------------------------
    # GÜNCELLENEN FONKSİYON: ÇİFT EKSENLİ TREND GRAFİĞİ
    # ---------------------------------------------------------
    def ciz_gecmis_trend(self, df):
        self.temizle()
        if df is None or df.empty:
            tk.Label(self.frame, text="Henüz kaydedilmiş veri yok.").pack()
            return
        

        # Grafik alanını oluştur
        fig, ax1 = plt.subplots(figsize=(12, 6))

        try:
            # 1. Veri Hazırlığı
            df = df.copy() # Orijinal veriyi bozmamak için kopyala
            df['Tarih'] = pd.to_datetime(df['Tarih'])
            df = df.sort_values('Tarih')

            # Eğer dataframe içinde 'RiskScore' sütunu yoksa, hata vermemesi için rastgele veya 0 dolduralım
            if 'RiskScore' not in df.columns:
                df['RiskScore'] = (df['SysBP'] + df['DiaBP']) / 4  # Temsili hesap

            # -----------------------------------------------------
            # SOL EKSEN (AX1) - TANSİYON VERİLERİ
            # -----------------------------------------------------
            ln1 = ax1.plot(df['Tarih'], df['SysBP'], color='#c0392b', marker='o', 
                           linewidth=2, label='Büyük Tansiyon')
            ln2 = ax1.plot(df['Tarih'], df['DiaBP'], color='#2980b9', marker='o', 
                           linewidth=2, label='Küçük Tansiyon')

            # Hipertansiyon Sınırı (140)
            ln3 = ax1.axhline(y=140, color='gray', linestyle='--', alpha=0.5, label='Hipertansiyon Sınırı (140)')

            ax1.set_ylabel("Tansiyon (mmHg)", fontweight='bold')
            ax1.set_xlabel("Tarih", fontweight='bold')
            ax1.grid(True, alpha=0.3)

            # -----------------------------------------------------
            # SAĞ EKSEN (AX2) - RİSK SKORU
            # -----------------------------------------------------
            ax2 = ax1.twinx()  # X eksenini paylaşan ikinci bir Y ekseni yarat
            
            ln4 = ax2.plot(df['Tarih'], df['RiskScore'], color='#8e44ad', linestyle='--', 
                           marker='.', label='Risk Skoru (%)')
            
            ax2.set_ylabel("Risk Skoru (%)", color='#8e44ad', fontweight='bold')
            ax2.tick_params(axis='y', labelcolor='#8e44ad')
            ax2.set_ylim(0, 100)  # Risk skoru her zaman 0-100 arasındadır

            # -----------------------------------------------------
            # ORTAK LEJANT (İKİ EKSENİ BİRLEŞTİRME)
            # -----------------------------------------------------
            # Matplotlib'de iki eksen olunca lejantlar ayrı düşer, onları topluyoruz:
            lines = ln1 + ln2 + [ln3] + ln4
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left', frameon=True, fancybox=True, framealpha=0.9)

            # -----------------------------------------------------
            # TARİH FORMATI VE BAŞLIK
            # -----------------------------------------------------
            myFmt = mdates.DateFormatter('%d-%m-%Y\n%H:%M')
            ax1.xaxis.set_major_formatter(myFmt)
            ax1.set_xticks(df['Tarih'])
            plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")

            plt.title("Tansiyon Takip Grafiği ve Risk Analizi", fontsize=12, fontweight='bold')
            plt.tight_layout()

            self.goster(fig)
            
        except Exception as e:
            print(f"Grafik çizim hatası: {e}")
            tk.Label(self.frame, text=f"Grafik Hatası: {e}").pack()