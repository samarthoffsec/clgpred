import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

# 1. Ensure the output directory exists
os.makedirs("./scraped_data", exist_ok=True)

# 2. Define the 15 IIT targets
IIT_TARGETS = [
    {"name": "Indian Institute of Technology Bombay", "short": "IIT_Bombay", "url": "https://www.iitb.ac.in"},
    {"name": "Indian Institute of Technology Delhi", "short": "IIT_Delhi", "url": "https://home.iitd.ac.in"},
    {"name": "Indian Institute of Technology Madras", "short": "IIT_Madras", "url": "https://www.iitm.ac.in"},
    {"name": "Indian Institute of Technology Kanpur", "short": "IIT_Kanpur", "url": "https://www.iitk.ac.in"},
    {"name": "Indian Institute of Technology Kharagpur", "short": "IIT_Kharagpur", "url": "https://www.iitkgp.ac.in"},
    {"name": "Indian Institute of Technology Roorkee", "short": "IIT_Roorkee", "url": "https://www.iitr.ac.in"},
    {"name": "Indian Institute of Technology Guwahati", "short": "IIT_Guwahati", "url": "https://www.iitg.ac.in"},
    {"name": "Indian Institute of Technology Hyderabad", "short": "IIT_Hyderabad", "url": "https://www.iith.ac.in"},
    {"name": "Indian Institute of Technology (BHU) Varanasi", "short": "IIT_BHU", "url": "https://iitbhu.ac.in"},
    {"name": "Indian Institute of Technology Indore", "short": "IIT_Indore", "url": "https://www.iiti.ac.in"},
    {"name": "Indian Institute of Technology Gandhinagar", "short": "IIT_Gandhinagar", "url": "https://iitgn.ac.in"},
    {"name": "Indian Institute of Technology Bhubaneswar", "short": "IIT_Bhubaneswar", "url": "https://www.iitbbs.ac.in"},
    {"name": "Indian Institute of Technology Ropar", "short": "IIT_Ropar", "url": "https://www.iitrpr.ac.in"},
    {"name": "Indian Institute of Technology Mandi", "short": "IIT_Mandi", "url": "https://www.iitmandi.ac.in"},
    {"name": "Indian Institute of Technology Jodhpur", "short": "IIT_Jodhpur", "url": "https://www.iitj.ac.in"}
]

# 3. Clean Master Prompt Template (Explicit terminal output instruction)
MASTER_PROMPT_TEMPLATE = """
You are acting as an automated data aggregation agent for AlphaJEE. Your task is to navigate the web using Playwright to extract concrete, verifiable facts about {iit_name} (URL: {base_url}).

### TARGET DATA POINTS TO EXTRACT:
1. NIRF Ranking: Latest engineering rank.
2. Branch-wise Placements: Look for the official Training & Placement (TPO) cell or Gymkhana placement report. Extract average CTC, median CTC, and placement percentages specifically for CSE, ECE, EE, and ME if visible.
3. Curriculum/Course Structure: Locate the academic curriculum or syllabus page for undergraduate (B.Tech) courses. Extract the names of core subjects for CSE and ECE/EE and all mentioned branches on the website(e.g., OS, DBMS, VLSI Design).
4. Campus Life & Infrastructure: Find official pages for the Gymkhana or Student Affairs. Extract lists of sports facilities (e.g., Olympic-size pool, athletic tracks) and active cultural/technical clubs.
5. Startup Incubation: Locate the E-Cell (Entrepreneurship Cell) or official TBI (Technology Business Incubator). Extract its name, presence, and any notable supported startups or key facilities.
6. Wikipedia: Locate the official Wikipedia page of the college and cross-verify your details, and also fetch details which you could not find on the official site. Make sure the fetched detail has at least one source cited.

### MANDATORY RUNTIME GUARDRAILS:
- NO ESTIMATIONS / NO OPINIONS: Do not extract blogs, student forums (Quora, Reddit), or opinion pieces. Rely ONLY on official domain suffixes (.ac.in, .org) or the official Wikipedia page summary as a backup.
- STRICT DATA FIDELITY (NO GUESSING): Do not estimate salary ranges or extrapolate based on overall departmental performance. If branch-specific data (e.g., CSE median CTC) is not explicitly stated in the official report, you must output exactly: `NOT_FOUND_SEPARATELY`.
- BRANCH AVAILABILITY FORMATTING: Do not write conversational notes in value fields. If a branch (like ECE) does not exist natively or is grouped under another department, output exactly: `NOT_APPLICABLE (Merged with [Branch Name])`.
- MAXIMUM NAVIGATION DEPTH: Do not click deeper than 3 layers from the provided {base_url} or your search result.
- TIMEOUT HANDLING: If a page takes longer than 15 seconds to load or throws a 403/404 error, immediately take a screenshot, log the error, go back, and try an alternative link or use the official Wikipedia page.
- INFIDELITY PREVENTION: If a specific data point (like the exact incubation budget) is not explicitly listed on the site, write `NOT_FOUND` for that field. Do NOT guess or generalize based on your training data.

### OUTPUT INSTRUCTIONS:
When all data points are gathered or alternatives are exhausted, format your findings into a clear, un-nested Markdown structure. Do not format it into JSON yet.

CRITICAL: Output your final formatted Markdown report directly into the terminal response. Do not use any file tools or attempt to write to disk. Just print it clearly.

Begin by using a search engine or navigating directly to {base_url}.
"""

def run_agent(target):
    print(f" [STARTING]: Agent for {target['short']}")
    
    # Clean injection without appending weird lines later
    formatted_prompt = MASTER_PROMPT_TEMPLATE.format(
        iit_name=target['name'],
        base_url=target['url']
    )
    
    try:
        process = subprocess.Popen(
            ['gemini'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Capture the terminal output from the agent
        stdout, stderr = process.communicate(input=formatted_prompt)
        
        if process.returncode == 0 and stdout.strip():
            # Python writes the file cleanly to disk
            file_path = f"./scraped_data/{target['short']}_raw.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(stdout.strip())
            print(f" [SUCCESS]: Saved data to {file_path}")
        else:
            print(f"❌ [ERROR]: {target['short']} failed. Exit code {process.returncode}. Stderr: {stderr}")
            
    except Exception as e:
        print(f" [CRITICAL]: Failed executing agent for {target['short']}: {str(e)}")

def main():
    # Set concurrent browsers (adjust based on your machine's power)
    MAX_CONCURRENT_BROWSERS = 4
    
    print(f"Initializing scraping engine pool with {MAX_CONCURRENT_BROWSERS} parallel workers...")
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_BROWSERS) as executor:
        executor.map(run_agent, IIT_TARGETS)

if __name__ == "__main__":
    main()
