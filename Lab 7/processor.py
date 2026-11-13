
def sanitize_license_plate(plate):
    if not isinstance(plate, str):
        return ""

    plate = plate.strip()

    for ch in ['-', ' ', '_', '#']:
        plate = plate.replace(ch, '')

    return plate.upper()


def parse_trip_mileage(mileage_csv):
    if not isinstance(mileage_csv, str):
        return []

    if not mileage_csv.strip():
        return []

    try:
        parts = mileage_csv.split(',')
        mileages = []

        for m in parts:
            value = m.strip()

            if not value:
                return []

            mileage = float(value)

            if mileage < 0:
                return []

            mileages.append(mileage)

        return mileages

    except ValueError:
        return []


def format_rental_invoice(record):
    if not isinstance(record, str):
        return "Invalid rental record"

    try:
        parts = record.split(':')

        if len(parts) != 3:
            return "Invalid rental record"

        driver = parts[0].strip()
        days = int(parts[1].strip())
        category = parts[2].strip()

        if not driver or not category or days <= 0:
            return "Invalid rental record"

        daily_rate = 50.0 if category.lower() == "suv" else 30.0
        total = days * daily_rate

        return (
            f"Driver {driver} booked {category} "
            f"for {days} days: Total ${total:.2f}"
        )

    except ValueError:
        return "Invalid rental record"


def main():
    print("==== Running sanitize_license_plate ====")
    raw_plate = input("Enter license plate with delimiters (-, _, #): ")
    clean_plate = sanitize_license_plate(raw_plate)
    print("Sanitized Plate:", clean_plate)

    print("\n==== Running parse_trip_mileage ====")
    csv_input = input("Enter CSV of mileages (e.g. 100.5, 45.2, 80.0): ")
    mileage_list = parse_trip_mileage(csv_input)
    print("Parsed Mileage List:", mileage_list)

    print("\n==== Running format_rental_invoice ====")
    record_input = input("Enter rental record (Driver:Days:Category): ")
    invoice = format_rental_invoice(record_input)
    print("Rental Invoice:", invoice)


if __name__ == "__main__":
    main()
