import re
import random
from django.db.models import Q
# from regions.models import Region
from users.models import UserPreference

# class ChatbotLogic:
#     """챗봇 로직 클래스"""
    
#     def __init__(self):
#         self.greetings = ['안녕', 'hello', 'hi', '안녕하세요', '반가워', '하이', '헬로']
#         self.farewells = ['잘가', 'bye', '안녕히가세요', '그만', '종료', '끝', '나갈게']
        
#         # 키워드 매핑
#         self.traffic_keywords = ['교통', '버스', '지하철', '교통편', '대중교통', '이동', '접근성']
#         self.education_keywords = ['교육', '학교', '대학', '학원', '유치원', '초등학교', '중학교', '고등학교']
#         self.cost_keywords = ['생활비', '비용', '돈', '가격', '월세', '전세', '임대료', '렌트']
#         self.medical_keywords = ['의료', '병원', '의사', '약국', '건강', '치료', '진료']
#         self.comparison_keywords = ['비교', 'vs', '대비', '차이', '어떤게', '어느게']
#         self.weather_keywords = ['날씨', '기후', '온도', '비', '눈', '바람']
        
#     def process_message(self, message, user=None):
#         """사용자 메시지를 처리하고 응답을 생성"""
#         original_message = message
#         message = message.lower().strip()
        
#         # 인사말 처리
#         if any(greeting in message for greeting in self.greetings):
#             return self._handle_greeting(user)
        
#         # 작별인사 처리
#         if any(farewell in message for farewell in self.farewells):
#             return self._handle_farewell()
        
#         # 도움말
#         if any(keyword in message for keyword in ['도움', 'help', '도움말', '무엇', '뭐', '어떤']):
#             return self._handle_help()
        
#         # 비교 관련 질문
#         if any(keyword in message for keyword in self.comparison_keywords):
#             return self._handle_comparison_request(original_message)
        
#         # 지역 추천 요청 처리
#         if any(keyword in message for keyword in ['추천', '추천해', '추천해줘', '어디', '지역', '살면', '이사']):
#             return self._handle_recommendation_request(message, user)
        
#         # 지역 정보 요청 처리
#         if any(keyword in message for keyword in ['정보', '알려줘', '어떤', '특징', '소개']):
#             return self._handle_region_info_request(original_message)
        
#         # 교통 관련 질문
#         if any(keyword in message for keyword in self.traffic_keywords):
#             return self._handle_traffic_question(message)
        
#         # 교육 관련 질문
#         if any(keyword in message for keyword in self.education_keywords):
#             return self._handle_education_question(message)
        
#         # 생활비 관련 질문
#         if any(keyword in message for keyword in self.cost_keywords):
#             return self._handle_cost_question(message)
        
#         # 의료 관련 질문
#         if any(keyword in message for keyword in self.medical_keywords):
#             return self._handle_medical_question(message)
        
#         # 날씨 관련 질문
#         if any(keyword in message for keyword in self.weather_keywords):
#             return self._handle_weather_question(message)
        
#         # 지역명이 포함된 경우
#         region_info = self._extract_region_from_message(original_message)
#         if region_info:
#             return self._handle_specific_region_question(region_info, message)
        
#         # 기본 응답
#         return self._handle_default_response()
    
#     def _handle_greeting(self, user):
#         """인사말 처리"""
#         if user and user.is_authenticated:
#             return f"안녕하세요 {user.username}님! 지역 추천 챗봇입니다. 어떤 도움이 필요하신가요?"
#         else:
#             return "안녕하세요! 지역 추천 챗봇입니다. 어떤 도움이 필요하신가요?"
    
#     def _handle_farewell(self):
#         """작별인사 처리"""
#         return "안녕히 가세요! 또 궁금한 것이 있으시면 언제든 말씀해주세요."
    
#     def _handle_recommendation_request(self, message, user):
#         """추천 요청 처리"""
#         try:
#             if user and user.is_authenticated:
#                 # 사용자 선호도 기반 추천
#                 try:
#                     preference = user.userpreference
#                     regions = Region.objects.all()
                    
