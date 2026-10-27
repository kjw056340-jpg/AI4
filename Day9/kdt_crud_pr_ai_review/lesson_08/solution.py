def combine_tasks(main_tasks: list[dict], feature_tasks: list[dict]) -> list[dict]:
    by_id = {task["id"]: task for task in main_tasks}
    for task in feature_tasks:
        by_id[task["id"]] = task
    return [by_id[key] for key in sorted(by_id)]

if __name__ == "__main__":
    print(combine_tasks([{"id": 1}], [{"id": 2}]))
