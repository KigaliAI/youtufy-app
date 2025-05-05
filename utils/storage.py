import os
import json

def save_user_data(user_email, data, filename="youtube_subscriptions.json"):
    user_dir = f"users/{user_email}"
    os.makedirs(user_dir, exist_ok=True)
    with open(f"{user_dir}/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_user_data(user_email, filename="youtube_subscriptions.json"):
    user_file = f"users/{user_email}/{filename}"
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []