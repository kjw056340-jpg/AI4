def can_edit(role: str) -> bool:
    return "admin" in role

if __name__ == "__main__":
    print(can_edit("not-admin"))
