import json
import time

# SAVING---------------------------------------------------------------
def saving_user_input(user_input, field_name):
    try:
        with open("user_input.json", "r") as file:
            content = file.read().strip()
            history = json.loads(content) if content else {"entries": []}
    except (FileNotFoundError, json.JSONDecodeError):
        history = {"entries": []}

    if not history["entries"] or "completed_at" in history["entries"][-1]:
        # making it create a new entry
        new_entry = {
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "answers": {}
        }
        history["entries"].append(new_entry)

    # adds user to the end
    history["entries"][-1]["answers"][field_name] = user_input
    
    # saving
    with open("user_input.json", "w") as file:
        json.dump(history, file, indent=4)
    # print("saved")

def complete_entry():
    try:
        with open("user_input.json", "r") as file:
            history = json.loads(file.read())
            if history["entries"]:
                history["entries"][-1]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("user_input.json", "w") as file:
            json.dump(history, file, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        pass