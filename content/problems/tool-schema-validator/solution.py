TYPES: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _type_name(value: object) -> str:
    return type(value).__name__


def _matches(value: object, expected: str) -> bool:
    # bool subclasses int in Python, so {"top_k": True} sails through a naive
    # isinstance check. Reject it explicitly for the numeric types.
    if expected in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, TYPES[expected])


def validate_args(schema: dict, args: dict) -> list[str]:
    properties: dict = schema.get("properties", {})
    required: list = schema.get("required", [])

    for name, spec in properties.items():
        if spec.get("type") not in TYPES:
            raise ValueError(f"unsupported type {spec.get('type')!r} for property {name!r}")

    errors: list[str] = []

    for name in required:
        if name not in args:
            errors.append(f"missing required property: {name}")

    for name, value in args.items():
        spec = properties.get(name)
        if spec is None:
            errors.append(f"unknown property: {name}")
            continue

        expected = spec["type"]
        if not _matches(value, expected):
            errors.append(f"{name}: expected {expected}, got {_type_name(value)}")
            continue  # a wrong type makes the enum check meaningless

        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{name}: expected one of {spec['enum']!r}, got {value!r}")

    return sorted(errors)


# What the interviewer is checking:
#   - the bool guard on integer/number
#   - every error collected, so one retry can fix everything
#   - `continue` after a type error, so the model is not told two contradictory
#     things about one property
#   - a bad schema raises rather than being reported as a model mistake
