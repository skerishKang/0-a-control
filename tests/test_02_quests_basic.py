from scripts.db_base import connect


def main() -> None:
    with connect() as conn:
        quests = conn.execute(
            "SELECT id, title, status FROM quests LIMIT 5"
        ).fetchall()
    print([dict(q) for q in quests])


if __name__ == "__main__":
    main()
