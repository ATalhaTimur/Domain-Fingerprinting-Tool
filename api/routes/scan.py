from fastapi import APIRouter, Request

from application.dto.scan_request import ScanRequestDTO

router = APIRouter(prefix="/api/v1")


@router.post("/scan")
async def scan(body: ScanRequestDTO, request: Request):
    use_case = request.app.state.scan_use_case
    result = await use_case.execute(body)
    return result.to_dict()


@router.get("/health")
async def health():
    return {"status": "ok"}
