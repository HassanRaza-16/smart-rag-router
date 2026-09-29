from app.core.config import get_settings
from app.services.routing_service import RoutingService


settings = get_settings()

router = RoutingService(
    settings
)


def test_simple_query():

    result = router.classify(
        "What is RAG?"
    )

    assert result == "small"


def test_complex_query():

    result = router.classify(
        "Compare RAG and fine tuning "
        "and analyze their architecture "
        "tradeoffs and implementation."
    )

    assert result == "large"


def test_small_model():

    model = router.select_model(
        "What is machine learning?"
    )

    assert model == settings.small_model


def test_large_model():

    model = router.select_model(
        "Compare RAG and fine tuning "
        "and analyze the tradeoffs."
    )

    assert model == settings.large_model