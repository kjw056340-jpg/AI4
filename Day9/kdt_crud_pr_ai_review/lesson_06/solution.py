def summarize_changes(changes: list[dict]) -> dict:
    return {"changed": [c["path"] for c in changes]}

if __name__ == "__main__":
    print(summarize_changes([{"path": "old.py", "status": "deleted"}]))
