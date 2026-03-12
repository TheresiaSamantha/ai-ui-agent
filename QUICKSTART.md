# Quick Start Guide - AI UI Agent

## 🚀 Menjalankan Aplikasi

### 1. Setup Backend (Terminal 1)

```bash
# Masuk ke folder backend
cd ai-ui-agent/backend

# Aktifkan virtual environment
source venv/Scripts/activate  # Windows Git Bash
# source venv/bin/activate     # Linux/Mac

# Install dependencies (jika belum)
pip install -r requirements.txt

# PENTING: Setup file .env dengan API key
cp .env.example .env
# Edit .env dan tambahkan GEMINI_API_KEY Anda
# nano .env  atau  notepad .env
# Isi dengan: GEMINI_API_KEY=your_actual_api_key_here

# Jalankan server
python main.py
```

> **⚠️ WAJIB:** Sebelum menjalankan server, pastikan file `.env` sudah dibuat dan berisi `GEMINI_API_KEY` yang valid. Dapatkan API key gratis di [Google AI Studio](https://ai.google.dev/).

✅ Server akan berjalan di: http://localhost:8000  
📚 API Docs: http://localhost:8000/docs

### 2. Setup Frontend (Terminal 2)

```bash
# Masuk ke folder frontend
cd ai-ui-agent/frontend

# Install dependencies (jika belum)
npm install

# Jalankan dev server
npm run dev
```

✅ Frontend akan berjalan di: http://localhost:5173

### 3. Test Aplikasi

1. Buka browser: http://localhost:5173
2. Pastikan status indicator menunjukkan **"Connected"** (hijau)
3. Coba prompt: **"How do I login?"**
4. Pilih file: **login_context.json** (atau biarkan AI memilih)
5. Klik **"Generate Task Instructions"**
6. Lihat 7 langkah instruksi muncul secara real-time!

## 🧪 Test Backend Saja

```bash
# Test list files
curl http://localhost:8000/api/files

# Test generate task
curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{"prompt":"How to login?","file":"login_context.json"}'

# Test agent langsung
cd backend
python agent.py
```

## 📝 Contoh Prompt Yang Bisa Dicoba

1. **"How do I login to the application?"**
2. **"Where is the login button located?"**
3. **"What are the steps to submit the login form?"**
4. **"Find the password input field"**
5. **"How to access the application?"**

## ⚠️ Troubleshooting

### Backend Error: "No module named 'fastapi'"

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Error: "Cannot connect to backend"

- Pastikan backend sudah berjalan di port 8000
- Check di http://localhost:8000 (harus menampilkan JSON response)

### Backend Error: "API Key not found"

```bash
# Edit file .env
cd backend
nano .env  # atau notepad .env

# Tambahkan:
GEMINI_API_KEY=your_api_key_here
```

## 🎯 Struktur Project

```
ai-ui-agent/
├── backend/              ← FastAPI server
│   ├── main.py           ← API endpoints
│   ├── agent.py          ← AI logic
│   ├── mcp_server.py     ← File tools
│   └── Data_Analis/      ← UI context files
└── frontend/             ← React app
    └── src/
        └── App.jsx       ← Main UI
```

## 📚 Dokumentasi Lengkap

Lihat **README.md** untuk:

- Penjelasan arsitektur lengkap
- Strategi prompt engineering
- MCP server design
- Metrics & monitoring
- Deployment guide

## 🙋 Pertanyaan?

Baca README.md atau check API docs di http://localhost:8000/docs
