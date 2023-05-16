# Fuzzy Matching

This notebook compares "official" organization names from two databases: the Orbis company name database, and the GDELT knowledge graph. Orbis company names are reconciled with alternative organization identifiers, taking in an Orbis company name and returning all alternative names mentioned in the GDELT dataset, such as alternative spellings and naming variations that refer to the same organization.

Video demo: [https://drive.google.com/file/d/1SKS0D7L4ChkmMsverInDZV472-QIYtRR/view?usp=sharing](https://drive.google.com/file/d/1SKS0D7L4ChkmMsverInDZV472-QIYtRR/view?usp=sharing).

## Requirements
#### System:
- Python 2.7 or higher

#### Packages:
- openpyxl
- cleanco
- py_stringsimjoin
- py_stringmatching
- fuzzywuzzy
- jellyfish

## Setup
Open the project directory and verify that these six items are present:
- `README.md`
- `fuzzy_matching.py`
- `fuzzy_matching.ipynb`
- `fuzzy_matching.html`
- `./input`
- `./output`

## Input data
You can save a CSV file of an Orbis database query and a CSV file of a GDELT database query of news articles in the `./input` folder. 

Test input data: [https://drive.google.com/drive/folders/1W-YW7AgZFmaURkman-IAp5vNUk56qKGS?usp=sharing](https://drive.google.com/drive/folders/1W-YW7AgZFmaURkman-IAp5vNUk56qKGS?usp=sharing)

## Output data
Is saved in the `./output` folder. CSV files are saved while execution processes to save progress and provide an option to stop execution and resume at a later time using the stored CSV data.

Final output containing a dictionary of matches is saved in the `./output` folder as `OUTPUT.csv`.

Test output using data from Sierra Leone in 2020: [https://drive.google.com/drive/folders/1mFuDGppvwxO-T09agvrkdHo9sSU-f3ko?usp=sharing](https://drive.google.com/drive/folders/1mFuDGppvwxO-T09agvrkdHo9sSU-f3ko?usp=sharing)

## Usage
1. Verify there are two files in the `./input` folder:
   - An Excel dataset of "official" Orbis organization names.
   - A CSV dataset GDELT of news articles.
2. Configure execution settings:
   - Set the ORBIS_INPUT relative file path
   - Set the GDELT_INPUT relative file path
   - Set the number of Orbis rows to process; each row represents one company
   - Set the number and range of GDELT rows to process; each row represents one article, and the number of articles is the difference between the start and end rows.
3. Execute the notebook:
   - You can run the entire notebook from cell 1 to the last cell.
   - All output data is saved in the `./output` folder in CSV format.
   - The notebook saves execution progress as CSV data in the `./output` folder while the code is executed.
   - If execution stops, it can be resumed by starting at the most recent cell that loads a progress output file.
   - Keep the saved progress output files to avoid unnecessary re-execution of all cells.
4. Manipulate filter match threshold:
   - You can manipulate the various scoring and filtering methods by looking at the comments and testing different configurations.
   - Default scoring:
     - fuzz_score = fuzz_ratio + fuzz_partial_ratio + fuzz_token_sort_ratio (Score between 0 and 300)
     - jaro_distance (Score between 0 and 1)
   - Default scoring threshold of likely matches:
     - fuzz_score > 280 and jaro_distance > 0.9
4. Get the output:
   - Final output is saved as `OUTPUT.csv` in the `./output` directory.
 
## Match threshold settings
The "match threshold" cell allows you to change and mix/match different scoring thresholds to experiment with accuracy and sensitivity. This is a time-consuming process and will require continuous improvement.

![Match threshold cell](./match_threshold.png)

## Additional notes
1. Error analysis is not present in this notebook.
    - This is could be added to this notebook to help find optimal match score thresholds.
2. Currently, only fuzz similarity and jaro-wrinkler distances are used to determine matches.
    - Additional scores, such as cosine simularity, are included but _not_ used in the final threshold step; more experimentation will help determine how to include the additional measurements.
2. Large datasets will take a long time to process.
    - 36,000 GDELT articles and 2700 Orbis company names can take over 8 hours to process on a 6-core systeem.
3. If input file types change (from CSV to Excel, for example) make sure to tweak the pandas code that loads the input file.
    - Change `pd.read_csv()` to `pd.read_excel()` or vice versa.

## Next steps
1. Find an optimal match threshold by mixing and adjusting the various scoring measures.
2. Determine an efficient method of error analysis.
3. Research an effective method to match acronyms with full names by using surrounding contextual information.
