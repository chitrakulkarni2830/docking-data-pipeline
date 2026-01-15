import requests
import sqlite3
import csv
import random
import time
from rdkit import Chem
from rdkit.Chem import Descriptors

# ------------------------------------------------------------------------------
# 1. CONSTANTS & CONFIGURATION
# ------------------------------------------------------------------------------

# Define our list of compounds to screen.
# We have 5 Natural Substrates and 5 Synthetic Inhibitors.
NATURAL_SUBSTRATES = [
    "Dihydrofolate",
    "Folic Acid"]
import requests  # Used to fetch data from the internet (PubChem)
import sqlite3   # Used to create and manage the database
import csv       # Used to create the Excel-compatible CSV file
import random    # Used to generate random numbers for our simulation
import time      # Used to pause the script so we don't overwhelm the API
from rdkit import Chem             # RDKit is a chemistry library
from rdkit.Chem import Descriptors # We used this specifically to calculate LogP

# ==============================================================================
# SECTION 1: SETTING UP OUR DATA LISTS
# ==============================================================================

# We define two lists of drug names.
# One list for "Natural Substrates" (found in nature).
NATURAL_SUBSTRATES = [
    "Dihydrofolate",
    "Folic Acid",
    "Tetrahydrofolate",
    "7,8-Dihydrobiopterin",
    "L-Methionine"
]

# One list for "Synthetic Inhibitors" (man-made drugs).
SYNTHETIC_INHIBITORS = [
    "Methotrexate",
    "Pemetrexed",
    "Aminopterin",
    "Trimethoprim",
    "Pyrimethamine"
]

# This is the "address" of the PubChem database API we will talk to.
# The curly braces {} are a placeholder where we will put the drug name later.
BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/MolecularWeight,IsomericSMILES/JSON"

# ==============================================================================
# SECTION 2: DEFINING OUR TOOLS (FUNCTIONS)
# ==============================================================================

def get_compound_data(drug_name):
    """
    This function takes a 'drug_name' (text), asks PubChem for its details,
    and returns its SMILES string (structure) and Molecular Weight.
    """
    print(f"--- Processing: {drug_name} ---")
    print(f"  Step 1: Connecting to PubChem for {drug_name}...")
    
    # We insert the specific drug name into our URL.
    request_url = BASE_URL.format(drug_name)
    
    # We identify ourselves to the website so they don't block us.
    my_headers = {'User-Agent': 'StudentPortfolioProject/1.0'}
    
    try:
        # We send the request to the website.
        response = requests.get(request_url, headers=my_headers, timeout=10)
        
        # We check if the website replied with "200 OK".
        if response.status_code == 200:
            # We convert the text response into a Python dictionary (JSON data).
            json_data = response.json()
            
            # PubChem data is nested (like a box inside a box). We need to dig in.
            # We look for the 'PropertyTable' and then the list of 'Properties'.
            properties_list = json_data['PropertyTable']['Properties']
            first_result = properties_list[0]
            
            # Now we extract the specific info we want.
            # We look for SMILES (structure) and MolecularWeight.
            
            # Note: Sometimes the database uses slightly different keys for SMILES.
            # We check a few possibilities to be safe.
            smiles_string = first_result.get('IsomericSMILES')
            if not smiles_string:
                smiles_string = first_result.get('CanonicalSMILES')
            if not smiles_string:
                smiles_string = first_result.get('SMILES')
                
            molecular_weight = first_result.get('MolecularWeight')
            
            print(f"  Step 2: Check! Found MW: {molecular_weight}")
            return smiles_string, molecular_weight
            
        else:
            # If the website didn't say "OK", we print the error code.
            print(f"  Error: Website returned status code {response.status_code}")
            return None, None
            
    except Exception as error_message:
        # If something crashes (like no internet), we catch the error here.
        print(f"  Critical Error: {error_message}")
        return None, None


def calculate_logp(smiles_string):
    """
    This function uses RDKit to calculate the LogP (lipophilicity) value.
    LogP tells us how well a drug mixes with oil vs water.
    """
    if smiles_string is None:
        return 0.0
        
    try:
        # Convert the text string (SMILES) into a chemistry object RDKit understands.
        molecule = Chem.MolFromSmiles(smiles_string)
        
        if molecule:
            # Calculate the LogP value.
            log_p_value = Descriptors.MolLogP(molecule)
            # Round it to 4 decimal places to make it look nice.
            return round(log_p_value, 4)
            
    except Exception:
        print("  Error: Could not calculate LogP.")
        
    return 0.0