#                     # 선호도 기반 점수 계산
#                     scored_regions = []
#                     for region in regions:
#                         score = 0
#                         score += region.traffic_score * preference.traffic_importance
#                         score += region.education_score * preference.education_importance
                        
#                         # 비용 선호도 반영
#                         cost_score = 0
#                         if preference.preferred_cost_level == region.cost_level:
#                             cost_score = 100
#                         elif preference.preferred_cost_level == '낮음' and region.cost_level in ['매우낮음', '낮음']:
#                             cost_score = 80
#                         elif preference.preferred_cost_level == '보통' and region.cost_level == '보통':
#                             cost_score = 100
#                         elif preference.preferred_cost_level == '높음' and region.cost_level in ['높음', '매우높음']:
#                             cost_score = 80
                        
#                         score += cost_score * preference.cost_importance
#                         scored_regions.append((region, score))
                    
#                     # 점수순 정렬
#                     scored_regions.sort(key=lambda x: x[1], reverse=True)
#                     recommended_regions = [region for region, score in scored_regions[:3]]
                    
#                     response = "당신의 선호도에 맞는 지역을 추천해드릴게요:\n\n"
#                     for i, region in enumerate(recommended_regions, 1):
#                         response += f"{i}. {region.name}\n"
#                         response += f"   - 교통: {region.traffic_score}점\n"
#                         response += f"   - 교육: {region.education_score}점\n"
#                         response += f"   - 생활비: {region.cost_level}\n\n"
                    
#                     response += "더 자세한 정보를 원하시면 지역명을 말씀해주세요!"
#                     return response
                    
#                 except UserPreference.DoesNotExist:
#                     return "선호도를 먼저 설정해주세요! 선호도 설정 후 맞춤 추천을 받을 수 있습니다."
#             else:
#                 # 비로그인 사용자에게 인기 지역 추천
#                 popular_regions = Region.objects.all()[:3]
#                 response = "인기 지역을 추천해드릴게요:\n\n"
#                 for i, region in enumerate(popular_regions, 1):
#                     response += f"{i}. {region.name}\n"
#                     response += f"   - 교통: {region.traffic_score}점\n"
#                     response += f"   - 교육: {region.education_score}점\n"
#                     response += f"   - 생활비: {region.cost_level}\n\n"
                
#                 response += "더 자세한 정보를 원하시면 지역명을 말씀해주세요!"
#                 return response
                
#         except Exception as e:
#             return "죄송합니다. 추천 시스템에 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    
#     def _handle_region_info_request(self, message):
#         """지역 정보 요청 처리"""
#         # 지역명 추출
#         regions = Region.objects.all()
#         for region in regions:
#             if region.name in message:
#                 response = f"{region.name} 지역 정보입니다:\n\n"
#                 response += f"📍 위치: {region.name}\n"
#                 response += f"🚌 교통: {region.traffic_score}점\n"
#                 response += f"🎓 교육: {region.education_score}점\n"
#                 response += f"💰 생활비: {region.cost_level}\n"
#                 if region.population:
#                     response += f"👥 인구: {region.population:,.0f}명\n"
#                 if region.area:
#                     response += f"📏 면적: {region.area}km²\n"
#                 if region.description:
#                     response += f"\n📝 설명: {region.description}\n"
                
#                 response += f"\n더 자세한 정보는 '{region.name}' 상세 페이지를 확인해보세요!"
#                 return response
        
#         return "어떤 지역에 대해 알고 싶으신가요? 지역명을 말씀해주세요."
    
#     def _handle_traffic_question(self, message):
#         """교통 관련 질문 처리"""
#         # 교통이 좋은 지역 추천
#         good_traffic_regions = Region.objects.filter(traffic_score__gte=8).order_by('-traffic_score')[:3]
        
#         response = "교통이 좋은 지역들을 알려드릴게요:\n\n"
#         for i, region in enumerate(good_traffic_regions, 1):
#             response += f"{i}. {region.name} (교통점수: {region.traffic_score}점)\n"
        
#         response += "\n교통 점수는 지하철, 버스, 도로 상황 등을 종합적으로 평가한 것입니다."
#         return response
    
