def print_if(message: str = "", end: str = "\n", condition: bool = True) -> None:
    print(message, end=end) if condition else None


def format_message(message: str, format_map: dict) -> str:
    for key, value in format_map.items():
        message = message.replace(key, str(value))
    return message


def retrieve_key(
    target: dict,
    key: str,
    expected: type,
    required: bool = True,
    fallback=None,
    extra: str = "",
    expected_message: str = "key f:key is type f:type, but expected f:extype",
    required_message: str = "key f:key is required",
):
    # Formats all formattable words into their representated.
    message_formatting_map = {
        "f:key": key,
        "f:extype": expected,
        "f:type": None,  # this is manipulated later
        "f:extra": extra,
    }

    try:
        retrieved = target[key]

    except KeyError:
        if required:
            raise KeyError(format_message(required_message, message_formatting_map))
        else:
            return fallback

    else:
        if isinstance(retrieved, expected) is False:
            message_formatting_map["f:type"] = str(type(retrieved))
            raise TypeError(format_message(expected_message, message_formatting_map))

        return retrieved
