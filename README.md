# Trading Simulator

Professional altın/gümüş trading simülatörü. FastAPI backend + React frontend + MySQL.

## 🚀 Docker ile Hızlı Başlangıç (Önerilen)

### Tüm servisleri başlat:
```bash
docker-compose up --build
```

### Background'da çalıştır:
```bash
docker-compose up -d --build
```

### Logları takip et:
```bash
# Tüm servisler
docker-compose logs -f

# Sadece backend
docker-compose logs -f backend

# Sadece frontend
docker-compose logs -f frontend
```

## 🛠️ Manuel Kurulum (Alternatif)

### 1. MySQL Başlat
```bash
docker-compose up -d mysql
```

### 2. Backend Kurulum
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 3. Frontend Kurulum
```bash
cd frontend
npm install
npm start
```

## Kullanım

1. **Kayıt Ol**: Yeni hesap oluştur (başlangıç bakiyesi: $10,000)
2. **Fiyatları İzle**: Canlı altın/gümüş fiyat grafikleri
3. **İşlem Yap**: Buy/Sell işlemleri
4. **Pozisyonları Takip Et**: Açık pozisyonlar ve P/L hesaplaması

## Özellikler

- ✅ LBMA feed parsing (CSV/XML)
- ✅ 2 saniyede bir fiyat güncellemeleri
- ✅ WebSocket canlı fiyat yayını
- ✅ JWT authentication
- ✅ Trade işlemleri (buy/sell)
- ✅ P/L hesaplaması
- ✅ WebSocket reconnect logic
- ✅ Responsive design

## 🔧 Docker Komutları

```bash
# Servisleri başlat
docker-compose up -d

# Servisleri durdur
docker-compose down

# Servisleri yeniden başlat
docker-compose restart

# Container'lara gir
docker-compose exec backend bash
docker-compose exec mysql mysql -u root -p
docker-compose exec frontend sh

# Logları görüntüle
docker-compose logs --tail=50 backend
```

## 📡 API Endpoints

- `POST /api/v1/auth/register` - Kayıt ol
- `POST /api/v1/auth/login` - Giriş yap
- `POST /api/v1/trading/trade` - İşlem yap
- `GET /api/v1/trading/positions` - Pozisyonları getir
- `GET /api/v1/prices/current` - Güncel fiyatlar
- `GET /health` - Sistem durumu
- `WebSocket /ws` - Canlı fiyatlar

## Teknolojiler

**Backend**: FastAPI, SQLAlchemy, MySQL, WebSockets, JWT
**Frontend**: React, Recharts, WebSocket client
