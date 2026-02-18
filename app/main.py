from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import customer, import_data, scoring
from app.services import llm_service

BASE_DIR = Path(__file__).parent.parent  # project root

app = FastAPI(title="架電レコメンドツール")

app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")

app.include_router(customer.router, prefix="/api")
app.include_router(scoring.router, prefix="/api")
app.include_router(llm_service.router, prefix="/api")
app.include_router(import_data.router, prefix="/api")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/import")
def import_page(request: Request):
    return templates.TemplateResponse("import.html", {"request": request})


@app.get("/customers/{customer_id}")
def customer_detail_page(request: Request, customer_id: int):
    return templates.TemplateResponse(
        "customer_detail.html",
        {"request": request, "customer_id": customer_id}
    )


@app.on_event("startup")
def startup_event():
    from app.database import Base, engine
    import time
    import os
    import app.models.customer  # noqa: F401
    import app.models.call_record  # noqa: F401
    import app.models.ocr_card  # noqa: F401
    # wait for DB to become available (useful when DB container still initializing)
    max_wait = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
    start = time.time()
    while True:
        try:
            with engine.connect() as conn:
                break
        except Exception as e:
            if time.time() - start > max_wait:
                raise
            print("Waiting for DB to be ready...", str(e))
            time.sleep(2)

    Base.metadata.create_all(bind=engine)

    from data_import.seed import seed
    seed()

    print("架電レコメンドツール起動完了")
