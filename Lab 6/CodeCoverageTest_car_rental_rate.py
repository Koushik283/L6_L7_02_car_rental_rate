
import pytest

from car_rental_rate import (
    process_rental_fleet,
    check_fleet_telematics
)


def test_invalid_rental_input():
    with pytest.raises(ValueError):
        process_rental_fleet(None, 10.0)


def test_negative_admin_fee():
    with pytest.raises(ValueError):
        process_rental_fleet([], -5.0)


def test_empty_rental_batch():
    result = process_rental_fleet([], 10.0)

    assert result == {
        "total_revenue": 0.0,
        "status": "EMPTY_BATCH"
    }


def test_unconfirmed_rental():
    rentals = [
        {"is_confirmed": False, "days": 5}
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "EMPTY_BATCH"


def test_invalid_rental_days():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 0
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "EMPTY_BATCH"


@pytest.mark.parametrize(
    "vehicle_type, expected_revenue",
    [
        ("luxury", 250.0),
        ("suv", 150.0),
        ("economy", 90.0),
        ("unknown", 90.0)
    ]
)
def test_vehicle_types(vehicle_type, expected_revenue):
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": vehicle_type,
            "driver_age": 30,
            "days": 2,
            "trip_segments": []
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == expected_revenue
    assert result["status"] == "STANDARD"


def test_young_luxury_driver():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "luxury",
            "driver_age": 20,
            "days": 2,
            "trip_segments": []
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 350.0


def test_young_economy_driver():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 24,
            "days": 2,
            "trip_segments": []
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 130.0


def test_normal_and_boundary_mileage():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 2,
            "trip_segments": [100, 300]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 170.0


def test_negative_mileage():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-10, 50]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 60.0
    assert result["status"] == "STANDARD"


def test_high_mileage_adult_driver():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [350]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 190.0


def test_high_mileage_young_driver():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 20,
            "days": 1,
            "trip_segments": [350, 50]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 320.0


def test_high_risk_audit():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-1, -2, -3, -4, -5]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "HIGH_RISK_AUDIT"
    assert result["total_revenue"] == 50.0


def test_missing_optional_rental_fields():
    rentals = [
        {"is_confirmed": True}
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 50.0


def test_telematics_empty_matrix():
    assert check_fleet_telematics([]) == "NO_DATA"


def test_telematics_empty_vehicle_logs():
    assert check_fleet_telematics([[]]) == "SAFE"


def test_telematics_safe_speeds():
    assert check_fleet_telematics([[50, 80, 100]]) == "SAFE"


def test_telematics_single_speeding_event():
    assert check_fleet_telematics([[110]]) == "SAFE"


def test_telematics_speeding_streak_reset():
    assert check_fleet_telematics([[110, 90, 120]]) == "SAFE"


def test_telematics_consecutive_speeding():
    assert check_fleet_telematics([[110, 120]]) == "GROUND_VEHICLE"
