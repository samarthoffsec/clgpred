import os
import subprocess

# 1. Setup Directories
INPUT_DIR = "./scraped_data/"
OUTPUT_DIR = "./structured_json/"

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. The Strict System Prompt
SYSTEM_INSTRUCTION = """
You are a strict data parsing agent for AlphaJEE. Your job is to convert unstructured college markdown data into a valid JSON object.
You must adhere strictly to the following keys and data types. 

Handling Missing Data:
- If a data point is marked as "NOT_FOUND", "NOT_FOUND_SEPARATELY", or "NOT_APPLICABLE", convert it to `null` (for numbers) or an empty array `[]` (for lists).

Expected JSON Schema:
{
  "college_name": "Full Name of the College",
  "nirf_engineering_rank": <integer or null>,
  "overall_median_ctc_lpa": <float or null>,
  "overall_placement_percentage": <float or null>,
  "cse_core_subjects": ["Subject 1", "Subject 2"],
  "ee_core_subjects": ["Subject 1", "Subject 2"],
  "sports_infrastructure": ["Facility 1", "Facility 2"],
  "student_clubs": ["Club 1", "Club 2"],
  "incubation_center_name": "Name of incubator or null",
  "notable_startups": ["Startup 1", "Startup 2"]
}

CRITICAL: Return ONLY the raw JSON block. Do not include any conversational text. 
"""

def clean_json_output(raw_output):
    """Strips markdown formatting if the CLI model adds it by mistake."""
    cleaned = raw_output.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def process_file(filename):
    input_path = os.path.join(INPUT_DIR, filename)
    json_filename = filename.replace("_raw.txt", ".json")
    output_path = os.path.join(OUTPUT_DIR, json_filename)
    
    # Skip if we already generated the JSON for this file
    if os.path.exists(output_path):
        print(f"⏩ Skipping {filename}, JSON already exists.")
        return

    print(f"🔄 Parsing {filename} into JSON...")
    
    # Read the original untouched text file
    with open(input_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
        
    # Combine the instruction and the raw data
    full_prompt = f"{SYSTEM_INSTRUCTION}\n\nRAW DATA TO PARSE:\n{raw_content}"
    
    try:
        # Call the Gemini CLI via subprocess
        process = subprocess.Popen(
            ['gemini'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=full_prompt)
        
        if process.returncode == 0 and stdout.strip():
            final_json = clean_json_output(stdout)
            
            # Write safely to the new JSON file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_json)
                
            print(f"✅ Successfully created {json_filename}")
        else:
            print(f"❌ CLI Error on {filename}: {stderr}")
            
    except Exception as e:
        print(f"💥 Failed executing CLI for {filename}: {str(e)}")

def main():
    print(f"📂 Scanning {INPUT_DIR} for raw text files")
    
    files_to_process = [f for f in os.listdir(INPUT_DIR) if f.endswith("_raw.txt")]
    
    if not files_to_process:
        print("No raw text files found. Make sure your Playwright script has run first.")
        return
        
    for file in files_to_process:
        process_file(file)
        
    print("🎉 All files serialized successfully!")

if __name__ == "__main__":
    main()