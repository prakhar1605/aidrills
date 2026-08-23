Before a support transcript becomes an eval set, or a prompt becomes a log line, the
personal data has to come out. This is a heuristic scrubber — the kind every company
writes once and then relies on far more than they should.

Implement `redact(text, types=None)`. Return `(redacted_text, counts)`.

| type | placeholder | matches |
|---|---|---|
| `email` | `[EMAIL]` | an address |
| `api_key` | `[API_KEY]` | `sk-` followed by 16 or more key characters |
| `credit_card` | `[CREDIT_CARD]` | 13–19 digits, spaces or hyphens allowed, **passing the Luhn check** |
| `ssn` | `[SSN]` | US format, `123-45-6789` |
| `ip` | `[IP]` | an IPv4 address |
| `phone` | `[PHONE]` | `555-123-4567`, `(555) 123-4567`, with an optional country code |

- `types=None` scans for everything. Otherwise scan only the named types.
- `counts` has one entry per **scanned** type, including the ones that found
  nothing.
- Apply the types in the order of the table. A digit run that is a valid card must
  not be re-matched as a phone number.
- An unknown type name raises `ValueError`.

### What the interviewer is checking

The Luhn check. Without it "any 13–19 digit run" redacts order numbers, tracking
IDs and timestamps, and a redactor that mangles ordinary data is one that gets
switched off. Ordering is the other half: overlapping patterns mean the strictest
one has to run first. Expect to be asked where this fails — names and addresses,
which no regex reaches, and that is the honest answer.
