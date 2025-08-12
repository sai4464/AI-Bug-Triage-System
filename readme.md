# 🐞 AI Bug Triage System

A smart, responsive web application that classifies bug reports by **category** (UI, Backend, Security, etc.) and **urgency level** (Critical, High, Medium, Low) using powerful AI models from Hugging Face.

---

## 🚀 Features

- 🎯 **Semantic Classification** using pretrained embeddings (`all-MiniLM-L6-v2`)
- 🤖 **Hugging Face Transformers** for intelligent text understanding
- 🧠 **Rule-enhanced AI logic** to improve accuracy (e.g., security = always urgent)
- 🌍 **Web API with Flask** (supports batch & single bug triage)
- 📊 **Dashboard-style results** with pastel-themed UI
- 🧾 Confidence scores and category-wise summary
- 🧪 Health check + AI status endpoints

---

## 🧠 Tech Stack

| Layer            | Tools & Libraries                             |
|------------------|-----------------------------------------------|
| Frontend         | HTML, Bootstrap 5, FontAwesome, Vanilla JS    |
| Backend (API)    | Flask, Flask-CORS                             |
| AI Models        | Hugging Face Transformers, SentenceTransformers |
| ML Tools         | PyTorch, scikit-learn, cosine similarity      |

---

## 📂 Project Structure

bug-triage-ai/
├── app.py # Flask app with API endpoints
├── main.py # Entry point to start the app
├── ai_triage_service.py # Core AI logic using embeddings & similarity
├── openai_service.py # Fallback (if AI model not installed)
├── templates/
│ └── index.html # Beautiful pastel UI frontend
├── static/ # (Optional) CSS/JS/image assets
└── README.md # You are here

---

## 🧪 How to Run Locally

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/bug-triage-ai.git
cd bug-triage-ai
2. Install Dependencies
pip install -r requirements.txt
Or manually install:
pip install flask flask-cors transformers sentence-transformers torch scikit-learn
3. Run the App
python main.py
Then open http://localhost:8080 in your browser.
📤 API Endpoints
POST /triage
Analyze a single bug report.
Request:

{
  "title": "Login button not working",
  "description": "Clicking login does nothing. Happening on mobile and desktop."
}
Response:
{
  "category": "UI",
  "urgency": "High",
  "category_confidence": 0.92,
  "urgency_confidence": 0.87
}
POST /batch-triage
Analyze 1–20 bug reports in a single call.
{
  "bugs": [
    {"title": "...", "description": "..."},
    ...
  ]
}
GET /ai-status
Returns model info and whether AI mode is active.
🎨 UI Preview
📌 TODO / Ideas
 Export results to CSV
 Real-time feedback as you type
 REST + GraphQL support
 CI/CD Deployment (Render, GCP, Railway)
📄 License
MIT License © 2025 [sai4464]
🤝 Contributing
Pull requests and ideas welcome!
Feel free to fork and build your own flavor of bug triaging.
💬 Contact
Need help or want to collaborate?
📫 Email: meetcharan2025@gmail.com
