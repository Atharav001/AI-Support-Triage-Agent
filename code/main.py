import os
import random
import numpy as np
import pandas as pd
import concurrent.futures
from agent import SupportAgent
import config

# Deterministic setup
random.seed(42)
np.random.seed(42)

def process_single(idx, row, agent):
    issue_str = str(row.get('issue', ''))
    subject_str = str(row.get('subject', ''))
    company_str = row.get('company', None)
    try:
        res = agent.process_ticket(issue_str, subject_str, company_str)
    except Exception as e:
        res = {
            "status": "escalated",
            "product_area": "general",
            "response": "Error processing ticket.",
            "justification": str(e),
            "request_type": "product_issue"
        }
    res["issue"] = issue_str
    res["subject"] = subject_str
    res["company"] = company_str
    return idx, res

def main():
    print(f"Loading support tickets from {config.INPUT_CSV}...")
    try:
        df = pd.read_csv(config.INPUT_CSV)
        df.columns = [str(c).lower() for c in df.columns]
    except FileNotFoundError:
        print(f"Error: Could not find {config.INPUT_CSV}")
        return
        
    print("Initializing agent (loading documents and embeddings)...")
    agent = SupportAgent()
    
    results = {}
    print(f"Processing {len(df)} tickets...")
    
    # Process concurrently with max_workers=3
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_single, idx, row, agent): idx for idx, row in df.iterrows()}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            idx, res = future.result()
            results[idx] = res
            completed += 1
            if completed % 5 == 0 or completed == len(df):
                print(f"Processed {completed}/{len(df)} tickets...")
                
    # Reconstruct in original order
    ordered_results = [results[i] for i in range(len(df))]
    out_df = pd.DataFrame(ordered_results)
    
    # Ensure all required columns are present
    cols = ["issue", "subject", "company", "response", "product_area", "status", "request_type", "justification"]
    for col in cols:
        if col not in out_df.columns:
            out_df[col] = ""
    out_df = out_df[cols]
    
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    out_df.to_csv(config.OUTPUT_CSV, index=False)
    print(f"Processing complete. Results saved to {config.OUTPUT_CSV}.")

if __name__ == "__main__":
    main()
