from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
from dotenv import load_dotenv
import csv
from typing import Dict, List, Optional
import requests
import logging
import json
from io import StringIO

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Define the SampleData model (import from models.py in your actual code)
class SampleData(BaseModel):
    id: str
    region: str
    age: int
    seed: str

# Load API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    logger.warning("GEMINI_API_KEY not found in environment variables. Ask Me Anything endpoint will not work.")
    
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory storage for uploaded data
ancient_data: Dict[str, Dict] = {}

@app.get("/")
def root():
    return {"message": "Welcome to the Ancient DNA API"}

# Helper function to process sample data and add to storage
def process_sample_data(sample_data: SampleData):
    ancient_data[sample_data.id] = {
        "region": sample_data.region,
        "age": sample_data.age,
        "seed": sample_data.seed
    }
    return sample_data

# Dummy DNA generation function (simulate expensive call)
def generate_dna_sequence(sample_id, region, age, seed):
    import random
    random.seed(hash(f"{sample_id}-{region}-{age}-{seed}"))
    return ''.join(random.choices("ATCG", k=100))

# Upload CSV endpoint - Form upload method
@app.post("/upload-csv/", tags=["data"])
async def upload_csv(file: Optional[UploadFile] = File(None)):
    logger.info("Received upload-csv request")
    
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided")
    
    logger.info(f"Received file: {file.filename}")
    
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

    try:
        contents = await file.read()
        contents_str = contents.decode('utf-8')
        
        # Parse CSV with pandas
        df = pd.read_csv(StringIO(contents_str))
        logger.info(f"CSV loaded with {len(df)} rows")
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Create SampleData object and process it
                sample = SampleData(
                    id=str(row["id"]),
                    region=row["region"],
                    age=int(row["age"]) if pd.notna(row["age"]) else 0,
                    seed=row["seed"]
                )
                process_sample_data(sample)
            except Exception as row_error:
                logger.error(f"Error processing row {index}: {str(row_error)}")
                
        return {"message": f"{len(df)} records successfully uploaded."}
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

# Add a direct JSON upload method
@app.post("/upload-json/", tags=["data"])
async def upload_json(samples: List[SampleData]):
    logger.info(f"Received JSON upload with {len(samples)} samples")
    
    for sample in samples:
        process_sample_data(sample)
    
    return {"message": f"{len(samples)} records successfully uploaded."}

# Add a single sample method
@app.post("/add-sample/", tags=["data"])
async def add_sample(sample: SampleData):
    logger.info(f"Adding single sample with ID: {sample.id}")
    process_sample_data(sample)
    return {"message": "Sample successfully added."}

# DNA generation endpoint
@app.get("/generate-sequence/", tags=["dna"])
def get_sequence(sample_id: str = Query(...)):
    if sample_id not in ancient_data:
        raise HTTPException(status_code=404, detail="Sample ID not found.")
    
    data = ancient_data[sample_id]
    sequence = generate_dna_sequence(sample_id, data["region"], data["age"], data["seed"])
    return {"sample_id": sample_id, "sequence": sequence}

# DNA comparison endpoint
@app.get("/compare-sequences/", tags=["dna"])
def compare_sequences(id1: str = Query(...), id2: str = Query(...)):
    if id1 not in ancient_data or id2 not in ancient_data:
        raise HTTPException(status_code=404, detail="One or both sample IDs not found.")
    
    seq1 = generate_dna_sequence(id1, **ancient_data[id1])
    seq2 = generate_dna_sequence(id2, **ancient_data[id2])

    matches = sum(c1 == c2 for c1, c2 in zip(seq1, seq2))
    similarity = round((matches / len(seq1)) * 100, 2)
    
    return {
        "id1": id1,
        "id2": id2,
        "similarity_percentage": f"{similarity}%"
    }

# List all samples endpoint
@app.get("/list-samples/", tags=["data"])
def list_samples():
    samples = []
    for sample_id, data in ancient_data.items():
        samples.append({
            "id": sample_id,
            "region": data["region"],
            "age": data["age"],
            "seed": data["seed"]
        })
    return {"samples": samples}

# Ask Me Anything Endpoint using Google Gemini API
class AskRequest(BaseModel):
    question: str

@app.post("/ask-me-anything/")
async def ask_me_anything(data: AskRequest):
    # Log the incoming question
    logger.info(f"Received question: {data.question}")
    
    # Check if we have any data loaded
    if not ancient_data:
        return {"answer": "No data has been uploaded yet. Please upload a CSV file first."}
    
    # Simple data analysis based on keywords in the question
    question_lower = data.question.lower()
    
    # Check if the question is about average age
    if "average" in question_lower and "age" in question_lower:
        try:
            # Calculate average age from our data
            ages = [entry["age"] for entry in ancient_data.values() if "age" in entry]
            if not ages:
                return {"answer": "I couldn't find age data in the uploaded information."}
            
            average_age = sum(ages) / len(ages)
            return {"answer": f"The average age in the uploaded data is {average_age:.2f} years."}
        except Exception as e:
            logger.error(f"Error calculating average age: {str(e)}")
            return {"answer": f"I encountered an error while calculating the average age: {str(e)}"}
    
    # Check if the question is about regions
    elif "region" in question_lower or "regions" in question_lower:
        try:
            # Get list of regions
            regions = [entry["region"] for entry in ancient_data.values() if "region" in entry]
            regions_count = {}
            for region in regions:
                if region in regions_count:
                    regions_count[region] += 1
                else:
                    regions_count[region] = 1
                    
            region_info = ", ".join([f"{region}: {count}" for region, count in regions_count.items()])
            return {"answer": f"The data includes the following regions: {region_info}"}
        except Exception as e:
            logger.error(f"Error analyzing regions: {str(e)}")
            return {"answer": f"I encountered an error while analyzing regions: {str(e)}"}
    
    # Check if the question is about count/number of records
    elif any(word in question_lower for word in ["many", "count", "number", "records", "samples"]):
        return {"answer": f"There are {len(ancient_data)} records in the uploaded data."}
    
    # If we can't determine what the question is about, use the Gemini API if available
    elif GEMINI_API_KEY:
        try:
            # Prepare context from our data
            data_context = "Based on the following data:\n"
            for sample_id, details in list(ancient_data.items())[:10]:  # Limit to first 10 records to avoid token limits
                data_context += f"ID: {sample_id}, Region: {details.get('region', 'Unknown')}, Age: {details.get('age', 'Unknown')}, Seed: {details.get('seed', 'Unknown')}\n"
            
            # Prepare the question with context
            augmented_question = f"{data_context}\n\nQuestion: {data.question}"
            
            # Call the Gemini API with the context-augmented question
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            params = {
                "key": GEMINI_API_KEY
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": augmented_question
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 200,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            response = requests.post(url, headers=headers, params=params, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                try:
                    answer = response_data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    answer = "Sorry, I couldn't process the response from the AI model."
            else:
                logger.error(f"API Error: {response.status_code}, {response.text}")
                return {"answer": f"Error: {response.status_code}. The API couldn't process your request."}
            
            return {"answer": answer}
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return {"answer": f"I encountered an error: {str(e)}"}
    else:
        return {"answer": "I'm sorry, I don't have enough information to answer that question. Please try asking about the age, region, or number of records in the uploaded data."}    