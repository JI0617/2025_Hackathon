from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
import uuid
from .models import ChatSession, ChatMessage
from .chatbot_logic import ChatbotLogic

def chat_view(request):
    """챗봇 채팅 페이지"""
    return render(request, 'chatbot/chat.html')

@csrf_exempt
def chat_api(request):
    """챗봇 API 엔드포인트"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': '메시지가 비어있습니다.'}, status=400)
            
            # 세션 처리
            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id, is_active=True)
                except ChatSession.DoesNotExist:
                    session = None
            else:
                session = None
            
            # 새 세션 생성
            if not session:
                session = ChatSession.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_id=str(uuid.uuid4()),
                    is_active=True
                )
            
            # 사용자 메시지 저장
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=message
            )
            
            # 챗봇 응답 생성
            chatbot = ChatbotLogic()
            bot_response = chatbot.process_message(message, request.user)
            
            # 봇 응답 저장
            bot_message = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=bot_response
            )
            
            return JsonResponse({
                'response': bot_response,
                'session_id': session.session_id,
                'timestamp': bot_message.timestamp.isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'서버 오류가 발생했습니다: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)

@login_required
def chat_history(request):
    """채팅 기록 조회"""
    sessions = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
    return render(request, 'chatbot/history.html', {'sessions': sessions})

@login_required
def chat_session_detail(request, session_id):
    """특정 채팅 세션 상세 보기"""
    try:
        session = ChatSession.objects.get(session_id=session_id, user=request.user)
        messages = session.messages.all().order_by('timestamp')
        return render(request, 'chatbot/session_detail.html', {
            'session': session,
            'messages': messages
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': '채팅 세션을 찾을 수 없습니다.'}, status=404)
