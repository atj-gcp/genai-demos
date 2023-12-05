BOT_NAME=$1
PROJECT_NAME=$2
echo $(gcloud auth print-access-token) > backend/token.txt

docker build . -t us-east1-docker.pkg.dev/$PROJECT_NAME/app/$BOT_NAME:latest

docker push us-east1-docker.pkg.dev/$PROJECT_NAME/app/$BOT_NAME:latest

gcloud run deploy $BOT_NAME \
    --image=us-east1-docker.pkg.dev/$PROJECT_NAME/app/$BOT_NAME:latest \
    --region=us-east1 \
    --service-account=vertex-ai-consumer@$PROJECT_NAME.iam.gserviceaccount.com \
    --allow-unauthenticated \
    --set-env-vars="STREAMLIT_SERVER_PORT=8080"
    