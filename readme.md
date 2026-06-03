python -m uvicorn main:app --reload 

# Backend
pip install -r requirements.txt
uvicorn main:app --reload
# Frontend (separate terminal)
cd ai-dashboard
npm run dev



http://localhost:5173/