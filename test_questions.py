def is_even(n):
    """Return True if n is even, otherwise False."""
    return n % 2 == 0

def test_is_even():
    assert is_even(4) is True
    assert is_even(5) is False