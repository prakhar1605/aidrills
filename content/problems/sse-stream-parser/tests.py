from submission import *


def test_two_events_in_one_chunk():
    out = list(parse_sse(['data: {"i": 0}\n\ndata: {"i": 1}\n\n']))
    exp = [{"i": 0}, {"i": 1}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_event_split_across_chunks():
    out = list(parse_sse(['data: {"i', '": 0}\n', '\n']))
    exp = [{"i": 0}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_one_character_at_a_time():
    stream = 'data: {"a": 1}\n\ndata: {"b": 2}\n\n'
    out = list(parse_sse(iter(stream)))
    exp = [{"a": 1}, {"b": 2}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_done_terminates_the_stream():
    out = list(parse_sse(['data: {"i": 0}\n\ndata: [DONE]\n\ndata: {"i": 9}\n\n']))
    exp = [{"i": 0}]
    assert out == exp, f"[DONE] must stop the stream: expected {exp!r}, got {out!r}"


def test_comments_are_ignored():
    out = list(parse_sse([': keep-alive\n\ndata: {"i": 0}\n\n']))
    exp = [{"i": 0}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_non_data_fields_are_ignored():
    out = list(parse_sse(['event: message\nid: 42\ndata: {"i": 0}\nretry: 100\n\n']))
    exp = [{"i": 0}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_multiline_data_is_joined():
    out = list(parse_sse(['data: {"a":\ndata:  1}\n\n']))
    exp = [{"a": 1}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_only_one_space_is_stripped():
    out = list(parse_sse(['data: "  padded"\n\n']))
    exp = ["  padded"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_value_containing_a_colon():
    out = list(parse_sse(['data: {"url": "https://example.com/x"}\n\n']))
    exp = [{"url": "https://example.com/x"}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_crlf_line_endings():
    out = list(parse_sse(['data: {"i": 0}\r\n\r\ndata: {"i": 1}\r\n\r\n']))
    exp = [{"i": 0}, {"i": 1}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_crlf_split_between_chunks():
    out = list(parse_sse(['data: {"i": 0}\r', '\n\r', '\n']))
    exp = [{"i": 0}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_trailing_event_without_blank_line():
    out = list(parse_sse(['data: {"i": 0}']))
    exp = [{"i": 0}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_malformed_frame_is_skipped():
    out = list(parse_sse(['data: not json\n\ndata: {"i": 1}\n\n']))
    exp = [{"i": 1}]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_empty_stream():
    out = list(parse_sse([]))
    assert out == [], f"expected [], got {out!r}"


def test_is_lazy():
    pulled = []

    def source():
        for chunk in ['data: {"i": 0}\n\n', 'data: {"i": 1}\n\n']:
            pulled.append(chunk)
            yield chunk

    stream = parse_sse(source())
    first = next(stream)
    assert first == {"i": 0}, f"expected the first event, got {first!r}"
    assert len(pulled) == 1, f"expected 1 chunk pulled before the first yield, got {len(pulled)}"
