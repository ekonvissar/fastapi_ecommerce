import importlib

ROUTER_MODULES = (
    "app.identity.api.router",
    "app.catalog.api.categories_router",
    "app.catalog.api.products_router",
    "app.catalog.api.reviews_router",
    "app.ordering.api.router",
    "app.ordering.api.cart_router",
    "app.notifications.api.ws_router",
    "app.shared.api.health_router",
)


def include_routers(app) -> None:
    for module_path in ROUTER_MODULES:
        module = importlib.import_module(module_path)
        app.include_router(module.router)
