from app import calculate_discount


def test_ten_percent_discount():
    assert calculate_discount(100) == 90
