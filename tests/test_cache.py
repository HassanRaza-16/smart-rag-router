from app.core.config import get_settings
from app.services.routing_service import RoutingService


def test_cache_threshold():

    settings = get_settings()

    assert 0 < settings.cache_threshold <= 1


def test_router_has_models():

    settings = get_settings()

    router = RoutingService(
        settings
    )

    assert router.settings.small_model
    assert router.settings.large_model