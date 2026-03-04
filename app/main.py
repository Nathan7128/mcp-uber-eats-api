from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.client import UberEatsAPIError
from app.routers import orders, promotions, stores

app = FastAPI(
    title="Uber Eats API Wrapper",
    version="1.0.0",
    description=(
        "Read-only wrapper for the Uber Eats API. "
        "Exposes endpoints to query stores, orders, and promotions. "
        "All endpoints require a valid Uber Eats API token configured via the UBER_EATS_API_TOKEN environment variable."
    ),
)


@app.exception_handler(UberEatsAPIError)
async def uber_eats_error_handler(request: Request, exc: UberEatsAPIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "metadata": exc.metadata},
    )


app.include_router(stores.router)
app.include_router(orders.router)
app.include_router(promotions.router)
