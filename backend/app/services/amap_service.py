"""高德地图MCP服务封装"""

import json
import re
from typing import Any, Dict, List, Optional

from hello_agents.tools import MCPTool

from ..config import get_settings
from ..models.schemas import Location, POIInfo, RouteInfo, WeatherInfo

_amap_mcp_tool = None


def get_amap_mcp_tool() -> MCPTool:
    """获取高德地图MCP工具实例(单例模式)"""
    global _amap_mcp_tool

    if _amap_mcp_tool is None:
        settings = get_settings()

        if not settings.amap_api_key:
            raise ValueError("高德地图API Key未配置,请在.env文件中设置AMAP_API_KEY")

        _amap_mcp_tool = MCPTool(
            name="amap",
            description="高德地图服务,支持POI搜索、路线规划、天气查询等功能",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
            auto_expand=True,
        )

        print("✅ 高德地图MCP工具初始化成功")
        available_tools = getattr(_amap_mcp_tool, "_available_tools", []) or []
        print(f"   工具数量: {len(available_tools)}")

        if available_tools:
            print("   可用工具:")
            for tool in available_tools[:5]:
                print(f"     - {tool.get('name', 'unknown')}")
            if len(available_tools) > 5:
                print(f"     ... 还有 {len(available_tools) - 5} 个工具")

    return _amap_mcp_tool


