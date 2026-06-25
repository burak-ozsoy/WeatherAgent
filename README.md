---
title: WeatherAgent
emoji: 🌤️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
---

# 🌤️ Weather-Aware Activity Recommendation Agent
## Adım Adım Kurulum ve Çalıştırma Rehberi

# 🌤️ Weather-Aware Activity Recommendation Agent
## Adım Adım Kurulum ve Çalıştırma Rehberi

---

## 📁 Proje Yapısı

```
weather_agent/
├── app.py                   ← Streamlit web arayüzü
├── weather_agent.py         ← Backend / Agent mantığı (terminal için)
├── weather_service.py       ← Hava verisi çekme + normalize + karar motoru
├── activities.py            ← Aktivite kataloğu (her birinin gerçek sıcaklık/rüzgar/koşul eşikleri)
├── suitability.py           ← Bir aktivitenin o anki havaya uyup uymadığını kontrol eden ortak kural
├── recommendation_engine.py ← Hava + kategoriye göre gerçek öneri üretimi
├── evaluator.py             ← Önerilerin gerçekten uygun olup olmadığını bağımsız doğrulayan katman
├── requirements.txt         ← Gerekli kütüphaneler
├── Dockerfile               ← Hugging Face Docker deploy ayarı
├── .gitignore               ← GitHub'a gitmemesi gereken dosyalar
└── README.md                ← Bu dosya
```

Mantık artık tek bir dosyada değil, görevine göre ayrılmış modüllerde: `app.py` ve `weather_agent.py` aynı `weather_service.py` / `recommendation_engine.py` / `evaluator.py` üzerinden çalışıyor, yani hava verisi çekme veya karar mantığı iki yerde ayrı ayrı tutulup birbirinden sapmıyor.

---

## 🔑 ADIM 1: OpenWeatherMap API Key Alma (ÜCRETSİZ)

1. https://openweathermap.org/api adresine git
2. "Sign Up" ile ücretsiz hesap oluştur
3. E-posta ile doğrula
4. Sağ üstten "My API Keys" bölümüne git
5. API key'ini kopyala (örn: `a1b2c3d4e5f6g7h8i9j0`)
6. ⚠️ API key aktif olması **10-15 dakika** sürebilir!

---

## 💻 ADIM 2: Python Ortamı Kurma

### Python yüklü değilse:
https://python.org/downloads → Python 3.10+ indir ve kur

### Sanal ortam oluştur (önerilir):
```bash
# Proje klasörüne git
cd weather_agent

# Sanal ortam oluştur
python -m venv venv

# Aktif et (Windows)
venv\Scripts\activate

# Aktif et (Mac/Linux)
source venv/bin/activate
```

---

## 📦 ADIM 3: Kütüphaneleri Yükle

```bash
pip install -r requirements.txt
```

Veya tek tek:
```bash
pip install --upgrade streamlit requests
```

> **Not:** `pip install streamlit` zaten kuruluysa paketi **güncellemez**, sadece "already satisfied" der. Daha önce eski bir sürüm kurduysan mutlaka `--upgrade` ile çalıştır, yoksa bazı arayüz öğeleri terminalde hata fırlatabilir.

---

## 🔐 ADIM 4: API Key'i Girme

Koddaki hiçbir dosyada sabit (hardcoded) API key **yok** — bu bilinçli bir tercih, key'in repoya/Hugging Face'e yanlışlıkla sızmasını engelliyor.

### Terminal (`weather_agent.py`) için:
```bash
# Ortam değişkeni olarak ayarla (önerilen)
export OPENWEATHER_API_KEY="senin_api_keyin"      # Mac/Linux
set OPENWEATHER_API_KEY=senin_api_keyin           # Windows (cmd)

python weather_agent.py
```
Ortam değişkeni ayarlanmazsa program terminalde key'i elle girmeni ister.

### Streamlit (`app.py`) için:
Key dosyaya yazılmaz. Uygulama açıldığında sol sidebar'daki **"OpenWeatherMap API Key"** alanına key'ini yapıştırırsın; sadece o oturum için hafızada tutulur, hiçbir yere kaydedilmez. Boş bırakıp "Analyze Weather" dersen uygulama key isteyen net bir uyarı gösterir.

