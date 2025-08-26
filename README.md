# Özel Matematik Dersi Platformu

5-8. sınıf öğrencileri için özel olarak tasarlanmış interaktif matematik öğrenme platformu. Öğretmenler ve öğrenciler için kapsamlı özellikler sunar.

## 🚀 Özellikler

### Öğretmenler İçin:
- **Sınıf Yönetimi**: Öğrencileri sınıflara ekleme ve yönetme
- **Ödev Oluşturma**: PDF ve ekran görüntüleri ile ödev yükleme
- **Otomatik Puanlama**: Öğrenci cevaplarını otomatik değerlendirme
- **Detaylı Analitik**: Öğrenci performansını takip etme
- **Geri Bildirim**: Kişiselleştirilmiş geri bildirim verme

### Öğrenciler İçin:
- **İnteraktif Ödevler**: Çeşitli soru tipleri (çoktan seçmeli, sayısal, kısa cevap)
- **Eğitici Oyunlar**: Çarpım tablosu, matematik bulmacaları, kesir oyunları
- **İlerleme Takibi**: Kişisel performans analizi
- **Anında Geri Bildirim**: Doğru/yanlış cevap açıklamaları

### Teknik Özellikler:
- **Modern Web Teknolojileri**: FastAPI, Tailwind CSS, Alpine.js
- **Güvenli Kimlik Doğrulama**: Firebase Authentication
- **Veri Depolama**: Firebase Firestore
- **Dosya Yönetimi**: Firebase Storage
- **Responsive Tasarım**: Tüm cihazlarda mükemmel çalışma

## 🛠️ Kurulum

### Gereksinimler:
- Python 3.8+
- Node.js (opsiyonel, geliştirme için)
- Firebase hesabı

### Adımlar:

1. **Projeyi klonlayın:**
```bash
git clone <repository-url>
cd ozel-ders-programi
```

2. **Python bağımlılıklarını yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Firebase konfigürasyonu:**
   - Firebase Console'da yeni bir proje oluşturun
   - Authentication'ı etkinleştirin (Google Sign-in)
   - Firestore Database'i oluşturun
   - Storage'ı etkinleştirin
   - `firebase-config-example.js` dosyasını kopyalayıp `firebase-config.js` olarak adlandırın
   - Kendi Firebase bilgilerinizle güncelleyin

4. **Ortam değişkenlerini ayarlayın:**
```bash
# .env dosyası oluşturun
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_B64=your-service-account-base64
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

5. **Uygulamayı çalıştırın:**
```bash
python -m uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

6. **Tarayıcıda açın:**
```
http://localhost:8000
```

## 📁 Proje Yapısı

```
├── api/
│   └── index.py              # Vercel deployment için
├── app/
│   ├── deps/
│   │   └── firebase.py       # Firebase bağımlılıkları
│   ├── models/
│   │   └── schemas.py        # Pydantic modelleri
│   ├── repos/
│   │   ├── assignments.py    # Ödev repository
│   │   ├── classes.py        # Sınıf repository
│   │   └── users.py          # Kullanıcı repository
│   ├── routers/
│   │   ├── analytics.py      # Analitik API'leri
│   │   ├── auth.py           # Kimlik doğrulama
│   │   ├── games.py          # Oyun API'leri
│   │   ├── student.py        # Öğrenci API'leri
│   │   └── teacher.py        # Öğretmen API'leri
│   ├── services/
│   │   └── scoring.py        # Puanlama servisi
│   ├── static/               # Statik dosyalar
│   ├── templates/            # HTML şablonları
│   └── main.py               # Ana uygulama
├── requirements.txt          # Python bağımlılıkları
└── vercel.json              # Vercel konfigürasyonu
```

## 🎮 Oyunlar

### Çarpım Tablosu Sprint
- 3 zorluk seviyesi (Kolay, Orta, Zor)
- Hızlı çarpım tablosu çözme
- Süre takibi ve puanlama

### Matematik Bulmaca
- Sayıları kullanarak hedef sayıya ulaşma
- Mantık ve problem çözme becerileri

### Kesir Eğlencesi
- Kesirleri karşılaştırma ve sıralama
- Görsel öğrenme desteği

## 🔧 API Endpoints

### Kimlik Doğrulama
- `POST /api/auth/bootstrap` - Kullanıcı oturumu başlatma

### Öğretmen API'leri
- `GET /api/teacher/classes` - Sınıfları listeleme
- `POST /api/teacher/classes` - Yeni sınıf oluşturma
- `POST /api/teacher/users` - Öğrenci ekleme
- `POST /api/teacher/assignments` - Ödev oluşturma

### Öğrenci API'leri
- `GET /api/student/assignments` - Ödevleri listeleme
- `POST /api/student/assignments/{id}/submit` - Ödev teslim etme

### Oyun API'leri
- `GET /api/games/available` - Mevcut oyunları listeleme
- `GET /api/games/{game}/questions` - Oyun sorularını alma
- `POST /api/games/submit-result` - Oyun sonucunu kaydetme

### Analitik API'leri
- `GET /api/analytics/teacher/overview` - Öğretmen genel bakış
- `GET /api/analytics/student/my-progress` - Öğrenci ilerlemesi

## 🚀 Deployment

### Vercel ile Deployment:
1. Vercel hesabı oluşturun
2. GitHub repository'nizi bağlayın
3. Ortam değişkenlerini ayarlayın
4. Deploy edin

### Firebase Service Account:
1. Firebase Console > Project Settings > Service Accounts
2. "Generate new private key" butonuna tıklayın
3. JSON dosyasını indirin
4. Base64 encode edin ve `FIREBASE_SERVICE_ACCOUNT_B64` olarak ayarlayın

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

Sorularınız için issue açabilir veya email gönderebilirsiniz.

## 🙏 Teşekkürler

- Firebase ekibine harika altyapı için
- FastAPI ekibine modern web framework için
- Tailwind CSS ekibine güzel tasarım sistemi için
