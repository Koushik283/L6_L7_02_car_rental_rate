
import pytest

from car_rental_rate import (
    process_rental_fleet,
    check_fleet_telematics
)


# -----------------------------------------
# PROCESS RENTAL FLEET - BRANCH COVERAGE
# -----------------------------------------

def test_invalid_rentals_list():
    with pytest.raises(ValueError):
        process_rental_fleet(None, 10.0)


def test_negative_admin_fee():
    with pytest.raises(ValueError):
        process_rental_fleet([], -5.0)


def test_empty_rentals_list():
    result = process_rental_fleet([], 10.0)

    assert result["status"] == "EMPTY_BATCH"


def test_unconfirmed_rental_branch():
    rentals = [
        {"is_confirmed": False}
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "EMPTY_BATCH"


def test_confirmed_rental_branch():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 2,
            "trip_segments": []
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "STANDARD"


def test_zero_days_branch():
    rentals = [
        {
            "is_confirmed": True,
            "days": 0
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "EMPTY_BATCH"


def test_positive_days_branch():
    rentals = [
        {
            "is_confirmed": True,
            "days": 2,
            "vehicle_type": "economy",
            "driver_age": 30,
            "trip_segments": []
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "STANDARD"


@pytest.mark.parametrize(
    "vehicle_type, expected_revenue",
    [
        ("luxury", 250.0),
        ("suv", 150.0),
        ("economy", 90.0)
    ]
)
def test_vehicle_type_branches(vehicle_type, expected_revenue):
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


def test_negative_mileage_branch():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [-50]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "STANDARD"


def test_normal_mileage_branch():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 70.0


def test_mileage_above_300_adult_driver():
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


def test_mileage_above_300_young_driver():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 20,
            "days": 1,
            "trip_segments": [350, 100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 320.0


def test_driver_age_below_25():
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


def test_driver_age_25_or_above():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 25,
            "days": 2,
            "trip_segments": []
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 90.0


def test_high_risk_audit_branch():
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


def test_standard_status_branch():
    rentals = [
        {
            "is_confirmed": True,
            "vehicle_type": "economy",
            "driver_age": 30,
            "days": 1,
            "trip_segments": [100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["status"] == "STANDARD"


def test_multiple_rentals_loop():
    rentals = [
        {
            "is_confirmed": False
        },
        {
            "is_confirmed": True,
            "vehicle_type": "suv",
            "driver_age": 30,
            "days": 2,
            "trip_segments": [100]
        }
    ]

    result = process_rental_fleet(rentals, 10.0)

    assert result["total_revenue"] == 170.0


# -----------------------------------------
# CHECK FLEET TELEMATICS - BRANCH COVERAGE
# -----------------------------------------

def test_empty_telematics_matrix():
    assert check_fleet_telematics([]) == "NO_DATA"


def test_empty_vehicle_logs():
    assert check_fleet_telematics([[]]) == "SAFE"


def test_safe_speed_branch():
    assert check_fleet_telematics([[50, 80, 100]]) == "SAFE"


def test_single_speeding_event():
    assert check_fleet_telematics([[110]]) == "SAFE"


def test_speeding_streak_reset_branch():
    assert check_fleet_telematics(
        [[110, 90, 120]]
    ) == "SAFE"


def test_consecutive_speeding_branch():
    assert check_fleet_telematics(
        [[110, 120]]
    ) == "GROUND_VEHICLE"


def test_multiple_vehicle_logs():
    telematics = [
        [50, 80],
        [110, 120]
    ]

    assert check_fleet_telematics(
        telematics
    ) == "GROUND_VEHICLE"
