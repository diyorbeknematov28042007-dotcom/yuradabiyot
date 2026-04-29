# ⚖️ YurAdabiyot — Yuridik Adabiyotlar Boti

Telegram bot — yuridik kitoblar elektron kutubxonasi.

---

## 🗂 Loyiha tuzilishi

```
YurAdabiyot/
├── main.py                  # Asosiy fayl (webhook)
├── config.py                # Token, admin ID, DB URL
├── requirements.txt         # Kutubxonalar
├── render.yaml              # Render deploy config
├── .env.example             # Environment namuna
├── database/
│   └── db.py                # PostgreSQL (asyncpg)
├── handlers/
│   ├── user.py              # Foydalanuvchi handlerlari
│   └── admin.py             # Admin handlerlari
├── keyboards/
│   └── keyboards.py         # Barcha tugmalar
└── middlewares/
    └── subscription.py      # Majburiy obuna
```

---

## 🚀 Deploy qilish

### 1. Supabase da baza yaratish
1. [supabase.com](https://supabase.com) → yangi project
2. Settings → Database → Connection String → **URI** ni nusxalang

### 2. GitHub ga yuklash
Barcha fayllarni GitHub repoga yuklang

### 3. Render da deploy
1. [render.com](https://render.com) → New → Web Service
2. GitHub reponi ulang
3. Environment Variables:
   - `BOT_TOKEN` = BotFather tokeningiz
   - `DATABASE_URL` = Supabase URI
   - `ADMIN_IDS` = `6206932601,8013328081`
4. Deploy bosing

### 4. UptimeRobot
[uptimerobot.com](https://uptimerobot.com) → HTTP monitor:
`https://your-app.onrender.com/health` — har 5 daqiqada

---

## ⚙️ Texnik stack
- Python 3.11+
- aiogram 3.13
- asyncpg (PostgreSQL)
- aiohttp (webhook server)
- Supabase (bepul, muddatsiz PostgreSQL)
- Render (bepul Web Service)
- UptimeRobot (uxlab qolmaslik uchun)
