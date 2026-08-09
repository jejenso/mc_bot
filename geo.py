def offset_from_coords(lat: float, lon: float) -> float | None:
    """
    Грубая оценка часового пояса по долготе (без внешних баз часовых поясов).
    Не идеально на границах стран, но для 'показать примерное локальное время' достаточно.
    """
    try:
        offset = round(lon / 15)
        offset = max(-12, min(14, offset))
        return float(offset)
    except Exception:
        return None
