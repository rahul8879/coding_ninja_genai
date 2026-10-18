import csv
from sqlalchemy.dialects.postgresql import insert
from app.db.database import PROJECT_ROOT, engine
from app.db.models import Base, Doctor

def main():
    csv_path = PROJECT_ROOT / "data" / "doctors.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    fields = [column.name for column in Doctor.__table__.columns if column.name != "id"]
    records, seen_emails = [], set()
    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = set(fields) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {sorted(missing)}")
        for line_number, row in enumerate(reader, start=2):
            record = {field: (row.get(field) or "").strip() for field in fields}
            if not record["name"] or not record["specialty"]:
                raise ValueError(f"Line {line_number}: name and specialty are required")
            email = record["email"].lower()
            if not email or email in seen_emails:
                raise ValueError(f"Line {line_number}: missing or duplicate email")
            record["email"] = email
            seen_emails.add(email)
            record["experience_years"] = int(record["experience_years"])
            record["rating"] = float(record["rating"])
            if record["experience_years"] < 0 or not 0 <= record["rating"] <= 5:
                raise ValueError(f"Line {line_number}: invalid experience or rating")
            records.append(record)
    if not records:
        raise ValueError("CSV contains no doctor records")
    with engine.begin() as connection:
        Base.metadata.create_all(connection)
        statement = insert(Doctor.__table__).values(records)
        statement = statement.on_conflict_do_update(
            index_elements=["email"],
            set_={
                field: statement.excluded[field] for field in fields if field != "email"
            },
        )
        connection.execute(statement)
    print(f"Successfully imported/updated {len(records)} doctors.")



if __name__ == "__main__":
    main()