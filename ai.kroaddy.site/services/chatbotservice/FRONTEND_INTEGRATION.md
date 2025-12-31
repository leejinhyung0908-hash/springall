# 챗봇 서비스 프론트엔드 연동 가이드

프론트엔드에서 챗봇 서비스를 연동하기 위한 API 문서입니다.

## 📋 목차

- [서비스 개요](#서비스-개요)
- [API 엔드포인트](#api-엔드포인트)
- [요청/응답 형식](#요청응답-형식)
- [프론트엔드 연동 예시](#프론트엔드-연동-예시)
- [에러 처리](#에러-처리)
- [주의사항](#주의사항)

---

## 서비스 개요

**서비스명**: Chatbot Service  
**포트**: 9004  
**기능**: OpenAI API를 사용한 한국어 챗봇 및 가격 분석 서비스

### 주요 기능
1. **일반 챗봇 대화**: 친절한 한국어 챗봇과 대화
2. **가격 분석**: 상품 가격 분석 및 조언

---

## API 엔드포인트

### Base URL

**개발 환경**:
- 직접 접근: `http://localhost:9004`
- Gateway 경유: `http://localhost:9000/chatbot` ✅ (연결 완료)

**프로덕션 환경**:
- Gateway 경유: `https://api.kroaddy.site/chatbot` (예상)

### 1. 서비스 상태 확인

```http
GET /health
```

**응답 예시**:
```json
{
  "status": "healthy",
  "chatbot_ready": true
}
```

---

### 2. 챗봇 대화

```http
POST /chat
Content-Type: application/json
```

**요청 본문**:
```json
{
  "message": "안녕, 오늘 날씨 어때?",
  "conversation_history": [
    {
      "role": "user",
      "content": "안녕하세요"
    },
    {
      "role": "assistant",
      "content": "안녕하세요! 무엇을 도와드릴까요?"
    }
  ]
}
```

**필드 설명**:
- `message` (필수): 사용자가 입력한 메시지
- `conversation_history` (선택): 이전 대화 이력
  - `role`: `"user"` 또는 `"assistant"`
  - `content`: 메시지 내용

**응답**:
```json
{
  "response": "안녕하세요! 오늘 날씨는 맑고 화창하네요. 외출하기 좋은 날씨예요!"
}
```

**응답 필드**:
- `response`: 챗봇의 응답 메시지

---

### 3. 가격 분석

```http
POST /analyze-price
Content-Type: application/json
```

**요청 본문**:
```json
{
  "product_name": "아이폰 15",
  "price": 1200000,
  "context": "최신 스마트폰, 애플 제품"
}
```

**필드 설명**:
- `product_name` (필수): 상품명
- `price` (선택): 가격 (숫자)
- `context` (선택): 추가 컨텍스트 정보

**응답**:
```json
{
  "analysis": "아이폰 15의 가격 1,200,000원은 시장 가격 대비 적정한 수준입니다. 애플의 최신 스마트폰으로 프리미엄 브랜드 가격대를 고려하면 합리적인 가격이라고 볼 수 있습니다..."
}
```

**응답 필드**:
- `analysis`: 가격 분석 결과

---

## 프론트엔드 연동 예시

### React/TypeScript 예시

```typescript
// api/chatbot.ts
const CHATBOT_API_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:9004';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
}

export interface PriceAnalysisRequest {
  product_name: string;
  price?: number;
  context?: string;
}

export interface PriceAnalysisResponse {
  analysis: string;
}

// 챗봇 대화 API
export async function sendChatMessage(
  message: string,
  conversationHistory?: ChatMessage[]
): Promise<string> {
  try {
    const response = await fetch(`${CHATBOT_API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ChatResponse = await response.json();
    return data.response;
  } catch (error) {
    console.error('챗봇 API 호출 실패:', error);
    throw error;
  }
}

// 가격 분석 API
export async function analyzePrice(
  productName: string,
  price?: number,
  context?: string
): Promise<string> {
  try {
    const response = await fetch(`${CHATBOT_API_URL}/analyze-price`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_name: productName,
        price,
        context,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: PriceAnalysisResponse = await response.json();
    return data.analysis;
  } catch (error) {
    console.error('가격 분석 API 호출 실패:', error);
    throw error;
  }
}
```

### React 컴포넌트 예시

```typescript
// components/Chatbot.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage, ChatMessage } from '@/api/chatbot';

export default function Chatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
    };

    // 사용자 메시지 추가
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 대화 이력을 API 형식으로 변환
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // API 호출
      const response = await sendChatMessage(input, conversationHistory);

      // 챗봇 응답 추가
      const botMessage: ChatMessage = {
        role: 'assistant',
        content: response,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('챗봇 오류:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: '죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
              입력 중...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="메시지를 입력하세요..."
            className="flex-1 border rounded-lg px-4 py-2"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg disabled:opacity-50"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 가격 분석 컴포넌트 예시

```typescript
// components/PriceAnalyzer.tsx
'use client';

import { useState } from 'react';
import { analyzePrice } from '@/api/chatbot';

export default function PriceAnalyzer() {
  const [productName, setProductName] = useState('');
  const [price, setPrice] = useState('');
  const [context, setContext] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!productName.trim()) {
      alert('상품명을 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setAnalysis('');

    try {
      const result = await analyzePrice(
        productName,
        price ? parseFloat(price) : undefined,
        context || undefined
      );
      setAnalysis(result);
    } catch (error) {
      console.error('가격 분석 오류:', error);
      setAnalysis('가격 분석 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">가격 분석</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">상품명 *</label>
          <input
            type="text"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
            placeholder="예: 아이폰 15"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">가격 (선택)</label>
          <input
            type="number"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
            placeholder="예: 1200000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">추가 정보 (선택)</label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
            placeholder="예: 최신 스마트폰, 애플 제품"
            rows={3}
          />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={isLoading}
          className="w-full bg-blue-500 text-white px-6 py-2 rounded-lg disabled:opacity-50"
        >
          {isLoading ? '분석 중...' : '가격 분석하기'}
        </button>

        {analysis && (
          <div className="mt-4 p-4 bg-gray-100 rounded-lg">
            <h3 className="font-bold mb-2">분석 결과</h3>
            <p className="whitespace-pre-wrap">{analysis}</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 에러 처리

### HTTP 상태 코드

- `200 OK`: 성공
- `400 Bad Request`: 잘못된 요청 형식
- `500 Internal Server Error`: 서버 오류

### 에러 응답 형식

```json
{
  "detail": "에러 메시지"
}
```

### 프론트엔드 에러 처리 예시

```typescript
try {
  const response = await fetch(`${CHATBOT_API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '서버 오류가 발생했습니다.');
  }

  const data = await response.json();
  return data.response;
} catch (error) {
  // 네트워크 오류 또는 서버 오류 처리
  if (error instanceof TypeError) {
    // 네트워크 오류
    throw new Error('서버에 연결할 수 없습니다.');
  }
  throw error;
}
```

---

## 주의사항

### 1. API 키 관리
- OpenAI API 키는 백엔드에서만 관리됩니다.
- 프론트엔드에서는 API 키를 직접 사용하지 않습니다.

### 2. CORS 설정
- 현재 개발 환경에서는 모든 origin을 허용합니다.
- 프로덕션 환경에서는 특정 origin만 허용하도록 설정해야 합니다.

### 3. 대화 이력 관리
- 대화 이력을 유지하려면 `conversation_history`를 전달해야 합니다.
- 대화 이력이 길어지면 토큰 사용량이 증가하므로, 최근 N개만 유지하는 것을 권장합니다.

### 4. Rate Limiting
- 현재 Rate Limiting이 설정되어 있지 않습니다.
- 과도한 요청을 방지하기 위해 프론트엔드에서 디바운싱을 구현하는 것을 권장합니다.

### 5. 로딩 상태 표시
- API 호출은 비동기이므로 로딩 상태를 표시하는 것이 좋습니다.

---

## 환경 변수 설정

프론트엔드 `.env.local` 파일:

```env
# 챗봇 서비스 API URL
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:9004

# 또는 Gateway 경유
# NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:9000/chatbot
```

---

## 테스트

### cURL로 테스트

```bash
# 챗봇 대화
curl -X POST "http://localhost:9004/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕, 오늘 날씨 어때?"
  }'

# 가격 분석
curl -X POST "http://localhost:9004/analyze-price" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "아이폰 15",
    "price": 1200000,
    "context": "최신 스마트폰"
  }'
```

---

## 추가 기능 제안

1. **스트리밍 응답**: 실시간으로 응답을 받아 표시
2. **이미지 첨부**: 상품 이미지를 첨부하여 분석
3. **대화 내보내기**: 대화 내용을 파일로 저장
4. **음성 입력**: 음성으로 메시지 입력

---

## 문의

문제가 발생하거나 추가 기능이 필요한 경우, 백엔드 팀에 문의해주세요.

