#!/usr/bin/env python3
"""
Settings loader for .env files
标准 라이브러리만 사용
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

# 프로젝트 루트
ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = ROOT_DIR / ".env"

# 캐시된 설정
_settings: Optional[Dict[str, str]] = None


def load_env() -> Dict[str, str]:
    """
    .env 파일과 환경변수를 읽어設定を読み込む
    환경변수가 .env보다 우선
    """
    global _settings
    if _settings is not None:
        return _settings
    
    settings = {}
    
    # 1. .env 파일 읽기
    if ENV_PATH.exists():
        try:
            with open(ENV_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 빈 줄과 주석 건너뛰기
                    if not line or line.startswith('#'):
                        continue
                    # 키=값 파싱
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 따옴표 제거
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        if key:
                            settings[key] = value
        except Exception as e:
            print(f"Warning: Failed to load .env: {e}")
    
    # 2. 환경변수가 있으면 그것으로 덮어쓰기
    for key in list(settings.keys()):
        env_value = os.environ.get(key)
        if env_value is not None:
            settings[key] = env_value
    
    _settings = settings
    return settings


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    설정값 가져오기
    """
    settings = load_env()
    return settings.get(name, default)


def get_provider() -> str:
    """
    현재 선택된 AI provider 반환 (legacy 호환)
    """
    return get_setting('AI_PROVIDER', 'groq')


def get_mode_config(mode: str) -> Dict[str, str]:
    """
    분석 모드별 설정 반환 (legacy 호환용)
    
    Args:
        mode: "quick", "medium", "deep", 또는 "glm"
    
    Returns:
        {"provider": "...", "model": "...", "api_key": "..."}
    """
    config = get_ai_mode_config(mode)
    return {
        "provider": config.get("provider", "groq"),
        "model": config.get("model", ""),
        "api_key": config.get("api_key", "")
    }


def get_ai_mode_config(mode: str) -> Dict[str, Any]:
    """
    분석 모드별 설정 반환 (4단계 + fallback 지원)
    
    Args:
        mode: "quick", "medium", "deep", 또는 "glm"
    
    Returns:
        {
            "provider": "...", 
            "model": "...", 
            "api_key": "...",
            "fallbacks": ["model1", "model2", ...]
        }
    """
    settings = load_env()
    mode = mode.lower()
    
    # mode별 설정 키
    provider_key = f"AI_{mode.upper()}_PROVIDER"
    model_key = f"AI_{mode.upper()}_MODEL"
    fallbacks_key = f"AI_{mode.upper()}_FALLBACKS"
    
    provider = settings.get(provider_key)
    model = settings.get(model_key)
    fallbacks_str = settings.get(fallbacks_key, '')
    
    # fallback 파싱 (쉼표로 구분)
    fallbacks = []
    if fallbacks_str:
        for f in fallbacks_str.split(','):
            f = f.strip()
            if f:
                fallbacks.append(f)
    
    # provider별 API 키 찾기
    api_key = None
    if provider == 'groq':
        api_key = settings.get('GROQ_API_KEY')
    elif provider == 'modal':
        api_key = settings.get('MODAL_API_KEY')
    elif provider == 'nvidia':
        api_key = settings.get('NVIDIA_API_KEY')
    
    # fallback: legacy 단일 provider 설정
    if not provider:
        provider = get_setting('AI_PROVIDER', 'groq')
    
    # fallback: legacy 단일 model 설정
    if not model:
        if provider == 'groq':
            model = settings.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
        elif provider == 'modal':
            model = settings.get('MODAL_MODEL', 'zai-org/GLM-5-FP8')
        elif provider == 'nvidia':
            model = settings.get('NVIDIA_MODEL', 'meta/llama-3.3-70b-instruct')
    
    return {
        "provider": provider or "groq",
        "model": model or "",
        "api_key": api_key,
        "fallbacks": fallbacks
    }


def get_all_modes() -> list:
    """지원하는 모든 분석 모드 목록 반환"""
    return ["quick", "medium", "deep", "glm"]


def get_mode_provider(model: str) -> str:
    """model 이름에서 provider 추측"""
    if 'GLM' in model or 'modal' in model.lower():
        return 'modal'
    elif 'groq' in model.lower():
        return 'groq'
    elif 'nvidia' in model.lower():
        return 'nvidia'
    return 'groq'


def get_kstartup_api_key() -> str:
    """K-Startup API Key 반환"""
    return get_setting('KSTARTUP_API_KEY', '')


def get_bizinfo_api_key() -> str:
    """Bizinfo (기업마당) API Key 반환"""
    return get_setting('BIZINFO_API_KEY', '')


def reload():
    """설정 다시 로드 (캐시をクリア)"""
    global _settings
    _settings = None


if __name__ == "__main__":
    # 테스트
    print("Settings loaded:")
    for k, v in load_env().items():
        # API 키는 마스킹
        if 'KEY' in k and v:
            print(f"  {k}={v[:4]}...")
        else:
            print(f"  {k}={v}")
    print("\nMode configs:")
    for mode in ['quick', 'deep']:
        config = get_mode_config(mode)
        print(f"  {mode}: {config}")