class AmapService:
    """高德地图服务封装类"""

    def __init__(self):
        self.mcp_tool = get_amap_mcp_tool()

    def _extract_json_payload(self, result: Any) -> Any:
        if isinstance(result, (dict, list)):
            return result

        text = str(result or "").strip()
        if not text:
            return {}

        fenced_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if fenced_match:
            candidate = fenced_match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        for pattern in (r"(\{.*\})", r"(\[.*\])"):
            match = re.search(pattern, text, re.DOTALL)
            if match:
                candidate = match.group(1).strip()
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}

    def _unwrap_payload(self, payload: Any) -> Any:
        current = payload
        for key in ("data", "result", "output"):
            if isinstance(current, dict) and key in current and current[key] not in (None, ""):
                current = current[key]
        return current

    def _to_float(self, value: Any, default: float = 0.0) -> float:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip().replace(",", "")
        if not text:
            return default
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return default
        return float(match.group(0))

    def _to_int(self, value: Any, default: int = 0) -> int:
        return int(round(self._to_float(value, float(default))))

    def _parse_location(self, value: Any) -> Optional[Location]:
        if isinstance(value, Location):
            return value

        if isinstance(value, dict):
            longitude = value.get("longitude", value.get("lng", value.get("lon")))
            latitude = value.get("latitude", value.get("lat"))
            if longitude is not None and latitude is not None:
                return Location(
                    longitude=self._to_float(longitude),
                    latitude=self._to_float(latitude),
                )

        if isinstance(value, str) and "," in value:
            parts = [part.strip() for part in value.split(",", 1)]
            if len(parts) == 2:
                return Location(
                    longitude=self._to_float(parts[0]),
                    latitude=self._to_float(parts[1]),
                )

        return None

    def _first_list(self, *candidates: Any) -> List[Any]:
        for candidate in candidates:
            if isinstance(candidate, list):
                return candidate
        return []

    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        try:
            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": "maps_text_search",
                    "arguments": {
                        "keywords": keywords,
                        "city": city,
                        "citylimit": str(citylimit).lower(),
                    },
                }
            )

            print(f"POI搜索结果: {str(result)[:200]}...")

            payload = self._unwrap_payload(self._extract_json_payload(result))
            poi_candidates = self._first_list(
                payload.get("pois") if isinstance(payload, dict) else None,
                payload.get("results") if isinstance(payload, dict) else None,
                payload if isinstance(payload, list) else None,
            )

            pois: List[POIInfo] = []
            for item in poi_candidates:
                if not isinstance(item, dict):
                    continue
                location = self._parse_location(item.get("location"))
                if location is None:
                    continue
                pois.append(
                    POIInfo(
                        id=str(item.get("id") or item.get("poi_id") or item.get("name") or ""),
                        name=str(item.get("name") or "未知地点"),
                        type=str(item.get("type") or item.get("category") or ""),
                        address=str(item.get("address") or item.get("pname") or city),
                        location=location,
                        tel=item.get("tel"),
                    )
                )

            return pois

        except Exception as e:
            print(f"❌ POI搜索失败: {str(e)}")
            return []

    def get_weather(self, city: str) -> List[WeatherInfo]:
        try:
            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": "maps_weather",
                    "arguments": {"city": city},
                }
            )

            print(f"天气查询结果: {str(result)[:200]}...")

            payload = self._unwrap_payload(self._extract_json_payload(result))
            forecasts = self._first_list(
                payload.get("forecasts") if isinstance(payload, dict) else None,
                payload if isinstance(payload, list) else None,
            )

            weather_list: List[WeatherInfo] = []
            for forecast in forecasts:
                if isinstance(forecast, dict) and isinstance(forecast.get("casts"), list):
                    for cast in forecast["casts"]:
                        if not isinstance(cast, dict):
                            continue
                        weather_list.append(
                            WeatherInfo(
                                date=str(cast.get("date") or ""),
                                day_weather=str(cast.get("dayweather") or cast.get("weather") or cast.get("day_weather") or ""),
                                night_weather=str(cast.get("nightweather") or cast.get("night_weather") or cast.get("dayweather") or cast.get("weather") or ""),
                                day_temp=self._to_int(cast.get("daytemp", cast.get("temperature", cast.get("day_temp", 0)))),
                                night_temp=self._to_int(cast.get("nighttemp", cast.get("night_temp", cast.get("temperature", 0)))),
                                wind_direction=str(cast.get("daywind") or cast.get("winddirection") or cast.get("wind_direction") or ""),
                                wind_power=str(cast.get("daypower") or cast.get("windpower") or cast.get("wind_power") or ""),
                            )
                        )
                elif isinstance(forecast, dict):
                    report_date = str(forecast.get("reporttime") or forecast.get("date") or "")
                    weather_list.append(
                        WeatherInfo(
                            date=report_date.split(" ")[0] if report_date else "",
                            day_weather=str(forecast.get("weather") or forecast.get("dayweather") or forecast.get("day_weather") or ""),
                            night_weather=str(forecast.get("nightweather") or forecast.get("night_weather") or forecast.get("weather") or ""),
                            day_temp=self._to_int(forecast.get("temperature", forecast.get("daytemp", forecast.get("day_temp", 0)))),
                            night_temp=self._to_int(forecast.get("nighttemp", forecast.get("night_temp", forecast.get("temperature", 0)))),
                            wind_direction=str(forecast.get("winddirection") or forecast.get("daywind") or forecast.get("wind_direction") or ""),
                            wind_power=str(forecast.get("windpower") or forecast.get("daypower") or forecast.get("wind_power") or ""),
                        )
                    )

            return weather_list

        except Exception as e:
            print(f"❌ 天气查询失败: {str(e)}")
            return []

    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking",
    ) -> Optional[RouteInfo]:
        try:
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address",
            }

            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")
            arguments: Dict[str, Any] = {
                "origin_address": origin_address,
                "destination_address": destination_address,
            }

            if origin_city:
                arguments["origin_city"] = origin_city
            if destination_city:
                arguments["destination_city"] = destination_city

            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": tool_name,
                    "arguments": arguments,
                }
            )

            print(f"路线规划结果: {str(result)[:200]}...")

            payload = self._unwrap_payload(self._extract_json_payload(result))
            route = payload.get("route") if isinstance(payload, dict) else None
            route = route if isinstance(route, dict) else payload if isinstance(payload, dict) else {}

            path = None
            if isinstance(route, dict):
                paths = route.get("paths")
                transits = route.get("transits")
                if isinstance(paths, list) and paths:
                    path = paths[0]
                elif isinstance(transits, list) and transits:
                    path = transits[0]

            if not isinstance(path, dict):
                return None

            description = str(
                path.get("strategy")
                or path.get("instruction")
                or path.get("cost")
                or f"{route_type}路线规划"
            )

            return RouteInfo(
                distance=self._to_float(path.get("distance", 0)),
                duration=self._to_int(path.get("duration", 0)),
                route_type=route_type,
                description=description,
            )

        except Exception as e:
            print(f"❌ 路线规划失败: {str(e)}")
            return None

    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        try:
            arguments = {"address": address}
            if city:
                arguments["city"] = city

            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": "maps_geo",
                    "arguments": arguments,
                }
            )

            print(f"地理编码结果: {str(result)[:200]}...")

            payload = self._unwrap_payload(self._extract_json_payload(result))
            geocodes = self._first_list(
                payload.get("geocodes") if isinstance(payload, dict) else None,
                payload if isinstance(payload, list) else None,
            )
            if geocodes and isinstance(geocodes[0], dict):
                return self._parse_location(geocodes[0].get("location"))

            if isinstance(payload, dict):
                return self._parse_location(payload.get("location"))

            return None

        except Exception as e:
            print(f"❌ 地理编码失败: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        try:
            result = self.mcp_tool.run(
                {
                    "action": "call_tool",
                    "tool_name": "maps_search_detail",
                    "arguments": {"id": poi_id},
                }
            )

            print(f"POI详情结果: {str(result)[:200]}...")

            payload = self._unwrap_payload(self._extract_json_payload(result))
            if isinstance(payload, dict):
                return payload
            return {"raw": str(result)}

        except Exception as e:
            print(f"❌ 获取POI详情失败: {str(e)}")
            return {}


_amap_service = None


def get_amap_service() -> AmapService:
    """获取高德地图服务实例(单例模式)"""
    global _amap_service

    if _amap_service is None:
        _amap_service = AmapService()

    return _amap_service
