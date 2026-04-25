"""鏃呰瑙勫垝API璺敱"""

import logging
from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trip", tags=["鏃呰瑙勫垝"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="鐢熸垚鏃呰璁″垝",
    description="鏍规嵁鐢ㄦ埛杈撳叆鐨勬梾琛岄渶姹?鐢熸垚璇︾粏鐨勬梾琛岃鍒?
)
async def plan_trip(request: TripRequest):
    """
    鐢熸垚鏃呰璁″垝

    Args:
        request: 鏃呰璇锋眰鍙傛暟

    Returns:
        鏃呰璁″垝鍝嶅簲
    """
    try:
        print(f"\n{'='*60}")
        print(f"馃摜 鏀跺埌鏃呰瑙勫垝璇锋眰:")
        print(f"   鍩庡競: {request.city}")
        print(f"   鏃ユ湡: {request.start_date} - {request.end_date}")
        print(f"   澶╂暟: {request.travel_days}")
        print(f"{'='*60}\n")

        # 鑾峰彇Agent瀹炰緥
        print("馃攧 鑾峰彇澶氭櫤鑳戒綋绯荤粺瀹炰緥...")
        agent = get_trip_planner_agent()

        # 鐢熸垚鏃呰璁″垝
        print("馃殌 寮€濮嬬敓鎴愭梾琛岃鍒?..")
        trip_plan = agent.plan_trip(request)

        print("鉁?鏃呰璁″垝鐢熸垚鎴愬姛,鍑嗗杩斿洖鍝嶅簲\n")

        return TripPlanResponse(
            success=True,
            message="鏃呰璁″垝鐢熸垚鎴愬姛",
            data=trip_plan
        )

    except Exception as e:
        print(f"鉂?鐢熸垚鏃呰璁″垝澶辫触: {str(e)}")
        logger.exception("Failed to handle /trip/plan request")
        raise HTTPException(
            status_code=500,
            detail=f"鐢熸垚鏃呰璁″垝澶辫触: {str(e)}"
        )


@router.get(
    "/health",
    summary="鍋ュ悍妫€鏌?,
    description="妫€鏌ユ梾琛岃鍒掓湇鍔℃槸鍚︽甯?
)
async def health_check():
    """鍋ュ悍妫€鏌?""
    try:
        # 妫€鏌gent鏄惁鍙敤
        agent = get_trip_planner_agent()
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.agent.name,
            "tools_count": len(agent.agent.list_tools())
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"鏈嶅姟涓嶅彲鐢? {str(e)}"
        )