#     def _handle_education_question(self, message):
#         """교육 관련 질문 처리"""
#         # 교육이 좋은 지역 추천
#         good_education_regions = Region.objects.filter(education_score__gte=8).order_by('-education_score')[:3]
        
#         response = "교육 환경이 좋은 지역들을 알려드릴게요:\n\n"
#         for i, region in enumerate(good_education_regions, 1):
#             response += f"{i}. {region.name} (교육점수: {region.education_score}점)\n"
        
#         response += "\n교육 점수는 학교 수, 교육 시설, 학원 등을 종합적으로 평가한 것입니다."
#         return response
    
#     def _handle_cost_question(self, message):
#         """생활비 관련 질문 처리"""
#         # 생활비가 낮은 지역 추천
#         low_cost_regions = Region.objects.filter(cost_level__in=['매우낮음', '낮음'])[:3]
        
#         response = "생활비가 낮은 지역들을 알려드릴게요:\n\n"
#         for i, region in enumerate(low_cost_regions, 1):
#             response += f"{i}. {region.name} (생활비: {region.cost_level})\n"
        
#         response += "\n생활비는 주택, 식비, 교통비 등을 종합적으로 고려한 것입니다."
#         return response
    
#     def _handle_help(self):
#         """도움말"""
#         response = "저는 지역 추천 챗봇입니다! 다음과 같은 도움을 드릴 수 있어요:\n\n"
#         response += "🔍 지역 추천: '추천해줘', '어디 살면 좋을까?'\n"
#         response += "📊 지역 정보: '서울 정보 알려줘', '강남구 특징'\n"
#         response += "🚌 교통 정보: '교통 좋은 곳', '교통편'\n"
#         response += "🎓 교육 정보: '교육 좋은 곳', '학교'\n"
#         response += "💰 생활비 정보: '생활비 낮은 곳', '비용'\n"
#         response += "❓ 도움말: '도움말', 'help'\n\n"
#         response += "무엇이든 편하게 물어보세요!"
#         return response
    
#     def _extract_region_from_message(self, message):
#         """메시지에서 지역명 추출"""
#         regions = Region.objects.all()
#         for region in regions:
#             if region.name in message or region.city in message:
#                 return region
#         return None
    
#     def _handle_specific_region_question(self, region, message):
#         """특정 지역에 대한 질문 처리"""
#         response = f"📍 {region.name}에 대해 질문해주셨네요!\n\n"
        
#         # 교통 관련 질문인지 확인
#         if any(keyword in message for keyword in self.traffic_keywords):
#             response += f"🚌 교통: {region.traffic_score}점\n"
#             if region.traffic_score >= 8:
#                 response += "교통이 매우 좋은 지역입니다!\n"
#             elif region.traffic_score >= 6:
#                 response += "교통이 양호한 지역입니다.\n"
#             else:
#                 response += "교통이 다소 불편할 수 있습니다.\n"
        
#         # 교육 관련 질문인지 확인
#         if any(keyword in message for keyword in self.education_keywords):
#             response += f"🎓 교육: {region.education_score}점\n"
#             if region.education_score >= 8:
#                 response += "교육 환경이 매우 좋은 지역입니다!\n"
#             elif region.education_score >= 6:
#                 response += "교육 환경이 양호한 지역입니다.\n"
#             else:
#                 response += "교육 시설이 다소 부족할 수 있습니다.\n"
        
#         # 생활비 관련 질문인지 확인
#         if any(keyword in message for keyword in self.cost_keywords):
#             response += f"💰 생활비: {region.cost_level}\n"
#             cost_descriptions = {
#                 '매우낮음': '매우 저렴한 생활비',
#                 '낮음': '저렴한 생활비',
#                 '보통': '보통 수준의 생활비',
#                 '높음': '비싼 생활비',
#                 '매우높음': '매우 비싼 생활비'
#             }
#             response += f"{cost_descriptions.get(region.cost_level, '정보 없음')}입니다.\n"
        
#         # 의료 관련 질문인지 확인
#         if any(keyword in message for keyword in self.medical_keywords):
#             response += f"🏥 의료: {region.medical_score}점\n"
#             if region.medical_score >= 8:
#                 response += "의료 시설이 매우 잘 갖춰진 지역입니다!\n"
#             elif region.medical_score >= 6:
#                 response += "의료 시설이 양호한 지역입니다.\n"
#             else:
#                 response += "의료 시설이 다소 부족할 수 있습니다.\n"
        
