from fastapi import FastAPI

from src.items.routes import item_router
from src.userauth.routes import auth_router
from src.notes.routes import notes_router
from src.tags.routes import tags_router
from src.errors import register_error_handlers
from src.middleware import register_middleware


version = "v1"

app = FastAPI(
    version=version,
    title="Warehouse Management API",
    description="API to manage items in warehouse",
    docs_url=f"/api/{version}/docs"
)

register_error_handlers(app)
register_middleware(app)

app.include_router(item_router, prefix=f"/api/{version}/items", tags=["Items"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])
app.include_router(notes_router, prefix=f"/api/{version}/notes", tags=["Notes"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["Tags"])


