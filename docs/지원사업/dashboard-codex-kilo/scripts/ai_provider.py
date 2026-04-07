#!/usr/bin/env python3
"""
AI Provider Interface
4단계 분석 모드 + Fallback 체인 지원
표준 라이브러리만 사용
"""

import json
import re
import ssl
import urllib.request
import urllib.error
from typing import Dict, Optional, Any, List

# settings 모듈에서 설정 로드
import settings


# 재시도할 에러 코드
RETRYABLE_ERRORS = {429, 503, 504}
RETRYABLE_EXCEPTIONS = (urllib.error.URLError, TimeoutError)


def analyze_notice(notice: Dict[str, Any], mode: str = "quick") -> Dict[str, Any]:
    """
    공고 분석 실행 - 4단계 모드 + Fallback 체인
    
    Args:
        notice: 공고 정보 딕셔너리
        mode: "quick", "medium", "deep", 또는 "glm"
        
    Returns:
        분석 결과 딕셔너리:
        {
            'success': bool,
            'mode': str,
            'provider': str,
            'model': str,           # 최종 사용된 모델
            'fallback_used': bool,  # fallback이 사용되었는지
            'fit_score': float | None,
            'summary': str | None,
            'strengths': str | None,
            'risks': str | None,
            'next_actions': str | None,
            'error': str | None
        }
    """
    mode = mode.lower()
    
    # 지원되는 모드인지 확인
    valid_modes = settings.get_all_modes()
    if mode not in valid_modes:
        return {
            'success': False,
            'mode': mode,
            'provider': None,
            'model': None,
            'fallback_used': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'error': f'Invalid mode: {mode}. Supported modes: {valid_modes}'
        }
    
    # mode별 설정 로드
    config = settings.get_ai_mode_config(mode)
    primary_provider = config.get('provider', 'groq')
    primary_model = config.get('model', '')
    api_key = config.get('api_key')
    fallbacks: List[str] = config.get('fallbacks', [])
    
    if not api_key:
        return {
            'success': False,
            'mode': mode,
            'provider': primary_provider,
            'model': primary_model,
            'fallback_used': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'error': f'{primary_provider.upper()}_API_KEY not configured'
        }
    
    if not primary_model:
        return {
            'success': False,
            'mode': mode,
            'provider': primary_provider,
            'model': None,
            'fallback_used': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'error': f'AI_{mode.upper()}_MODEL not configured'
        }
    
    # 1차 모델 시도
    result = _analyze_with_provider(
        notice, 
        provider=primary_provider, 
        model=primary_model, 
        api_key=api_key,
        mode=mode
    )
    
    # 성공하면 반환
    if result.get('success'):
        result['mode'] = mode
        result['fallback_used'] = False
        return result
    
    # 실패 시 fallback 시도
    original_error = result.get('error', '')
    
    for fallback_model in fallbacks:
        print(f"[ai_provider] Primary failed ({original_error}), trying fallback: {fallback_model}", flush=True)
        
        result = _analyze_with_provider(
            notice,
            provider=primary_provider,  # 같은 provider 사용
            model=fallback_model,
            api_key=api_key,
            mode=mode
        )
        
        if result.get('success'):
            result['mode'] = mode
            result['fallback_used'] = True
            result['original_error'] = original_error  # 어떤 에러에서allback했는지
            return result
    
    # 모두 실패
    result['mode'] = mode
    result['fallback_used'] = False
    return result


def _analyze_with_provider(notice: Dict[str, Any], provider: str, model: str, api_key: str, mode: str) -> Dict[str, Any]:
    """provider에 따라 분석 실행"""
    if provider == 'groq':
        return _analyze_with_groq(notice, model=model, mode=mode, api_key=api_key)
    elif provider == 'nvidia':
        return _analyze_with_nvidia(notice, model=model, mode=mode, api_key=api_key)
    elif provider == 'modal':
        return _analyze_with_modal(notice, model=model, mode=mode, api_key=api_key)
    else:
        return {
            'success': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'model': model,
            'provider': provider,
            'mode': mode,
            'error': f'Unknown provider: {provider}'
        }


def _make_request(url: str, data: Dict, api_key: str, timeout: int = 60) -> Dict:
    """OpenAI 호환 API 요청 실행 (http.client 사용)"""
    import http.client
    import ssl
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path
    
    ctx = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection(host, 443, context=ctx)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    body = json.dumps(data)
    
    try:
        conn.request('POST', path, body, headers)
        response = conn.getresponse()
        
        if response.status != 200:
            raise urllib.error.HTTPError(
                url, response.status, response.reason,
                response.getheaders(), response
            )
        
        return json.loads(response.read().decode('utf-8'))
    finally:
        conn.close()