#         # 일반적인 정보
#         if not any(keyword in message for keyword in self.traffic_keywords + self.education_keywords + self.cost_keywords + self.medical_keywords):
#             response += f"📊 종합 정보:\n"
#             response += f"🚌 교통: {region.traffic_score}점\n"
#             response += f"🎓 교육: {region.education_score}점\n"
#             response += f"🏥 의료: {region.medical_score}점\n"
#             response += f"💰 생활비: {region.cost_level}\n"
        
#         if region.description:
#             response += f"\n📝 지역 설명: {region.description}\n"
        
#         response += f"\n더 자세한 정보는 '{region.name}' 상세 페이지를 확인해보세요!"
#         return response
    
#     def _handle_comparison_request(self, message):
#         """비교 요청 처리"""
#         # 메시지에서 지역명들 추출
#         regions = Region.objects.all()
#         mentioned_regions = []
        
#         for region in regions:
#             if region.name in message or region.city in message:
#                 mentioned_regions.append(region)
        
#         if len(mentioned_regions) < 2:
#             return "비교하고 싶은 지역들을 말씀해주세요! 예: '서울과 부산 비교해줘'"
        
#         # 최대 3개 지역까지만 비교
#         mentioned_regions = mentioned_regions[:3]
        
#         response = f"📍 {', '.join([r.name for r in mentioned_regions])} 지역 비교입니다:\n\n"
        
#         for region in mentioned_regions:
#             response += f"🏙️ {region.name}\n"
#             response += f"   🚌 교통: {region.traffic_score}점\n"
#             response += f"   🎓 교육: {region.education_score}점\n"
#             response += f"   🏥 의료: {region.medical_score}점\n"
#             response += f"   💰 생활비: {region.cost_level}\n\n"
        
#         # 추천 지역
#         best_region = max(mentioned_regions, key=lambda r: r.traffic_score + r.education_score + r.medical_score)
#         response += f"⭐ 종합적으로 {best_region.name}이 가장 추천됩니다!"
        
#         return response
    
#     def _handle_medical_question(self, message):
#         """의료 관련 질문 처리"""
#         # 의료가 좋은 지역 추천
#         good_medical_regions = Region.objects.filter(medical_score__gte=8).order_by('-medical_score')[:3]
        
#         response = "🏥 의료 시설이 좋은 지역들을 알려드릴게요:\n\n"
#         for i, region in enumerate(good_medical_regions, 1):
#             response += f"{i}. {region.name} (의료점수: {region.medical_score}점)\n"
        
#         response += "\n의료 점수는 병원, 약국, 의료진 등을 종합적으로 평가한 것입니다."
#         return response
    
#     def _handle_weather_question(self, message):
#         """날씨 관련 질문 처리"""
#         responses = [
#             "죄송합니다. 현재 날씨 정보는 제공하지 않습니다. 지역별 기후 정보는 각 지역 상세 페이지에서 확인하실 수 있어요!",
#             "날씨 정보는 실시간으로 변하므로 정확한 정보를 제공하기 어렵습니다. 대신 지역별 교통, 교육, 생활비 정보를 도와드릴 수 있어요!",
#             "기상청이나 날씨 앱에서 정확한 날씨 정보를 확인하시는 것을 추천드려요. 저는 지역 생활 정보를 도와드릴게요!"
#         ]
#         return random.choice(responses)
    
#     def _handle_default_response(self):
#         """기본 응답"""
#         responses = [
#             "죄송합니다. 잘 이해하지 못했어요. '도움말'을 입력하시면 제가 할 수 있는 일을 알려드릴게요!",
#             "무엇을 도와드릴까요? 지역 추천, 정보 조회 등 다양한 서비스를 제공합니다.",
#             "지역에 대해 궁금한 것이 있으시면 언제든 말씀해주세요!",
#             "구체적으로 어떤 지역이나 주제에 대해 알고 싶으신가요?",
#         ]
#         return random.choice(responses) 