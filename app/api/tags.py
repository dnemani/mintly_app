"""
API endpoints for tag management
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import logging

from app.db_instance import db_manager

router = APIRouter(prefix="/api/tags", tags=["tags"])
logger = logging.getLogger(__name__)


class TagCreate(BaseModel):
    """Request model for adding a tag to a transaction"""
    tag_name: str


class TagResponse(BaseModel):
    """Response model for tag information"""
    id: int
    name: str
    usage_count: int


@router.get("/list")
async def list_all_tags() -> List[TagResponse]:
    """Get all tags with usage counts"""
    try:
        tags = db_manager.get_all_tags()
        return [TagResponse(**tag) for tag in tags]
    except Exception as e:
        logger.error(f"Error listing tags: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tags: {str(e)}")


@router.post("/{transaction_id}/add")
async def add_tag_to_transaction(transaction_id: int, tag_data: TagCreate):
    """Add a tag to a transaction"""
    try:
        db_manager.add_tag_to_transaction(transaction_id, tag_data.tag_name)
        
        return {
            "status": "success",
            "message": f"Added tag '{tag_data.tag_name}' to transaction {transaction_id}"
        }
    except Exception as e:
        logger.error(f"Error adding tag: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding tag: {str(e)}")


@router.delete("/{transaction_id}/remove")
async def remove_tag_from_transaction(transaction_id: int, tag_name: str):
    """Remove a tag from a transaction"""
    try:
        success = db_manager.remove_tag_from_transaction(transaction_id, tag_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found")
        
        return {
            "status": "success",
            "message": f"Removed tag '{tag_name}' from transaction {transaction_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tag: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error removing tag: {str(e)}")


@router.get("/{transaction_id}/list")
async def get_transaction_tags(transaction_id: int) -> List[str]:
    """Get all tags for a specific transaction"""
    try:
        tags = db_manager.get_transaction_tags(transaction_id)
        return tags
    except Exception as e:
        logger.error(f"Error getting transaction tags: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tags: {str(e)}")


@router.get("/filter/{tag_name}")
async def get_transactions_by_tag(tag_name: str):
    """Get all transactions with a specific tag"""
    try:
        df = db_manager.get_transactions_by_tag(tag_name)
        
        if len(df) == 0:
            return []
        
        transactions = df.to_dicts()
        return transactions
    except Exception as e:
        logger.error(f"Error getting transactions by tag: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving transactions: {str(e)}")


@router.get("/sources")
async def get_all_sources():
    """Get all unique transaction sources"""
    try:
        result = db_manager.conn.execute("""
            SELECT DISTINCT source 
            FROM transactions 
            WHERE source IS NOT NULL
            ORDER BY source
        """).fetchall()
        
        sources = [row[0] for row in result]
        return {"sources": sources}
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sources: {str(e)}")


@router.get("/merchants")
async def get_all_merchants():
    """Get all unique merchants"""
    try:
        result = db_manager.conn.execute("""
            SELECT DISTINCT merchant, COUNT(*) as transaction_count
            FROM transactions 
            WHERE merchant IS NOT NULL
            GROUP BY merchant
            ORDER BY transaction_count DESC, merchant
        """).fetchall()
        
        merchants = [{'name': row[0], 'count': row[1]} for row in result]
        return {"merchants": merchants}
    except Exception as e:
        logger.error(f"Error getting merchants: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving merchants: {str(e)}")

