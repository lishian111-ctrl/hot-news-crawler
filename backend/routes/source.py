"""
信源接口路由
提供信源列表、Excel 导入导出等 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from loguru import logger

from database import get_db
from models.source import Source
from services.excel import ExcelService

router = APIRouter(prefix="/source", tags=["信源管理"])


@router.get("/list", summary="获取信源列表")
async def get_source_list(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(default=None, description="分类筛选"),
    board: Optional[str] = Query(default=None, description="板块筛选"),
    keyword: Optional[str] = Query(default=None, description="关键词搜索"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Source).order_by(Source.weight.desc(), Source.created_at.desc())
    if category:
        stmt = stmt.where(Source.category == category)
    if board:
        stmt = stmt.where(Source.board == board)
    if keyword:
        stmt = stmt.where(
            (Source.name.contains(keyword)) | (Source.url.contains(keyword))
        )
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    count_stmt = select(func.count(Source.id))
    if category:
        count_stmt = count_stmt.where(Source.category == category)
    if board:
        count_stmt = count_stmt.where(Source.board == board)
    if keyword:
        count_stmt = count_stmt.where(
            (Source.name.contains(keyword)) | (Source.url.contains(keyword))
        )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    source_data = [source.to_dict() for source in sources]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": source_data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/{source_id}", summary="获取信源详情")
async def get_source_detail(source_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Source).where(Source.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="信源不存在")
    return {"code": 200, "message": "success", "data": source.to_dict()}


@router.post("/import", summary="Excel 导入信源")
async def import_source_excel(
    file: UploadFile = File(..., description="Excel 文件"),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="只支持 Excel (.xlsx) 文件格式")
    
    content = await file.read()
    excel_service = ExcelService()
    result = excel_service.import_sources_from_binary(content)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "解析 Excel 失败"))
    
    data = result.get("data", [])
    if not data:
        raise HTTPException(status_code=400, detail="Excel 文件为空或格式不正确")
    
    imported_count = 0
    error_count = 0
    errors = []
    
    for idx, row in enumerate(data, start=2):
        try:
            if not row.get("name") or not row.get("url"):
                errors.append("第" + str(idx) + "行：缺少必填字段")
                error_count += 1
                continue
            source = Source(
                name=row["name"],
                url=row["url"],
                category=row.get("category", ""),
                weight=row.get("weight", 1),
                board=row.get("board", "")
            )
            db.add(source)
            imported_count += 1
        except Exception as e:
            errors.append("第" + str(idx) + "行：" + str(e))
            error_count += 1
    
    await db.commit()
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "imported_count": imported_count,
            "error_count": error_count,
            "errors": errors[:10]
        }
    }


@router.get("/export", summary="Excel 导出信源")
async def export_source_excel(
    category: Optional[str] = Query(default=None, description="分类筛选"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Source)
    if category:
        stmt = stmt.where(Source.category == category)
    stmt = stmt.order_by(Source.category, Source.weight.desc())
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    if not sources:
        raise HTTPException(status_code=404, detail="没有可导出的数据")
    
    source_data = []
    for source in sources:
        source_data.append({
            "name": source.name,
            "url": source.url,
            "category": source.category,
            "weight": source.weight,
            "board": source.board
        })
    
    excel_service = ExcelService()
    excel_result = excel_service.export_sources_to_bytes(source_data)
    
    if not excel_result.get("success"):
        raise HTTPException(status_code=500, detail=excel_result.get("error", "导出失败"))
    
    excel_bytes = excel_result.get("content", b"")
    filename = "信源列表_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx"
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=" + filename}
    )


@router.get("/categories", summary="获取信源分类列表")
async def get_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(
        Source.category,
        func.count(Source.id).label("count")
    ).group_by(Source.category).order_by(func.count(Source.id).desc())
    result = await db.execute(stmt)
    categories = [
        {"category": row[0] or "未分类", "count": row[1]}
        for row in result.all()
    ]
    return {"code": 200, "message": "success", "data": categories}


@router.delete("/{source_id}", summary="删除信源")
async def delete_source(source_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Source).where(Source.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="信源不存在")
    await db.delete(source)
    await db.commit()
    return {"code": 200, "message": "success", "data": {"deleted_id": source_id}}
