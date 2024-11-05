# [GCP Document OCR](https://atalaya.digital/)

[![Image](./assets/document_ocr_hero.webp "Document OCR")](https://atalaya.digital/)

**Technos**

Dependency management: Poetry
Language: Python 3.12
Model Evaluation Platform: Comet (Not yet implemented...)

## Steps

### 1. Prepare de environment

```t
poetry new [PROJECT_NAME]
# Install dependencies
poetry install
# Enable venv
poetry shell
```

### 2. Intialize gcloud CLI in local Terminal and Enable APIs

```t
# Initialize gcloud CLI
gcloud init

# List accounts whose credentials are stored on the local system:
gcloud auth list

gcloud config set project [PROJECT_ID]

gcloud services enable documentai.googleapis.com
```

### 3. Create a document OCR processor
