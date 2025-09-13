# 🚀 Vulna - Quick Start Guide for New Engineers

## 🎯 TL;DR - Get Started in 5 Minutes

### 1. **Clone & Setup**
```bash
git clone https://github.com/Keyvanhardani/Vulna.git
cd Vulna
python -m venv vulna-env
vulna-env\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. **Install Prerequisites**
```bash
# Install Ollama with AI model
ollama pull qwen2.5-coder:latest
```

### 3. **Run Vulna**
```bash
python -m backend.main
# ✅ Opens dashboard at http://localhost:3000
```

### 4. **Test the System**
- Click "🚀 Start Browser (Fixed)" in dashboard
- Visit http://testphp.vulnweb.com
- Watch vulnerabilities appear in real-time

---

## 🏗️ **Project Structure (Essential)**

```
Vulna/
├── backend/
│   ├── llm/worker.py          # AI vulnerability analysis
│   ├── utils/url_filter.py    # Smart filtering (CDN/static)
│   ├── web/
│   │   ├── dashboard.py       # FastAPI backend
│   │   ├── static/            # Modular CSS/JS
│   │   └── templates/         # HTML components
│   └── main.py               # Entry point
├── tests/test_filtering.py    # Test filtering system
└── data/                     # Runtime data (auto-created)
```

## 🎯 **Development Focus Areas**

### **Frontend (Modular UI)**
- **CSS Modules**: `backend/web/static/css/`
- **JS Modules**: `backend/web/static/js/`
- **Components**: `backend/web/templates/components/`

### **Backend (AI & Security)**
- **AI Logic**: `backend/llm/`
- **Filtering**: `backend/utils/`
- **APIs**: `backend/web/dashboard.py`

## 🔧 **Common Tasks**

### **Add New Component**
```bash
# 1. Create HTML
echo '<div class="new-component">...</div>' > backend/web/templates/components/new.html

# 2. Add CSS
# Edit backend/web/static/css/components.css

# 3. Add JS
# Edit appropriate backend/web/static/js/ file

# 4. Include in dashboard
# Add {% include 'components/new.html' %} to templates
```

### **Test Changes**
```bash
python tests/test_filtering.py    # Test filtering
python -m backend.main           # Run full system
curl http://localhost:3000/test  # Test components
```

### **Commit & Push**
```bash
git add .
git commit -m "🚀 Feature: Brief description"
git push origin feature/branch-name
```

## 🚨 **Quick Troubleshooting**

| Problem | Solution |
|---------|----------|
| Port 8080 in use | `netstat -ano \| findstr :8080` and kill process |
| No AI responses | Check `ollama list` and `ollama serve` |
| Static files not loading | Verify `backend/web/static/` path |
| WebSocket errors | Check browser console, restart dashboard |

## 📚 **Key Files to Understand**

1. **`backend/main.py`** - Application entry point
2. **`backend/web/dashboard.py`** - Web server & APIs
3. **`backend/llm/worker.py`** - AI analysis engine
4. **`backend/utils/url_filter.py`** - Smart filtering logic
5. **`backend/web/templates/dashboard.html`** - Complete UI reference

## 🎉 **Your First Day**

- [ ] Setup environment and run Vulna
- [ ] Explore both dashboard versions (/ and /modular)
- [ ] Read `INTELLIGENT_FILTERING.md` and `MODULAR_STRUCTURE.md`
- [ ] Test filtering with `python tests/test_filtering.py`
- [ ] Pick a small improvement and submit a PR

**Welcome to the team! Let's build amazing security tools together!** 🛡️

---

**Need more details?** → Read `ENGINEER_ONBOARDING.md` for complete documentation.
