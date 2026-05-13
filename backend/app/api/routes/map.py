"""地图服务API路由"""

import logging

from fastapi import APIRouter, HTTPException, Query

from ...models.schemas import POISearchResponse, RouteRequest, RouteResponse, WeatherResponse
from ...services.amap_service import get_amap_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/map", tags=["地图服务"])


@router.get(
    "/poi",
    response_model=POISearchResponse,
    summary="搜索POI",
    description="根据关键词搜索POI(兴趣点)"
)
async def search_poi(
    keywords: str = Query(..., description="搜索关键词", example="故宫"),
    city: str = Query(..., description="城市", example="北京"),
    citylimit: bool = Query(True, description="是否限制在城市范围内")
):
    """搜索POI"""
    try:
        service = get_amap_service()
        pois = service.search_poi(keywords, city, citylimit)

        return POISearchResponse(
            success=True,
            message="POI搜索成功",
            data=pois,
        )

    except Exception as e:
        logger.exception("POI搜索失败")
        raise HTTPException(
            status_code=500,
            detail=f"POI搜索失败: {str(e)}"
        )


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="查询天气",
    description="查询指定城市的天气信息"
)
async def get_weather(
    city: str = Query(..., description="城市名称", example="北京")
):
    """查询天气"""
    try:
        service = get_amap_service()
        weather_info = service.get_weather(city)

        return WeatherResponse(
            success=True,
            message="天气查询成功",
            data=weather_info,
        )

    except Exception as e:
        logger.exception("天气查询失败")
        raise HTTPException(
            status_code=500,
            detail=f"天气查询失败: {str(e)}"
        )


@router.post(
    "/route",
    response_model=RouteResponse,
    summary="规划路线",
    description="规划两点之间的路线"
)
async def plan_route(request: RouteRequest):
    """规划路线"""
    try:
        service = get_amap_service()
        route_info = service.plan_route(
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type,
        )

        return RouteResponse(
            success=route_info is not None,
            message="路线规划成功" if route_info is not None else "未获取到路线规划结果",
            data=route_info,
        )

    except Exception as e:
        logger.exception("路线规划失败")
        raise HTTPException(
            status_code=500,
            detail=f"路线规划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查地图服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        service = get_amap_service()
        available_tools = getattr(service.mcp_tool, "_available_tools", []) or []

        return {
            "status": "healthy",
            "service": "map-service",
            "mcp_tools_count": len(available_tools),
        }
    except Exception as e:
        logger.exception("地图服务健康检查失败")
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )
