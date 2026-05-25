from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import re
import uvicorn
import json

app = FastAPI(title="快递单号识别API")

# 快递单号规则库
EXPRESS_RULES = [
    {"code": "SF", "name": "顺丰速运", "pattern": r"^SF\d{12}$"},
    {"code": "EMS", "name": "中国邮政EMS", "pattern": r"^[A-Za-z]{2}\d{9}[A-Za-z]{2}$"},
    {"code": "ZTO", "name": "中通快递", "pattern": r"^\d{12,15}$"},
    {"code": "YTO", "name": "圆通速递", "pattern": r"^YT\d{10,12}$"},
    {"code": "YD", "name": "韵达快递", "pattern": r"^\d{12,13}$"},
    {"code": "STO", "name": "申通快递", "pattern": r"^\d{12,15}$"},
    {"code": "JD", "name": "京东物流", "pattern": r"^JD\d{12,15}$"},
    {"code": "JT", "name": "极兔速递", "pattern": r"^JT\d{12,15}$"},
    {"code": "DE", "name": "德邦快递", "pattern": r"^DPK\d{12}$"},
]

class TrackNumberRequest(BaseModel):
    track_number: str

@app.post("/identify")
async def identify_express(request: TrackNumberRequest):
    track_number = request.track_number.strip()
    
    if not track_number:
        raise HTTPException(status_code=400, detail="快递单号不能为空")
    
    matches = []
    for rule in EXPRESS_RULES:
        if re.match(rule["pattern"], track_number, re.IGNORECASE):
            matches.append({
                "code": rule["code"],
                "name": rule["name"]
            })
    
    if not matches:
        result = {
            "success": False,
            "message": "未识别到快递公司",
            "track_number": track_number
        }
    else:
        result = {
            "success": True,
            "track_number": track_number,
            "result": matches[0] if len(matches) == 1 else matches,
            "is_ambiguous": len(matches) > 1
        }
    
    # 手动设置响应头，确保UTF-8编码，兼容PowerShell
    json_str = json.dumps(result, ensure_ascii=False)
    return Response(content=json_str.encode('utf-8'), media_type="application/json; charset=utf-8")

@app.get("/")
async def root():
    result = {"message": "快递单号识别API已启动", "usage": "POST /identify 传入 {'track_number': '你的单号'}"}
    json_str = json.dumps(result, ensure_ascii=False)
    return Response(content=json_str.encode('utf-8'), media_type="application/json; charset=utf-8")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
