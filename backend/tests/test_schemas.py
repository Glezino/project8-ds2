from app.schemas.health import HealthResponse


def test_health_response_round_trip() -> None:
    response = HealthResponse(status="ok")
    payload = response.model_dump()
    assert payload == {"status": "ok"}

    reparsed = HealthResponse.model_validate(payload)
    assert reparsed == response