def run_docking_simulation(drug_type):
    """
    This generates a FAKE docking score for our project context.
    'Docking score' represents how tightly the drug binds to the protein.
    More negative numbers = tighter binding (better).
    
    We add a simple rule: 'Synthetic' drugs get slightly better scores 
    than 'Natural' ones on average.
    """
    # Pick a random number between -6.0 and -10.0
    random_score = random.uniform(-6.0, -10.0)
    
    if drug_type == "Synthetic":
        # Make the score even lower (better) by subtracting extra points.
        bonus = random.uniform(1.0, 2.0)
        final_score = random_score - bonus
    else:
        # Natural substrates keep the base score.
        final_score = random_score
        
    return round(final_score, 2)


def create_database():
    """
    Creates a new empty database file called 'results.db' with a table.
    """
    print("\nSetting up the database...")
    # Connect to the database file (it creates it if it doesn't exist).
    connection = sqlite3.connect('results.db')
    cursor = connection.cursor()
    
    # First, drop the table if it already exists so we start fresh.
    cursor.execute('DROP TABLE IF EXISTS screening_results')

    # Create the table named 'screening_results' with columns for our data.
    cursor.execute('''
        CREATE TABLE screening_results (
            name TEXT,
            type TEXT,
            smiles TEXT,
            mw REAL,
            logp REAL,
            score REAL
        )
    ''')
    
    connection.commit() # Save changes.
    connection.close()  # Close connection.


def save_result_to_db(name, drug_type, smiles, mw, logp, score):
    """
    Saves one single row of data into our database.
    """
    connection = sqlite3.connect('results.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO screening_results VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, drug_type, smiles, mw, logp, score))
    
    connection.commit()
    connection.close()


def export_to_csv():
    """
    Reads all data from the database and saves it to a CSV file.
    """
    print("\nExporting data to CSV file...")
    connection = sqlite3.connect('results.db')
    cursor = connection.cursor()
    
    # Get all rows.
    cursor.execute("SELECT * FROM screening_results")
    all_rows = cursor.fetchall()
    
    # write to file 'natvssynt.csv'.
    with open('natvssynt.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header (column names).
        writer.writerow(["Name", "Type", "SMILES", "Molecular Weight", "LogP", "Score"])
        # Write all the data.
        writer.writerows(all_rows)
        
    connection.close()
    print("Success! File 'natvssynt.csv' created.")


# ==============================================================================
# SECTION 3: MAIN EXECUTION (Where the script starts running)
# ==============================================================================

def main():
    # 1. First, we create the database.
    create_database()
    
    # 2. We combine our two lists into one big list of items to process.
    # We use a simple loop to build this.
    all_items_to_process = []
    
    for name in NATURAL_SUBSTRATES:
        # We attach the label "Natural" to the name.
        all_items_to_process.append((name, "Natural"))
        
    for name in SYNTHETIC_INHIBITORS:
        # We attach the label "Synthetic" to the name.
        all_items_to_process.append((name, "Synthetic"))
    
    # 3. Now we loop through every single drug in our combined list.
    for current_drug in all_items_to_process:
        
        # Unpack the tuple (Name, Type)
        drug_name = current_drug[0]
        drug_type = current_drug[1]
        
        # A. Fetch data from the web.
        smiles_string, mw = get_compound_data(drug_name)
        
        # Only proceed if we successfully got the SMILES string.
        if smiles_string is not None:
            
            # B. Calculate LogP using RDKit.
            log_p = calculate_logp(smiles_string)
            
            # C. Run the "simulation" to get a score.
            affinity_score = run_docking_simulation(drug_type)
            
            # D. Save everything to the database.
            save_result_to_db(drug_name, drug_type, smiles_string, mw, log_p, affinity_score)
            
            print(f"  Step 3: Done! Score = {affinity_score}")
        
        else:
            print(f"  Skipping {drug_name} because data was missing.")
            
        print("--------------------------------------------------")
        # Sleep for 1 second to be polite to the API.
        time.sleep(1)
        
    # 4. Finally, export everything to CSV.
    export_to_csv()
    print("\nAll done! You can check 'natvssynt.csv' now.")

# This line checks if we are running this script directly.
if __name__ == "__main__":
    main()

