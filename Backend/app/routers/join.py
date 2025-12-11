from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/join", response_class=HTMLResponse)
def join_landing(code: str):
    html = f"""
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Unirte al grupo</title></head>
      <body style="font-family: system-ui, sans-serif; padding: 24px">
        <h2>Unirte al grupo</h2>
        <p>Si tienes la app instalada, <a href="uisgo://join?code={code}">toca aquí para abrirla</a>.</p>
        <p>Si aún no la tienes, instala la app y usa este código:</p>
        <pre style="font-size: 28px; font-weight: 700">{code}</pre>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
