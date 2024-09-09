import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json

# Custom JSON Response to handle NaN and Infinity values (optional if you want to allow NaN in JSON)
class CustomJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        # Allows handling NaN, Infinity values by forcing them into valid JSON
        return json.dumps(content, allow_nan=True).encode("utf-8")

app = FastAPI()

# Construct the file path to the CSV file
csv_file_path = os.path.join(os.getcwd(), "data", "gym_exercise_dataset.csv")

# Check if the file exists
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"CSV file not found at path: {csv_file_path}")

# Load CSV into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Clean the data by replacing Infinity and NaN values with an appropriate default
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.fillna("", inplace=True)  # Replace NaN with an empty string

# Utility function to search in the CSV data
def search_csv(column: str, value: str):
    # Perform case-insensitive search
    result = df[df[column].str.contains(value, case=False, na=False)]
    
    # Return result as a dictionary that can be converted to JSON
    return result.to_dict(orient="records")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Exercise Search API"}

# Search endpoint
@app.get("/search", response_class=CustomJSONResponse)  # Optional: if you want to allow NaN in JSON
def search(
    column: str = Query(..., description="Column to search in (e.g., 'Exercise Name', 'Target_Muscles')"),
    value: str = Query(..., description="Value to search for")
):
    # Ensure the column exists in the DataFrame
    if column not in df.columns:
        return {"error": f"Invalid column name: {column}. Available columns: {list(df.columns)}"}
    
    # Get search results
    results = search_csv(column, value)
    
    # If no results found
    if not results:
        return {"message": "No matching records found."}
    
    # Return results
    return results