import torch
from transformers import AutoProcessor, Gemma3ForConditionalGeneration
import json
import random

class MusicChatBot:
    def __init__(self):
        print("Gemma-3-4b-it 모델을 로딩 중...")
        self.model_id = "google/gemma-3-4b-it"
        
        # GPU 사용 가능 여부 확인
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"사용 중인 디바이스: {self.device}")
        
        try:
            # 모델과 프로세서 로드
            self.model = Gemma3ForConditionalGeneration.from_pretrained(
                self.model_id, 
                device_map="auto",
                torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
            ).eval()
            
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            print("모델 로딩 완료!")
            
        except Exception as e:
            print(f"모델 로딩 실패: {e}")
            print("대체 응답 모드로 전환합니다.")
            self.model = None
            self.processor = None
        
        # 대화 기록 저장용
        self.conversation_history = []
        
        # 음악 관련 기본 응답 (모델 로딩 실패시 사용)
        self.fallback_responses = {
            "greeting": ["안녕하세요! 음악에 대해 무엇이든 물어보세요!", "반가워요! 어떤 음악을 좋아하시나요?"],
            "recommendation": ["좀 더 구체적으로 말씀해주시면 더 좋은 추천을 드릴 수 있어요!", "어떤 장르나 아티스트를 좋아하시는지 알려주세요!"],
            "default": ["음악에 대해 더 자세히 설명해주시면 도움을 드릴게요!", "음악 관련 질문이라면 무엇이든 물어보세요!"]
        }

    def get_response(self, user_message):
        """사용자 메시지에 대한 응답 생성"""
        if self.model is None or self.processor is None:
            return self._get_fallback_response(user_message)
        
        try:
            # 음악 전문가 시스템 프롬프트 설정
            system_prompt = """당신은 SOTP (SHOUT OUT TO SPOTIFY) 서비스의 전문 음악 추천 AI입니다. 
다음과 같은 역할을 수행합니다:

1. 사용자의 음악 취향 분석 및 개인화된 추천
2. 아티스트, 앨범, 장르에 대한 전문 정보 제공  
3. 음악 트렌드 및 차트 정보 안내
4. 플레이리스트 구성 조언
5. 친근하고 자연스러운 한국어 대화

항상 음악에 대한 열정과 전문성을 바탕으로 도움이 되는 답변을 제공하세요."""

            # 대화 메시지 구성
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": system_prompt}]
                }
            ]
            
            # 최근 대화 기록 포함 (최대 3개)
            recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
            for msg in recent_history:
                messages.append(msg)
            
            # 현재 사용자 메시지 추가
            messages.append({
                "role": "user", 
                "content": [{"type": "text", "text": user_message}]
            })
            
            # 모델 입력 처리
            inputs = self.processor.apply_chat_template(
                messages, 
                add_generation_prompt=True, 
                tokenize=True,
                return_dict=True, 
                return_tensors="pt"
            ).to(self.model.device)
            
            input_len = inputs["input_ids"].shape[-1]
            
            # 응답 생성
            with torch.inference_mode():
                generation = self.model.generate(
                    **inputs, 
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
                generation = generation[0][input_len:]
            
            # 응답 디코딩
            response = self.processor.decode(generation, skip_special_tokens=True)
            
            # 대화 기록 업데이트
            self._update_conversation_history(user_message, response)
            
            return response.strip()
            
        except Exception as e:
            print(f"모델 응답 생성 중 오류: {e}")
            return self._get_fallback_response(user_message)
    
    def _update_conversation_history(self, user_message, bot_response):
        """대화 기록 업데이트"""
        self.conversation_history.append({
            "role": "user",
            "content": [{"type": "text", "text": user_message}]
        })
        self.conversation_history.append({
            "role": "assistant", 
            "content": [{"type": "text", "text": bot_response}]
        })
        
        # 대화 기록이 너무 길어지면 오래된 것 삭제
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def _get_fallback_response(self, user_message):
        """모델 로딩 실패시 사용할 기본 응답"""
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ["안녕", "hello", "hi", "반가"]):
            return random.choice(self.fallback_responses["greeting"])
        elif any(word in user_message_lower for word in ["추천", "recommend", "좋은", "음악"]):
            return random.choice(self.fallback_responses["recommendation"])
        else:
            return random.choice(self.fallback_responses["default"])
    
    def clear_history(self):
        """대화 기록 초기화"""
        self.conversation_history = []


# 전역 챗봇 인스턴스
music_chatbot = MusicChatBot()

def get_response(msg):
    """Flask 앱에서 호출하는 함수 (기존 인터페이스 유지)"""
    return music_chatbot.get_response(msg)


if __name__ == "__main__":
    print("SOTP 음악 챗봇과 대화를 시작합니다! ('quit'을 입력하면 종료)")
    bot = MusicChatBot()
    
    while True:
        user_input = input("\n사용자: ")
        if user_input.lower() == "quit":
            break
        
        response = bot.get_response(user_input)
        print(f"SOTP 봇: {response}")

