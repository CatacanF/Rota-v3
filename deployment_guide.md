# Google Antigravity Deployment Guide

Complete step-by-step deployment instructions for all platforms.

---

## Table of Contents
1. [Google Cloud Platform (Recommended)](#google-cloud-deployment)
2. [Local Machine Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Post-Deployment Configuration](#post-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Google Cloud Deployment

### Prerequisites
- Google Cloud account with billing enabled
- `gcloud` CLI installed
- Project budget: $75-80/month

### Step 1: Create GCP Project

```bash
# Set project variables
export PROJECT_ID="antigravity-prod-$(date +%s)"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable billing (must be done via Console)
```

### Step 2: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  pubsub.googleapis.com
```

### Step 3: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create antigravity-sa \
  --display-name="Antigravity Service Account"

# Grant roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:antigravity-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:antigravity-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Step 4: Set Up Firestore

```bash
# Create Firestore database in Native mode
gcloud firestore databases create --region=$REGION
```

### Step 5: Store API Keys in Secret Manager

```bash
# Store Finnhub API key
echo -n "your_finnhub_key" | gcloud secrets create FINNHUB_API_KEY --data-file=-

# Store OpenAI API key
echo -n "your_openai_key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Store Perplexity API key
echo -n "your_perplexity_key" | gcloud secrets create PERPLEXITY_API_KEY --data-file=-

# Grant access to service account
for SECRET in FINNHUB_API_KEY OPENAI_API_KEY PERPLEXITY_API_KEY; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:antigravity-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Step 6: Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy antigravity-core \
  --source . \
  --region=$REGION \
  --platform=managed \
  --memory=2Gi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10 \
  --set-secrets=FINNHUB_API_KEY=FINNHUB_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,PERPLEXITY_API_KEY=PERPLEXITY_API_KEY:latest \
  --service-account=antigravity-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --allow-unauthenticated
```

### Step 7: Create Cloud Scheduler Jobs

```bash
# Get Cloud Run service URL
export SERVICE_URL=$(gcloud run services describe antigravity-core --region=$REGION --format='value(status.url)')

# Morning brief (8 AM Turkey time)
gcloud scheduler jobs create http antigravity-morning-brief \
  --location=$REGION \
  --schedule="0 8 * * 1-5" \
  --time-zone="Europe/Istanbul" \
  --uri="${SERVICE_URL}/api/v1/reports/morning" \
  --http-method=POST

# Midday update (1 PM Turkey time)
gcloud scheduler jobs create http antigravity-midday-update \
  --location=$REGION \
  --schedule="0 13 * * 1-5" \
  --time-zone="Europe/Istanbul" \
  --uri="${SERVICE_URL}/api/v1/reports/midday" \
  --http-method=POST

# Evening wrap (6 PM Turkey time)
gcloud scheduler jobs create http antigravity-evening-wrap \
  --location=$REGION \
  --schedule="0 18 * * 1-5" \
  --time-zone="Europe/Istanbul" \
  --uri="${SERVICE_URL}/api/v1/reports/evening" \
  --http-method=POST
```

### Step 8: Verify Deployment

```bash
# Check service status
gcloud run services describe antigravity-core --region=$REGION

# Test health endpoint
curl ${SERVICE_URL}/health

# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50 --format=json
```

---

## Local Deployment

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# Clone repository
git clone <your-repo>
cd sonic-granule

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FINNHUB_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export PERPLEXITY_API_KEY="your_key"

# Run morning report
python main.py morning
```

---

## Docker Deployment

### Prerequisites
- Docker Desktop installed

### Steps

```bash
# Build image
docker build -t antigravity:latest .

# Create .env file
cat > .env <<EOF
FINNHUB_API_KEY=your_key
OPENAI_API_KEY=your_key
PERPLEXITY_API_KEY=your_key
EOF

# Run container
docker run -p 8080:8080 --env-file .env antigravity:latest

# For background operation
docker run -d -p 8080:8080 --env-file .env --name antigravity antigravity:latest
```

---

## Post-Deployment

### Configure Notifications

1. **Slack Integration**
   - Create Slack incoming webhook
   - Add to Secret Manager: `SLACK_WEBHOOK_URL`

2. **Email Notifications**
   - Configure SendGrid or similar
   - Add API key to Secret Manager

3. **SMS Alerts**
   - Configure Twilio
   - Add credentials to Secret Manager

### Set Up Monitoring

```bash
# Create uptime check
gcloud monitoring uptime create antigravity-health \
  --resource-type=uptime-url \
  --host=${SERVICE_URL} \
  --path=/health \
  --check-interval=5m

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=<channel-id> \
  --display-name="Antigravity High Error Rate" \
  --condition-display-name="Error Rate > 5%" \
  --condition-threshold-value=0.05
```

---

## Troubleshooting

### Cloud Run 503 Errors
- Check max instances setting
- Review concurrency configuration
- Check memory limits

### Scheduler Jobs Failing
- Verify service URL is correct
- Check IAM permissions
- Review service account roles

### API Rate Limits
- Monitor API usage in dashboards
- Implement caching where possible
- Consider upgrading API plans

### Missing Data
- Verify API keys are set correctly
- Check Secret Manager access
- Review service account permissions

---

## Cost Optimization

- Set appropriate max instances (10 recommended)
- Use minimum instances = 0 to save costs
- Monitor API usage and optimize calls
- Set up budget alerts in GCP Console

**Estimated Monthly Cost: $75-80**
- Cloud Run: $2
- Cloud Scheduler: $0.30
- Firestore: $5
- APIs (Finnhub, OpenAI): $70

---

## Next Steps

1. Review `ultimate_investor_guide.md` for usage instructions
2. Check `quick_reference.md` for common tasks
3. Monitor system performance for first week
4. Adjust settings based on usage patterns

---

**Deployment Complete! 🚀**
