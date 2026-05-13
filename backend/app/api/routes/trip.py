"""旅行规划API路由"""

import logging

from fastapi import APIRouter, HTTPException

from ...agents.trip_planner_agent import get_trip_planner_agent
from ...models.schemas import TripPlanResponse, TripRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    生成旅行计划

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print("📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        print("🚀 开始生成旅行计划...")
        result = agent.plan_trip(request)

        if result["success"]:
            print("✅ 旅行计划生成成功,准备返回响应\n")
        else:
            print(f"⚠️  旅行计划生成未完成,返回备用计划: {result['message']}\n")

        return TripPlanResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"],
        )

    except Exception as e:
        logger.exception("生成旅行计划失败")
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        agent = get_trip_planner_agent()

        return {
            "status": "healthy",
            "service": "trip-planner",
            "agents": {
                "attraction": {
                    "name": agent.attraction_agent.name,
                    "tools_count": len(agent.attraction_agent.list_tools())
                },
                "weather": {
                    "name": agent.weather_agent.name,
                    "tools_count": len(agent.weather_agent.list_tools())
                },
                "hotel": {
                    "name": agent.hotel_agent.name,
                    "tools_count": len(agent.hotel_agent.list_tools())
                },
                "planner": {
                    "name": agent.planner_agent.name,
                    "tools_count": len(agent.planner_agent.list_tools())
                }
            }
        }
    except Exception as e:
        logger.exception("旅行规划服务健康检查失败")
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )