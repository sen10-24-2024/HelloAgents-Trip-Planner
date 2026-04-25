"""澶氭櫤鑳戒綋鏃呰瑙勫垝绯荤粺"""

import json
import logging
from typing import Dict, Any, List
from hello_agents import SimpleAgent
from hello_agents.tools import MCPTool
from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings

logger = logging.getLogger(__name__)

# ============ Agent鎻愮ず璇?============

ATTRACTION_AGENT_PROMPT = """浣犳槸鏅偣鎼滅储涓撳銆備綘鐨勪换鍔℃槸鏍规嵁鍩庡競鍜岀敤鎴峰亸濂芥悳绱㈠悎閫傜殑鏅偣銆?

**閲嶈鎻愮ず:**
浣犲繀椤讳娇鐢ㄥ伐鍏锋潵鎼滅储鏅偣!涓嶈鑷繁缂栭€犳櫙鐐逛俊鎭?

**宸ュ叿璋冪敤鏍煎紡:**
浣跨敤maps_text_search宸ュ叿鏃?蹇呴』涓ユ牸鎸夌収浠ヤ笅鏍煎紡:
`[TOOL_CALL:amap_maps_text_search:keywords=鏅偣鍏抽敭璇?city=鍩庡競鍚峕`

**绀轰緥:**
鐢ㄦ埛: "鎼滅储鍖椾含鐨勫巻鍙叉枃鍖栨櫙鐐?
浣犵殑鍥炲: [TOOL_CALL:amap_maps_text_search:keywords=鍘嗗彶鏂囧寲,city=鍖椾含]

鐢ㄦ埛: "鎼滅储涓婃捣鐨勫叕鍥?
浣犵殑鍥炲: [TOOL_CALL:amap_maps_text_search:keywords=鍏洯,city=涓婃捣]

**娉ㄦ剰:**
1. 蹇呴』浣跨敤宸ュ叿,涓嶈鐩存帴鍥炵瓟
2. 鏍煎紡蹇呴』瀹屽叏姝ｇ‘,鍖呮嫭鏂规嫭鍙峰拰鍐掑彿
3. 鍙傛暟鐢ㄩ€楀彿鍒嗛殧
"""

WEATHER_AGENT_PROMPT = """浣犳槸澶╂皵鏌ヨ涓撳銆備綘鐨勪换鍔℃槸鏌ヨ鎸囧畾鍩庡競鐨勫ぉ姘斾俊鎭€?

**閲嶈鎻愮ず:**
浣犲繀椤讳娇鐢ㄥ伐鍏锋潵鏌ヨ澶╂皵!涓嶈鑷繁缂栭€犲ぉ姘斾俊鎭?

**宸ュ叿璋冪敤鏍煎紡:**
浣跨敤maps_weather宸ュ叿鏃?蹇呴』涓ユ牸鎸夌収浠ヤ笅鏍煎紡:
`[TOOL_CALL:amap_maps_weather:city=鍩庡競鍚峕`

**绀轰緥:**
鐢ㄦ埛: "鏌ヨ鍖椾含澶╂皵"
浣犵殑鍥炲: [TOOL_CALL:amap_maps_weather:city=鍖椾含]

鐢ㄦ埛: "涓婃捣鐨勫ぉ姘旀€庝箞鏍?
浣犵殑鍥炲: [TOOL_CALL:amap_maps_weather:city=涓婃捣]

**娉ㄦ剰:**
1. 蹇呴』浣跨敤宸ュ叿,涓嶈鐩存帴鍥炵瓟
2. 鏍煎紡蹇呴』瀹屽叏姝ｇ‘,鍖呮嫭鏂规嫭鍙峰拰鍐掑彿
"""

HOTEL_AGENT_PROMPT = """浣犳槸閰掑簵鎺ㄨ崘涓撳銆備綘鐨勪换鍔℃槸鏍规嵁鍩庡競鍜屾櫙鐐逛綅缃帹鑽愬悎閫傜殑閰掑簵銆?

**閲嶈鎻愮ず:**
浣犲繀椤讳娇鐢ㄥ伐鍏锋潵鎼滅储閰掑簵!涓嶈鑷繁缂栭€犻厭搴椾俊鎭?

**宸ュ叿璋冪敤鏍煎紡:**
浣跨敤maps_text_search宸ュ叿鎼滅储閰掑簵鏃?蹇呴』涓ユ牸鎸夌収浠ヤ笅鏍煎紡:
`[TOOL_CALL:amap_maps_text_search:keywords=閰掑簵,city=鍩庡競鍚峕`

**绀轰緥:**
鐢ㄦ埛: "鎼滅储鍖椾含鐨勯厭搴?
浣犵殑鍥炲: [TOOL_CALL:amap_maps_text_search:keywords=閰掑簵,city=鍖椾含]

**娉ㄦ剰:**
1. 蹇呴』浣跨敤宸ュ叿,涓嶈鐩存帴鍥炵瓟
2. 鏍煎紡蹇呴』瀹屽叏姝ｇ‘,鍖呮嫭鏂规嫭鍙峰拰鍐掑彿
3. 鍏抽敭璇嶄娇鐢?閰掑簵"鎴?瀹鹃"
"""

