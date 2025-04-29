import pandas as pd
from .database import ancient_remains_db

def parse_and_store_csv(file):
    df = pd.read_csv(file)
    for _, row in df.iterrows():
        ancient_remains_db[row['id']] = {
            'region': row['region'],
            'age': row['age'],
            'seed': row['seed']
        }
    return {"message": f"Uploaded {len(df)} samples successfully"}

def calculate_similarity(seq1: str, seq2: str) -> float:
    matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
    length = min(len(seq1), len(seq2))
    return round(matches / length * 100, 2)
