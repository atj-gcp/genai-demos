docker build . -t us-east1-docker.pkg.dev/heroic-trilogy-340212/app/wealth-bot:latest

docker push us-east1-docker.pkg.dev/heroic-trilogy-340212/app/wealth-bot:latest

gcloud run deploy wealth-bot \
    --image=us-east1-docker.pkg.dev/heroic-trilogy-340212/app/wealth-bot:latest \
    --region=us-east1 \
    --service-account=vertex-ai-consumer@heroic-trilogy-340212.iam.gserviceaccount.com \
    --allow-unauthenticated \
    --set-env-vars="STREAMLIT_SERVER_PORT=8080"