PLANNER_AGENT_PROMPT = """浣犳槸琛岀▼瑙勫垝涓撳銆備綘鐨勪换鍔℃槸鏍规嵁鏅偣淇℃伅鍜屽ぉ姘斾俊鎭?鐢熸垚璇︾粏鐨勬梾琛岃鍒掋€?

璇蜂弗鏍兼寜鐓т互涓婮SON鏍煎紡杩斿洖鏃呰璁″垝:
```json
{
  "city": "鍩庡競鍚嶇О",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "绗?澶╄绋嬫杩?,
      "transportation": "浜ら€氭柟寮?,
      "accommodation": "浣忓绫诲瀷",
      "hotel": {
        "name": "閰掑簵鍚嶇О",
        "address": "閰掑簵鍦板潃",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500鍏?,
        "rating": "4.5",
        "distance": "璺濈鏅偣2鍏噷",
        "type": "缁忔祹鍨嬮厭搴?,
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "鏅偣鍚嶇О",
          "address": "璇︾粏鍦板潃",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "鏅偣璇︾粏鎻忚堪",
          "category": "鏅偣绫诲埆",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "鏃╅鎺ㄨ崘", "description": "鏃╅鎻忚堪", "estimated_cost": 30},
        {"type": "lunch", "name": "鍗堥鎺ㄨ崘", "description": "鍗堥鎻忚堪", "estimated_cost": 50},
        {"type": "dinner", "name": "鏅氶鎺ㄨ崘", "description": "鏅氶鎻忚堪", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "鏅?,
      "night_weather": "澶氫簯",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "鍗楅",
      "wind_power": "1-3绾?
    }
  ],
  "overall_suggestions": "鎬讳綋寤鸿",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

**閲嶈鎻愮ず:**
1. weather_info鏁扮粍蹇呴』鍖呭惈姣忎竴澶╃殑澶╂皵淇℃伅
2. 娓╁害蹇呴』鏄函鏁板瓧(涓嶈甯β癈绛夊崟浣?
3. 姣忓ぉ瀹夋帓2-3涓櫙鐐?
4. 鑰冭檻鏅偣涔嬮棿鐨勮窛绂诲拰娓歌鏃堕棿
5. 姣忓ぉ蹇呴』鍖呭惈鏃╀腑鏅氫笁椁?
6. 鎻愪緵瀹炵敤鐨勬梾琛屽缓璁?
7. **蹇呴』鍖呭惈棰勭畻淇℃伅**:
   - 鏅偣闂ㄧエ浠锋牸(ticket_price)
   - 椁愰ギ棰勪及璐圭敤(estimated_cost)
   - 閰掑簵棰勪及璐圭敤(estimated_cost)
   - 棰勭畻姹囨€?budget)鍖呭惈鍚勯」鎬昏垂鐢?
"""