---

## ▶️ ADIM 5: Uygulamayı Çalıştır

### Seçenek A - Terminal (Basit):
```bash
python weather_agent.py
```
API key'i sorar (env var yoksa), şehir adı sorar, analiz yapar, sonuçları terminale yazdırır.

### Seçenek B - Streamlit Web Arayüzü:
```bash
streamlit run app.py
```
Tarayıcı otomatik açılır: http://localhost:8501 — sidebar'a API key'ini gir, şehir ve kategori seç, "Analyze Weather"e tıkla.

---

## 🧪 ADIM 6: Test Et

### Test Şehirleri:
- `Istanbul` → Türkiye
- `London` → Yağmur testi için ideal!
- `Dubai` → Sıcak hava testi
- `Oslo` → Soğuk hava testi
- `Moscow` → Kar testi (kış aylarında)

### Beklenen Davranış:
Her aktivitenin (`activities.py`) kendi sıcaklık aralığı, maksimum rüzgar değeri ve kaçındığı hava koşulları var; öneri motoru sadece o an gerçekten uygun olanları gösteriyor — sabit bir "skor aralığına göre rastgele seç" mantığı değil.

| Durum | Beklenen Davranış |
|-------|---------------|
| Yağmurlu / Fırtınalı | Koşu, bisiklet, piknik gibi aktiviteler **hiç önerilmez**; sonuç İç Mekan & Kültür'e kayar (etiket bunu açıkça belirtir) |
| 15-25°C, açık, sakin rüzgar | Koşu, bisiklet, yürüyüş, piknik, fotoğrafçılık gibi seçenekler tam puan eşleşir |
| Rüzgar > aktivitenin eşiği (örn. bisiklette 7 m/s) | O aktivite havuzdan otomatik çıkar, diğerleri kalır |
| Sıcaklık < 5°C | Outdoor seçenekler büyük ölçüde elenir, İç Mekan/Kültür ile dolduruluyor |
| Sıcaklık > 24-30°C aralığı | Yüzme / sahil yürüyüşü gibi sıcağa özel aktiviteler devreye girer |

"Agent Trace" paneli kararın *neden* öyle verildiğini (yağmur, yüksek rüzgar, ideal aralık vb.) ayrı ayrı satırlarla gösteriyor; "Match Score" ise önerilenlerin gerçekten o anki havaya uyup uymadığını bağımsızca tekrar doğruluyor.

---

## ☁️ ADIM 7: Hugging Face Spaces'a Deploy Et

### 7.1 - Hugging Face hesabı aç:
https://huggingface.co/join

### 7.2 - Yeni Space oluştur:
1. https://huggingface.co/new-space adresine git
2. Space name: `weather-activity-agent`
3. **SDK: Docker** seç
4. Visibility: Public
5. "Create Space" tıkla

> Not: Streamlit uygulaması Hugging Face üzerinde Docker ile çalıştırılır. Bu yüzden projede `Dockerfile` bulunmalıdır.

### 7.3 - README.md Space ayarları:

`README.md` dosyasının en üstünde şu metadata bloğu bulunmalıdır:

```md
---
title: Weather Activity Agent
emoji: 🌤️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
---
```

### 7.4 - Dockerfile:

Proje klasöründeki `Dockerfile` dosyası Streamlit uygulamasını 8501 portunda başlatır:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 7.5 - Dosyaları yükle:

Space'e gir → "Files" sekmesi → Upload files.

Gerekli dosyalar:

- `app.py`
- `weather_service.py`
- `activities.py`
- `suitability.py`
- `recommendation_engine.py`
- `evaluator.py`
- `requirements.txt`
- `Dockerfile`
- `README.md`

`weather_agent.py` terminal/CLI kullanımı için opsiyoneldir. Projeyi tam göstermek istiyorsan yüklenebilir.

### 7.6 - API Key konusunda:

