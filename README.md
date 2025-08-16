
# Mess Bill Calculator (Streamlit)

A simple web app for colleges to upload mess invoices, add fixed expenses (cook, helpers, caretaker, and custom items), and compute the per-student mess bill.

## Features
- Upload multiple CSV/Excel invoices (expects an `Amount` column; optional `Item` and `Category`).
- Add fixed expenses (predefined + custom).
- Auto-sum total expenses and divide by number of students.
- Monthly period selection for reports.
- Download summary CSV and per-student ledger CSV.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud - easiest)
1. Push this folder to a new GitHub repository.
2. Go to https://share.streamlit.io/ (Streamlit Community Cloud).
3. Create a new app, point it to your repo and select `app.py` as the entry file.
4. Click **Deploy** — done!

## Alternative deploys
- **Hugging Face Spaces**: Create a new Space → choose Streamlit → upload repo files.
- **Render/Railway**: Use a Python service with `streamlit run app.py` as the start command and `pip install -r requirements.txt` as the build command.
- **Docker**: create a Dockerfile:

  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt ./
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  EXPOSE 8501
  CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
  ```

---
Built for simplicity — adjust fields as your college needs grow.
