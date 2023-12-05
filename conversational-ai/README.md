
# Overview
Generic implementation of PaLM 2 for Conversational AI.

Components include:
* PaLM 2 powered chat bot
* Google's Text 2 Speech
* Google's Translate API

# Pre-Requisites
1. Enable the following GCP services:
* Vertex AI
*
*

2. Create service account named `vertex-ai-consumer` and provide the following permissions:
*  Vertex AI Predictions
*
*

# Instructions

1. Configure app_json_config.json
2. Configure backend_json_config.json
3. Execute deploy_bot.sh with parameters $BOT_NAME and $PROJECT_ID
* ./deploy_bot.sh connie-bot <PROJECT_ID>
4. Execute the following command:
```gcloud run services update <BOT_NAME> --timeout=3500```

Note: Text-to-Speech voices can be modified by updating attributes language_code and language_name in the run_text_2_speech function in backend/backend.py.

## 🚀 About Me
Adrian Jones, Customer Engineer @ Google Cloud

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adrian-t-jones/) 