def _analyze_with_groq(notice: Dict[str, Any], model: str, mode: str, api_key: str) -> Dict[str, Any]:
    """Groq API로 분석"""
    if not api_key:
        return {
            'success': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'model': model,
            'provider': 'groq',
            'mode': mode,
            'error': 'GROQ_API_KEY not configured'
        }
    
    # 프롬프트 구성
    title = notice.get('title', '')
    summary = notice.get('summary_text', '')
    agency = notice.get('agency', '')
    ministry = notice.get('ministry', '')
    apply_end = notice.get('apply_end', '')
    apply_start = notice.get('apply_start', '')
    category = notice.get('category', '')
    manual_note = notice.get('manual_note', '')
    
    user_note = f"\n사용자 메모: {manual_note}" if manual_note else ""
    
    system_prompt = """You are a Korean government grant analysis expert. Analyze the following grant notice for SW/IT company suitability.

Respond ONLY with valid JSON, no other text:
{"fit_score": 0-10, "summary": "brief summary", "strengths": "key strengths", "risks": "key risks", "next_actions": "recommended next actions"}"""

    user_prompt = f"""Analyze this grant notice:

Title: {title}
Summary: {summary}
Agency: {agency}
Ministry: {ministry}
Category: {category}
Apply Period: {apply_start} ~ {apply_end}{user_note}

Return ONLY JSON."""

    try:
        result = _make_request(
            url='https://api.groq.com/openai/v1/chat/completions',
            data={
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 1000
            },
            api_key=api_key,
            timeout=60
        )
        
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {
                'success': False,
                'fit_score': None,
                'summary': None,
                'strengths': None,
                'risks': None,
                'next_actions': None,
                'model': model,
                'provider': 'groq',
                'mode': mode,
                'error': f'Failed to parse response: {content[:200]}'
            }
        
        return {
            'success': True,
            'fit_score': parsed.get('fit_score'),
            'summary': parsed.get('summary'),
            'strengths': parsed.get('strengths'),
            'risks': parsed.get('risks'),
            'next_actions': parsed.get('next_actions'),
            'model': model,
            'provider': 'groq',
            'mode': mode,
            'error': None
        }
        
    except urllib.error.HTTPError as e:
        return {
            'success': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'model': model,
            'provider': 'groq',
            'mode': mode,
            'error': f'HTTP Error: {e.code} {e.reason}'
        }
    except Exception as e:
        return {
            'success': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'model': model,
            'provider': 'groq',
            'mode': mode,
            'error': str(e)
        }


def _analyze_with_nvidia(notice: Dict[str, Any], model: str, mode: str, api_key: str) -> Dict[str, Any]:
    """NVIDIA NIM API로 분석"""
    if not api_key:
        return {
            'success': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'model': model,
            'provider': 'nvidia',
            'mode': mode,
            'error': 'NVIDIA_API_KEY not configured'
        }
    
    return {
        'success': False,
        'fit_score': None,
        'summary': None,
        'strengths': None,
        'risks': None,
        'next_actions': None,
        'model': model,
        'provider': 'nvidia',
        'mode': mode,
        'error': 'NVIDIA provider is not yet implemented. Coming soon.'
    }


def _analyze_with_modal(notice: Dict[str, Any], model: str, mode: str, api_key: str) -> Dict[str, Any]:
    """Modal API로 분석"""
    if not api_key:
        return {
            'success': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'model': model,
            'provider': 'modal',
            'mode': mode,
            'error': 'MODAL_API_KEY not configured'
        }
    
    # 프롬프트 구성
    title = notice.get('title', '')
    summary = notice.get('summary_text', '')
    agency = notice.get('agency', '')
    ministry = notice.get('ministry', '')
    apply_end = notice.get('apply_end', '')
    apply_start = notice.get('apply_start', '')
    category = notice.get('category', '')
    manual_note = notice.get('manual_note', '')
    
    user_note = f"\nUser note: {manual_note}" if manual_note else ""
    
    system_prompt = """You are a Korean government grant analysis expert. Analyze the following grant notice for SW/IT company suitability.

Respond ONLY with valid JSON, no other text:
{"fit_score": 0-10, "summary": "brief summary", "strengths": "key strengths", "risks": "key risks", "next_actions": "recommended next actions"}"""

    user_prompt = f"""Analyze this grant notice:

Title: {title}
Summary: {summary}
Agency: {agency}
Ministry: {ministry}
Category: {category}
Apply Period: {apply_start} ~ {apply_end}{user_note}

Return ONLY JSON."""

    try:
        result = _make_request(
            url='https://api.us-west-2.modal.direct/v1/chat/completions',
            data={
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 2000
            },
            api_key=api_key,
            timeout=120
        )
        
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        parsed = None
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                except:
                    pass
            
            if not parsed or not isinstance(parsed, dict):
                return {
                    'success': False,
                    'fit_score': None,
                    'summary': None,
                    'strengths': None,
                    'risks': None,
                    'next_actions': None,
                    'model': model,
                    'provider': 'modal',
                    'mode': mode,
                    'error': f'Failed to parse response: {content[:300]}'
                }
        
        return {
            'success': True,
            'fit_score': parsed.get('fit_score'),
            'summary': parsed.get('summary'),
            'strengths': parsed.get('strengths'),
            'risks': parsed.get('risks'),
            'next_actions': parsed.get('next_actions'),
            'model': model,
            'provider': 'modal',
            'mode': mode,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'fit_score': None,
            'summary': None,
            'strengths': None,
            'risks': None,
            'next_actions': None,
            'model': model,
            'provider': 'modal',
            'mode': mode,
            'error': str(e)
        }


if __name__ == "__main__":
    # 테스트
    test_notice = {
        'title': '2026년 XaaS 선도 프로젝트 개발지원 신규과제 공고',
        'summary_text': 'SW기업이 중심이 되어 全 산업의 디지털 서비스화를 촉진',
        'agency': '정보통신산업진흥원',
        'ministry': '과학기술정보통신부',
        'category': 'SW',
        'apply_start': '2026-03-05',
        'apply_end': '2026-04-06',
        'manual_note': 'NIPA형, SW기업-산업전문기업 컨소시엄 구성 필요'
    }
    
    print("Testing AI provider (4 modes)...")
    for mode in ['quick', 'medium', 'deep', 'glm']:
        print(f"\n=== Testing mode: {mode} ===")
        result = analyze_notice(test_notice, mode=mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))