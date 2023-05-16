import pickle, os
import pandas as pd

curr_dir = os.path.dirname(os.path.realpath(__file__))
logger_path = os.path.join(curr_dir, "logger.csv")
records_path = os.path.join(curr_dir, "dwn_map.pkl")

# Method to update logger.csv with the latest checkpoint
def update_logger():
    df = pd.read_csv(logger_path)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    old_id = max(df["data-record-id"])

    dwn_map = None
    with open(records_path, "rb") as handle:
        dwn_map = pickle.load(handle)

    reps = dwn_map["report"]
    tears = dwn_map["tearsheet"]
    indreps = dwn_map["industry-report"]
    ids = dwn_map["data-record-id"]
    comps = dwn_map["name"]

    min_len = min(len(reps), len(tears), len(indreps), len(ids), len(comps))
    reps = reps[:min_len]
    tears = tears[:min_len]
    indreps = indreps[:min_len]
    ids = ids[:min_len]
    comps = comps[:min_len]

    reps = df["report"].tolist() + reps
    tears = df["tearsheet"].tolist() + tears
    indreps = df["industry-report"].tolist() + indreps
    ids = df["data-record-id"].tolist() + ids
    comps = df["name"].tolist() + comps

    dwn_map_new = {"report": reps, "tearsheet": tears, "industry-report": indreps, "data-record-id": ids, "name": comps}
    df_new = pd.DataFrame.from_dict(dwn_map_new)
    new_id = max(df_new["data-record-id"])

    # Save the updated logger
    df_new.to_csv(logger_path)
    print(f"Updated logger from id = {old_id} to id = {new_id}")
    return True

if __name__ == "__main__":
    update_logger()