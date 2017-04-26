from serial.tools.list_ports import comports


def get_serialports():
    result = []
    for p, d, h in comports():
        if not p:
            continue
        result.append({"port": p, "description": d, "hwid": h})
    return result
