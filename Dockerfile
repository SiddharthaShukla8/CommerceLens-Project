FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8501
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8501
CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT}"]
