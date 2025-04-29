# 🧬 Ancient DNA API with Gemini AI - FastAPI Project

This project provides a FastAPI-based backend that allows you to:

- 📁 Upload ancient DNA sample data via CSV
- 🧬 Generate DNA sequences based on sample details
- 🔬 Compare two DNA sequences
- 🤖 Ask free-form natural language questions using **Gemini AI**

It includes Swagger UI for easy API testing and interactive documentation.

---

## 🚀 Features

- ✅ Upload CSV file with DNA sample data
- ✅ Generate repeatable DNA sequences from sample ID
- ✅ Compare two DNA sequences for similarity
- ✅ Ask natural language questions using Gemini AI
- ✅ Swagger UI for testing all endpoints

---

## 📦 Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/) – High performance web framework
- [Gemini AI](https://ai.google.dev/) – Generative AI by Google
- [Pandas](https://pandas.pydata.org/) – Data processing
- [Uvicorn](https://www.uvicorn.org/) – ASGI web server
- [dotenv](https://pypi.org/project/python-dotenv/) – For managing secrets

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash

git clone <your-repo-url>
cd your-project

```

### 2️⃣ Install Dependencies

```bash

pip install -r requirements.txt

```

### 3️⃣ Add Your Gemini API Key

Create a .env file in the root:

```bash

GOOGLE_API_KEY=your_gemini_api_key_here

```

### 4️⃣ Run the App

```bash

uvicorn main:app --reload

```

## 🌐 Swagger UI
 - Once the app is running, open this in your browser:
 - 🔗 http://localhost:8000/docs

 - You can test all endpoints directly in Swagger.


### API Endpoints

## 📁 /upload-csv/ – Upload DNA Sample CSV
 - Method: POST
 - Consumes: multipart/form-data
 - Form Field: file
 - Function: Uploads sample data from a CSV file

## 🧬/generate-sequence/ – Generate DNA Sequence
 - Method: GET
 - Query Param: sample_id
 - Function: Generates a pseudo-DNA sequence using the stored seed
 - 📌 Example:
 - http://localhost:8000/generate-sequence/?sample_id=101

## 🔬 /compare-sequences/ – Compare Two DNA Sequences
 - Method: GET
 - Query Params:
 - id1: First sample ID
 - id2: Second sample ID
 - Function: Compares two generated DNA sequences and returns the similarity %
 - 📌 Example:
 - http://localhost:8000/compare-sequences/?id1=101&id2=102

## 🤖 /ask-me-anything/ – Ask Gemini AI
 - Method: POST
 - Consumes: application/json
 - Body:

```bash
{
  "question": "What are the oldest DNA samples in Asia?"
}
```
 - Function: Sends your question to the Gemini AI model and returns the generated answer.

### 📌 How It Works
 - CSV Upload – Loads and stores DNA sample data in memory.
 - Generate Sequence – Uses the seed to create consistent DNA-like sequences.
 - Compare Sequence – Compares base pairs between two sequences and gives a similarity percentage.
 - Gemini AI – Uses Google Generative AI API to answer natural language questions based on DNA context or history.