Kodda API key hardcoded olmamalıdır. Kullanıcılar uygulama açıldığında sidebar’daki **"OpenWeatherMap API Key"** alanına kendi key’lerini girerek kullanır.

Terminal tarafında kullanmak için:

```bash
export OPENWEATHER_API_KEY="senin_api_keyin"      # Mac/Linux
set OPENWEATHER_API_KEY=senin_api_keyin           # Windows cmd
python weather_agent.py
```

### 7.7 - Deploy tamamlandı! 🎉

`https://huggingface.co/spaces/KULLANICI_ADIN/weather-activity-agent`

---

## 📊 Sistem Mimarisi

```
Kullanıcı Girişi (Şehir + Kategori + API Key)
        ↓
  Weather API Layer            weather_service.fetch_weather
  (OpenWeatherMap)
        ↓
  Data Processing Layer        weather_service.process_weather_data
  (Normalize & Extract)
        ↓
  Decision Engine (Agent)      weather_service.decision_engine
  (Rule-based, izlenebilir trace üretir)
        ↓
  Suitability Filter           suitability.activity_fits_weather
  (her aktivite kendi sıcaklık/rüzgar/koşul eşiğine göre elenir)
        ↓
  Recommendation Engine        recommendation_engine.generate_smart_recommendations
  (uygun havuzdan seçim + gerekirse İç Mekan/Kültür ile tamamlama)
        ↓
  Evaluator (bağımsız QA)      evaluator.evaluate_recommendations
  (önerilerin gerçekten uyup uymadığını ayrıca doğrular)
        ↓
  Kullanıcıya Öneriler
```

---

## 🤖 Neden Bu Bir "Autonomous Agent"?

| Kriter | Nasıl Sağlanıyor? |
|--------|-------------------|
| Bağımsız veri toplama | OpenWeatherMap API |
| Çoklu koşul değerlendirme | Decision engine + her aktivite için ayrı uygunluk kuralları |
| İnsan müdahalesi olmadan karar | Otomatik rule-based logic, izlenebilir "trace" çıktısıyla |
| Eylem üretme | Hava koşuluna gerçekten uyan aktivite önerileri |
| Kendi kendini doğrulama | Evaluator katmanı, motorun çıktısını bağımsızca tekrar kontrol ediyor |
| Araç kullanımı | External API + Python |

---

## 🐛 Sık Karşılaşılan Hatalar

### "401 Unauthorized"
→ API key yanlış veya henüz aktif değil (10-15 dk bekle)

### "404 Not Found"
→ Şehir adı yanlış yazılmış (İngilizce yaz: "Istanbul" not "İstanbul")

### "Connection Error"
→ İnternet bağlantısını kontrol et

### Terminalde `label_visibility` / `use_container_width` / beklenmeyen argüman hatası
→ Kurulu Streamlit sürümü çok eski. `pip install streamlit` zaten kuruluysa güncellemez; `pip install --upgrade streamlit` ile zorla güncelle. (Kod, geniş bir sürüm aralığıyla çalışacak şekilde yazıldı, ama yine de güncel tutmak en güvenlisi.)

### Streamlit açılmıyor / sayfa bomboş kalıyor
→ `pip install --upgrade streamlit` komutunu tekrar dene
→ Port 8501 kullanımda olabilir: `streamlit run app.py --server.port 8502`
→ Terminaldeki kırmızı hata metnine bak; genelde tam olarak hangi satırda sorun olduğunu söyler

---

## ✅ Proje Teslim Kontrol Listesi

- [ ] `weather_agent.py` terminalde çalışıyor (env var veya elle girilen key ile)
- [ ] `app.py` Streamlit arayüzü çalışıyor
- [ ] En az 5 farklı şehir test edildi (açık, yağmurlu, soğuk, sıcak, karlı)
- [ ] Karar motoru ve uygunluk filtresi tüm senaryoları kapsıyor (kötü havada uygunsuz aktivite önerilmiyor)
- [ ] API key hiçbir dosyada sabit yazılı değil
- [ ] Hugging Face'e deploy edildi
- [ ] README.md hazır

---

*Weather-Aware Activity Recommendation Agent © 2026*