class MultiAgentTripPlanner:
    """澶氭櫤鑳戒綋鏃呰瑙勫垝绯荤粺"""

    def __init__(self):
        """鍒濆鍖栧鏅鸿兘浣撶郴缁?""
        print("馃攧 寮€濮嬪垵濮嬪寲澶氭櫤鑳戒綋鏃呰瑙勫垝绯荤粺...")

        try:
            settings = get_settings()
            self.llm = get_llm()

            # 鍒涘缓鍏变韩鐨凪CP宸ュ叿(鍙垱寤轰竴娆?
            print("  - 鍒涘缓鍏变韩MCP宸ュ叿...")
            self.amap_tool = MCPTool(
                name="amap",
                description="楂樺痉鍦板浘鏈嶅姟",
                server_command=["uvx", "amap-mcp-server"],
                env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
                auto_expand=True
            )

            # 鍒涘缓鏅偣鎼滅储Agent
            print("  - 鍒涘缓鏅偣鎼滅储Agent...")
            self.attraction_agent = SimpleAgent(
                name="鏅偣鎼滅储涓撳",
                llm=self.llm,
                system_prompt=ATTRACTION_AGENT_PROMPT
            )
            self.attraction_agent.add_tool(self.amap_tool)

            # 鍒涘缓澶╂皵鏌ヨAgent
            print("  - 鍒涘缓澶╂皵鏌ヨAgent...")
            self.weather_agent = SimpleAgent(
                name="澶╂皵鏌ヨ涓撳",
                llm=self.llm,
                system_prompt=WEATHER_AGENT_PROMPT
            )
            self.weather_agent.add_tool(self.amap_tool)

            # 鍒涘缓閰掑簵鎺ㄨ崘Agent
            print("  - 鍒涘缓閰掑簵鎺ㄨ崘Agent...")
            self.hotel_agent = SimpleAgent(
                name="閰掑簵鎺ㄨ崘涓撳",
                llm=self.llm,
                system_prompt=HOTEL_AGENT_PROMPT
            )
            self.hotel_agent.add_tool(self.amap_tool)

            # 鍒涘缓琛岀▼瑙勫垝Agent(涓嶉渶瑕佸伐鍏?
            print("  - 鍒涘缓琛岀▼瑙勫垝Agent...")
            self.planner_agent = SimpleAgent(
                name="琛岀▼瑙勫垝涓撳",
                llm=self.llm,
                system_prompt=PLANNER_AGENT_PROMPT
            )

            print(f"鉁?澶氭櫤鑳戒綋绯荤粺鍒濆鍖栨垚鍔?)
            print(f"   鏅偣鎼滅储Agent: {len(self.attraction_agent.list_tools())} 涓伐鍏?)
            print(f"   澶╂皵鏌ヨAgent: {len(self.weather_agent.list_tools())} 涓伐鍏?)
            print(f"   閰掑簵鎺ㄨ崘Agent: {len(self.hotel_agent.list_tools())} 涓伐鍏?)

        except Exception as e:
            print(f"鉂?澶氭櫤鑳戒綋绯荤粺鍒濆鍖栧け璐? {str(e)}")
            logger.exception("Failed to initialize multi-agent trip planner")
            raise
    
    def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        浣跨敤澶氭櫤鑳戒綋鍗忎綔鐢熸垚鏃呰璁″垝

        Args:
            request: 鏃呰璇锋眰

        Returns:
            鏃呰璁″垝
        """
        try:
            print(f"\n{'='*60}")
            print(f"馃殌 寮€濮嬪鏅鸿兘浣撳崗浣滆鍒掓梾琛?..")
            print(f"鐩殑鍦? {request.city}")
            print(f"鏃ユ湡: {request.start_date} 鑷?{request.end_date}")
            print(f"澶╂暟: {request.travel_days}澶?)
            print(f"鍋忓ソ: {', '.join(request.preferences) if request.preferences else '鏃?}")
            print(f"{'='*60}\n")

            # 姝ラ1: 鏅偣鎼滅储Agent鎼滅储鏅偣
            print("馃搷 姝ラ1: 鎼滅储鏅偣...")
            attraction_query = self._build_attraction_query(request)
            attraction_response = self.attraction_agent.run(attraction_query)
            print(f"鏅偣鎼滅储缁撴灉: {attraction_response[:200]}...\n")

            # 姝ラ2: 澶╂皵鏌ヨAgent鏌ヨ澶╂皵
            print("馃尋锔? 姝ラ2: 鏌ヨ澶╂皵...")
            weather_query = f"璇锋煡璇request.city}鐨勫ぉ姘斾俊鎭?
            weather_response = self.weather_agent.run(weather_query)
            print(f"澶╂皵鏌ヨ缁撴灉: {weather_response[:200]}...\n")

            # 姝ラ3: 閰掑簵鎺ㄨ崘Agent鎼滅储閰掑簵
            print("馃彣 姝ラ3: 鎼滅储閰掑簵...")
            hotel_query = f"璇锋悳绱request.city}鐨剓request.accommodation}閰掑簵"
            hotel_response = self.hotel_agent.run(hotel_query)
            print(f"閰掑簵鎼滅储缁撴灉: {hotel_response[:200]}...\n")

            # 姝ラ4: 琛岀▼瑙勫垝Agent鏁村悎淇℃伅鐢熸垚璁″垝
            print("馃搵 姝ラ4: 鐢熸垚琛岀▼璁″垝...")
            planner_query = self._build_planner_query(request, attraction_response, weather_response, hotel_response)
            planner_response = self.planner_agent.run(planner_query)
            print(f"琛岀▼瑙勫垝缁撴灉: {planner_response[:300]}...\n")

            # 瑙ｆ瀽鏈€缁堣鍒?
            trip_plan = self._parse_response(planner_response, request)

            print(f"{'='*60}")
            print(f"鉁?鏃呰璁″垝鐢熸垚瀹屾垚!")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            print(f"鉂?鐢熸垚鏃呰璁″垝澶辫触: {str(e)}")
            logger.exception("Failed to generate trip plan")
            return self._create_fallback_plan(request)
    
    def _build_attraction_query(self, request: TripRequest) -> str:
        """鏋勫缓鏅偣鎼滅储鏌ヨ - 鐩存帴鍖呭惈宸ュ叿璋冪敤"""
        keywords = []
        if request.preferences:
            # 鍙彇绗竴涓亸濂戒綔涓哄叧閿瘝
            keywords = request.preferences[0]
        else:
            keywords = "鏅偣"

        # 鐩存帴杩斿洖宸ュ叿璋冪敤鏍煎紡
        query = f"璇蜂娇鐢╝map_maps_text_search宸ュ叿鎼滅储{request.city}鐨剓keywords}鐩稿叧鏅偣銆俓n[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        return query

    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "") -> str:
        """鏋勫缓琛岀▼瑙勫垝鏌ヨ"""
        query = f"""璇锋牴鎹互涓嬩俊鎭敓鎴恵request.city}鐨剓request.travel_days}澶╂梾琛岃鍒?

**鍩烘湰淇℃伅:**
- 鍩庡競: {request.city}
- 鏃ユ湡: {request.start_date} 鑷?{request.end_date}
- 澶╂暟: {request.travel_days}澶?
- 浜ら€氭柟寮? {request.transportation}
- 浣忓: {request.accommodation}
- 鍋忓ソ: {', '.join(request.preferences) if request.preferences else '鏃?}

**鏅偣淇℃伅:**
{attractions}

**澶╂皵淇℃伅:**
{weather}

**閰掑簵淇℃伅:**
{hotels}

**瑕佹眰:**
1. 姣忓ぉ瀹夋帓2-3涓櫙鐐?
2. 姣忓ぉ蹇呴』鍖呭惈鏃╀腑鏅氫笁椁?
3. 姣忓ぉ鎺ㄨ崘涓€涓叿浣撶殑閰掑簵(浠庨厭搴椾俊鎭腑閫夋嫨)
3. 鑰冭檻鏅偣涔嬮棿鐨勮窛绂诲拰浜ら€氭柟寮?
4. 杩斿洖瀹屾暣鐨凧SON鏍煎紡鏁版嵁
5. 鏅偣鐨勭粡绾害鍧愭爣瑕佺湡瀹炲噯纭?
"""
        if request.free_text_input:
            query += f"\n**棰濆瑕佹眰:** {request.free_text_input}"

        return query
    
    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """
        瑙ｆ瀽Agent鍝嶅簲
        
        Args:
            response: Agent鍝嶅簲鏂囨湰
            request: 鍘熷璇锋眰
            
        Returns:
            鏃呰璁″垝
        """
        try:
            # 灏濊瘯浠庡搷搴斾腑鎻愬彇JSON
            # 鏌ユ壘JSON浠ｇ爜鍧?
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                # 鐩存帴鏌ユ壘JSON瀵硅薄
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("鍝嶅簲涓湭鎵惧埌JSON鏁版嵁")
            
            # 瑙ｆ瀽JSON
            data = json.loads(json_str)
            
            # 杞崲涓篢ripPlan瀵硅薄
            trip_plan = TripPlan(**data)
            
            return trip_plan
            
        except Exception as e:
            print(f"鈿狅笍  瑙ｆ瀽鍝嶅簲澶辫触: {str(e)}")
            print(f"   灏嗕娇鐢ㄥ鐢ㄦ柟妗堢敓鎴愯鍒?)
            return self._create_fallback_plan(request)
    
    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """鍒涘缓澶囩敤璁″垝(褰揂gent澶辫触鏃?"""
        from datetime import datetime, timedelta
        
        # 瑙ｆ瀽鏃ユ湡
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        
        # 鍒涘缓姣忔棩琛岀▼
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)
            
            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"绗瑊i+1}澶╄绋?,
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}鏅偣{j+1}",
                        address=f"{request.city}甯?,
                        location=Location(longitude=116.4 + i*0.01 + j*0.005, latitude=39.9 + i*0.01 + j*0.005),
                        visit_duration=120,
                        description=f"杩欐槸{request.city}鐨勮憲鍚嶆櫙鐐?,
                        category="鏅偣"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"绗瑊i+1}澶╂棭椁?, description="褰撳湴鐗硅壊鏃╅"),
                    Meal(type="lunch", name=f"绗瑊i+1}澶╁崍椁?, description="鍗堥鎺ㄨ崘"),
                    Meal(type="dinner", name=f"绗瑊i+1}澶╂櫄椁?, description="鏅氶鎺ㄨ崘")
                ]
            )
            days.append(day_plan)
        
        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"杩欐槸涓烘偍瑙勫垝鐨剓request.city}{request.travel_days}鏃ユ父琛岀▼,寤鸿鎻愬墠鏌ョ湅鍚勬櫙鐐圭殑寮€鏀炬椂闂淬€?
        )


# 鍏ㄥ眬澶氭櫤鑳戒綋绯荤粺瀹炰緥
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """鑾峰彇澶氭櫤鑳戒綋鏃呰瑙勫垝绯荤粺瀹炰緥(鍗曚緥妯″紡)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner

