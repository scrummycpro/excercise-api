import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json
import random

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

# Function to get 6 random exercises for a specific muscle or all muscles
def get_six_random_exercises(muscle: str = None):
    if muscle:
        exercises_for_muscle = df[df['Target_Muscles'].str.contains(muscle, case=False, na=False)]
        if len(exercises_for_muscle) == 0:
            raise ValueError(f"No exercises found for the muscle: {muscle}")
        if len(exercises_for_muscle) <= 6:
            # If there are fewer than or equal to 6 exercises for that muscle, return all
            selected_exercises = exercises_for_muscle.to_dict(orient="records")
        else:
            # Otherwise, randomly sample 6 exercises
            selected_exercises = exercises_for_muscle.sample(6).to_dict(orient="records")
        return {muscle: selected_exercises}
    
    # If no specific muscle is given, return 6 random exercises per muscle
    muscles = df['Target_Muscles'].unique()  # Get all unique muscle groups
    random_exercises = {}

    for muscle in muscles:
        exercises_for_muscle = df[df['Target_Muscles'].str.contains(muscle, case=False, na=False)]
        if len(exercises_for_muscle) <= 6:
            selected_exercises = exercises_for_muscle.to_dict(orient="records")
        else:
            selected_exercises = exercises_for_muscle.sample(6).to_dict(orient="records")
        
        random_exercises[muscle] = selected_exercises

    return random_exercises

# Function to get one random exercise for a specific muscle or all muscles
def get_one_random_exercise(muscle: str = None):
    if muscle:
        exercises_for_muscle = df[df['Target_Muscles'].str.contains(muscle, case=False, na=False)]
        if len(exercises_for_muscle) == 0:
            raise ValueError(f"No exercises found for the muscle: {muscle}")
        selected_exercise = exercises_for_muscle.sample(1).to_dict(orient="records")
        return {muscle: selected_exercise}
    
    # If no specific muscle is given, return one random exercise per muscle
    muscles = df['Target_Muscles'].unique()  # Get all unique muscle groups
    random_exercises = {}

    for muscle in muscles:
        exercises_for_muscle = df[df['Target_Muscles'].str.contains(muscle, case=False, na=False)]
        selected_exercise = exercises_for_muscle.sample(1).to_dict(orient="records")
        random_exercises[muscle] = selected_exercise

    return random_exercises

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

# Random 6 exercises per muscle group endpoint with optional muscle input
@app.get("/six_exercises_per_muscle", response_class=CustomJSONResponse)
def six_exercises_per_muscle(muscle: str = None):
    try:
        exercises = get_six_random_exercises(muscle)
    except ValueError as e:
        return {"error": str(e)}

    return exercises

# One random exercise per muscle group endpoint with optional muscle input
@app.get("/one_exercise_per_muscle", response_class=CustomJSONResponse)
def one_exercise_per_muscle(muscle: str = None):
    try:
        exercises = get_one_random_exercise(muscle)
    except ValueError as e:
        return {"error": str(e)}

    return exercises