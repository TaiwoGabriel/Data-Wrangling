import pickle, os
import pandas as pd

if __name__ == "__main__":

    curr_dir = os.path.dirname(os.path.realpath(__file__))
    # These files will be used to keep track and record downloaded reports
    csvs = os.path.join(curr_dir, "logger.csv")
    records = os.path.join(curr_dir, "dwn_map.pkl")

    # Create a dummy entry in the CSV
    dwn_map = {"report": ["No"], "tearsheet": ["No"], "industry-report": ["No"], "data-record-id": [-100], "name": ["Dummy Entry"]}
    df = pd.DataFrame.from_dict(dwn_map)
    with open(records, 'wb') as handle:
        pickle.dump(dwn_map, handle, protocol=pickle.HIGHEST_PROTOCOL)
    df.to_csv(csvs)

    # Finally create a directory to store all the reports
    dir_path = os.path.join(curr_dir, "MSCI_Reports")
    os.mkdir(dir_path)