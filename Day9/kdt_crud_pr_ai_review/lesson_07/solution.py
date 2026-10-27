def can_edit(role: str) -> bool:
    return role == "admin"

if __name__ == "__main__":
    print(can_edit("not-admin"))
