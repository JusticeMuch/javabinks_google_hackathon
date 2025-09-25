import pandas as pd
from random import randint
import json
import vertexai
from vertexai.generative_models import GenerativeModel

# --------------------------
# 1. Configure your project
# --------------------------
PROJECT_ID = "hackathon-25-09-2025"
REGION = "us-central1"  # adjust if needed
MODEL_ID = "gemini-2.5-flash"
BUDGET_TOTAL = 10_000_000_000  # example total budget in ZAR


# --------------------------
# 2. Read historical budget data
# --------------------------
# CSV should have at least columns: time,item_id,target
#csv_file = "cape_town_budget.csv"
#df = pd.read_csv(csv_file)

# Optionally, convert to string table
#data_str = df.to_csv(index=False)

# --------------------------
# 1. Generate dummy data
# --------------------------
sectors = ["Water", "Health", "Education", "Sanitation", "Roads"]
years = [2019, 2020, 2021, 2022, 2023, 2024]
months = list(range(1, 13))

data = []

for year in years:
    for month in months:
        for sector in sectors:
            # dummy spend value
            amount = randint(1_000_000, 5_000_000)
            date_str = f"{year}-{month:02d}-01"
            data.append([date_str, sector, amount])

df = pd.DataFrame(data, columns=["time", "item_id", "target"])

# Convert to CSV string for prompt
data_str = df.to_csv(index=False)

# --------------------------
# 3. Build the prompt
# --------------------------
prompt = f"""
You are a municipal budget planning AI. 
Here is Cape Town's historical budget data (time,item_id,target):

{data_str}

Based on the past few years, provide a forecast for the next financial year's required amounts per sector. 
Then allocate a total budget of {BUDGET_TOTAL} ZAR across sectors.
Constraints:
- Health >= 2_000_000_000
- Water >= 1_000_000_000
- Education >= 1_500_000_000

Only output your response as a raw JSON array of objects, showing sector, forecast and allocation. Do not
provide code or any other commentary. JUST give the raw JSON array of objects, with the specified fields.
"""

# --------------------------
# 4. Initialize Vertex AI (Generative AI)
# --------------------------
vertexai.init(project=PROJECT_ID, location=REGION)

# --------------------------
# 5. Generate response from Gemini (GenerativeModel API)
# --------------------------
model = GenerativeModel(MODEL_ID)
try:
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.2, "max_output_tokens": 10000},
    )
except Exception as e:
    raise RuntimeError(
        f"Failed to call model '{MODEL_ID}' in region '{REGION}'. "
        "Ensure the Vertex AI API is enabled, your project has access to this model, "
        "and consider trying 'gemini-2.0-flash' if unavailable."
    ) from e

# The model returns text content
result_text = response.text
print("Raw model output:\n", result_text)

# --------------------------
# 6. Parse JSON output
# --------------------------
try:
    lines = result_text.splitlines()
    if len(lines) > 2:
        json_text = "\n".join(lines[1:-1])
    elif len(lines) == 2:
        json_text = lines[1]
    else:
        json_text = result_text
    allocation_json = json.loads(json_text)
    print("\nParsed JSON allocation:")
    for item in allocation_json:
        print(item)
except json.JSONDecodeError:
    print("\nCould not parse JSON. Model output:")
    print(result_text)
