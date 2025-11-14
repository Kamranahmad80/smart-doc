# Deployment Guide

## Local Development

### Quick Start

1. **Clone Repository**

   ```bash
   git clone https://github.com/yourusername/smart-doc.git
   cd smart-doc
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   streamlit run app.py
   ```

Visit `http://localhost:8501` in your browser.

---

## Production Deployment

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub**

   ```bash
   git push origin main
   ```

2. **Go to https://streamlit.io/cloud**
   - Connect your GitHub repository
   - Select this repository
   - Deploy with one click

### Option 2: Docker (Self-Hosted)

1. **Create Dockerfile**

   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["streamlit", "run", "app.py"]
   ```

2. **Build & Run**
   ```bash
   docker build -t smart-doc .
   docker run -p 8501:8501 smart-doc
   ```

### Option 3: Heroku

1. **Create Procfile**

   ```
   web: streamlit run --server.port $PORT app.py
   ```

2. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 4: AWS/Google Cloud/Azure

- Use containerized Docker image
- Deploy to services like:
  - AWS ECS/Fargate
  - Google Cloud Run
  - Azure Container Instances

---

## Environment Variables

Create `.env` file for sensitive configurations:

```env
# Optional configuration
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=200
```

---

## Performance Optimization

### For Large-Scale Deployments

1. **GPU Acceleration**

   ```bash
   pip install faiss-gpu
   # Requires CUDA toolkit
   ```

2. **Model Caching**

   - Pre-download model: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"`
   - Models cached in `~/.cache/huggingface/hub/`

3. **Memory Management**
   - Process documents in batches
   - Increase chunk size to reduce total chunks
   - Use smaller model if needed

---

## Security Considerations

✅ **Already Implemented:**

- CORS disabled by default
- CSRF protection enabled
- No external data transmission
- File size limit (200MB)

**Additional Hardening:**

- Use HTTPS/TLS in production
- Add authentication if needed
- Regular dependency updates
- Input validation (already done)

---

## Monitoring & Maintenance

### Logs

```bash
# View logs
streamlit logs

# Or redirect to file
streamlit run app.py > app.log 2>&1
```

### Updates

```bash
# Check for updates
pip list --outdated

# Update dependencies
pip install -r requirements.txt --upgrade
```

---

## Troubleshooting

### Port Already in Use

```bash
streamlit run app.py --server.port 8502
```

### Memory Issues

```bash
# Run with limited cache
streamlit run app.py --logger.level=warning --client.showErrorDetails=false
```

### Model Download Timeout

```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
```

---

## Version Control

### Recommended `.gitignore` (included)

- `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.streamlit/` - Local config
- `.env` - Environment variables

---

## Support

For issues or questions:

1. Check README.md
2. Review GitHub Issues
3. Check Streamlit documentation
4. Test in isolation: `python -m pytest`
