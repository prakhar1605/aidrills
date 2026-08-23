from submission import *


def test_luhn_accepts_a_valid_card():
    assert luhn("4242424242424242") is True, "the standard test card must pass"


def test_luhn_rejects_a_bad_checksum():
    assert luhn("4242424242424241") is False, "a wrong check digit must fail"


def test_luhn_rejects_non_digits():
    assert luhn("4242-4242") is False, "non-digits must fail rather than raise"


def test_email():
    out, counts = redact("reach me at ada@example.com please")
    assert out == "reach me at [EMAIL] please", f"got {out!r}"
    assert counts["email"] == 1, f"expected 1, got {counts['email']!r}"


def test_email_with_plus_and_dots():
    out, _ = redact("ada.lovelace+work@sub.example.co.uk")
    assert out == "[EMAIL]", f"got {out!r}"


def test_api_key():
    out, counts = redact("use sk-abc123def456ghi789jkl for this")
    assert "[API_KEY]" in out, f"got {out!r}"
    assert counts["api_key"] == 1, f"expected 1, got {counts['api_key']!r}"


def test_short_sk_string_is_not_a_key():
    out, counts = redact("sk-short")
    assert out == "sk-short", f"expected it untouched, got {out!r}"
    assert counts["api_key"] == 0, f"expected 0, got {counts['api_key']!r}"


def test_credit_card_with_spaces():
    out, counts = redact("card 4242 4242 4242 4242 on file")
    assert out == "card [CREDIT_CARD] on file", f"got {out!r}"
    assert counts["credit_card"] == 1, f"expected 1, got {counts['credit_card']!r}"


def test_credit_card_without_separators():
    out, _ = redact("4242424242424242")
    assert out == "[CREDIT_CARD]", f"got {out!r}"


def test_digits_that_fail_luhn_survive():
    out, counts = redact("order 4242424242424241 shipped")
    assert "4242424242424241" in out, f"a non-card digit run must survive, got {out!r}"
    assert counts["credit_card"] == 0, f"expected 0, got {counts['credit_card']!r}"


def test_ssn():
    out, counts = redact("ssn 123-45-6789 on record")
    assert out == "ssn [SSN] on record", f"got {out!r}"
    assert counts["ssn"] == 1, f"expected 1, got {counts['ssn']!r}"


def test_ip():
    out, counts = redact("connect to 192.168.1.1 first")
    assert out == "connect to [IP] first", f"got {out!r}"
    assert counts["ip"] == 1, f"expected 1, got {counts['ip']!r}"


def test_phone_with_hyphens():
    out, counts = redact("call 555-123-4567 today")
    assert out == "call [PHONE] today", f"got {out!r}"
    assert counts["phone"] == 1, f"expected 1, got {counts['phone']!r}"


def test_phone_with_parentheses_and_country_code():
    out, _ = redact("call +1 (555) 123-4567 today")
    assert "[PHONE]" in out, f"got {out!r}"
    assert "555" not in out, f"the number must be fully replaced, got {out!r}"


def test_a_card_is_not_reported_as_a_phone():
    _, counts = redact("4242 4242 4242 4242")
    assert counts["credit_card"] == 1, f"expected 1 card, got {counts!r}"
    assert counts["phone"] == 0, f"the card must not also count as a phone, got {counts!r}"


def test_multiple_of_one_type():
    _, counts = redact("a@x.com and b@y.com and c@z.com")
    assert counts["email"] == 3, f"expected 3, got {counts['email']!r}"


def test_mixed_types():
    text = "ada@example.com called from 555-123-4567 about ssn 123-45-6789"
    out, counts = redact(text)
    for placeholder in ("[EMAIL]", "[PHONE]", "[SSN]"):
        assert placeholder in out, f"expected {placeholder} in {out!r}"
    assert counts["email"] == 1 and counts["phone"] == 1 and counts["ssn"] == 1, f"got {counts!r}"


def test_clean_text_is_unchanged():
    text = "There is nothing sensitive in this sentence."
    out, counts = redact(text)
    assert out == text, f"expected the text unchanged, got {out!r}"
    assert set(counts.values()) == {0}, f"expected all zeros, got {counts!r}"


def test_counts_cover_every_scanned_type():
    _, counts = redact("nothing here")
    assert set(counts) == {"email", "api_key", "credit_card", "ssn", "ip", "phone"}, (
        f"every scanned type needs a count: got {sorted(counts)!r}"
    )


def test_selecting_types_limits_the_scan():
    text = "ada@example.com and 555-123-4567"
    out, counts = redact(text, types=["email"])
    assert "[EMAIL]" in out, f"got {out!r}"
    assert "555-123-4567" in out, f"phone must not be scanned, got {out!r}"
    assert set(counts) == {"email"}, f"expected only the email count, got {sorted(counts)!r}"


def test_unknown_type_raises():
    try:
        redact("text", types=["passport"])
    except ValueError:
        return
    raise AssertionError("an unknown type must raise ValueError")


def test_empty_text():
    out, counts = redact("")
    assert out == "", f"expected '', got {out!r}"
    assert set(counts.values()) == {0}, f"expected all zeros, got {counts!r}"
