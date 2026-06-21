from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI(title="Banking API Gateway")

SERVICES = {
    "auth": "http://localhost:8001/auth",
    "banking": "http://localhost:8002/banking"
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    if service not in SERVICES:
        return Response(content="Service not found", status_code=404)
    
    url = f"{SERVICES[service]}/{path}"
    async with httpx.AsyncClient() as client:
        req_params = dict(request.query_params)
        req_body = await request.body()
        req_headers = dict(request.headers)
        
        # Remove host header to avoid conflicts
        if "host" in req_headers:
            del req_headers["host"]

        resp = await client.request(
            method=request.method,
            url=url,
            params=req_params,
            content=req_body,
            headers=req_headers
        )
        
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
