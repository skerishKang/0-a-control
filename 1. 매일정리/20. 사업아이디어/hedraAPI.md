## Hedra API (0.1.0) 문서 정리

**API 개요**

*   **이름:** Hedra API
*   **버전:** 0.1.0
*   **Base URL:** `https://mercury.dev.dream-ai.com/api`
*   **API Key:** `X-API-KEY` 헤더를 통해 전달

**API 사용 예시 (Python)**

```python
import requests

BASE_URL = "https://mercury.dev.dream-ai.com/api"
API_KEY = "YOUR_API_KEY"  # 실제 API 키로 대체

# 1. 오디오 업로드
def upload_audio(audio_file_path):
    """오디오 파일을 업로드합니다."""
    url = f"{BASE_URL}/v1/audio"
    headers = {'X-API-KEY': API_KEY}
    files = {'file': open(audio_file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response.json() if response.status_code == 200 else None

# 2. 이미지 업로드
def upload_image(image_file_path):
    """이미지 파일을 업로드합니다."""
    url = f"{BASE_URL}/v1/portrait"
    headers = {'X-API-KEY': API_KEY}
    files = {'file': open(image_file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response.json() if response.status_code == 200 else None

# 3. 캐릭터 비디오 생성 초기화
def generate_character_video(avatar_image_url, audio_source, voice_url):
    """캐릭터 비디오 생성을 초기화합니다."""
    url = f"{BASE_URL}/v1/characters"
    headers = {'X-API-KEY': API_KEY}
    data = {
        "avatarImage": avatar_image_url,
        "audioSource": audio_source,
        "voiceUrl": voice_url
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json() if response.status_code == 200 else None

# 4. 프로젝트 상태 확인
def get_project_status(project_id):
    """프로젝트 상태를 확인합니다."""
    url = f"{BASE_URL}/v1/projects/{project_id}"
    headers = {'X-API-KEY': API_KEY}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
```

**API Endpoint 요약**

| Endpoint                      | Method | 설명                                                                                                              | 인증      | 요청 Body            | 응답 예시                                                                     |
| :---------------------------- | :----- | :---------------------------------------------------------------------------------------------------------------- | :-------- | :------------------- | :------------------------------------------------------------------------------ |
| `/v1/voices`                 | GET    | 사용 가능한 음성 목록 조회                                                                                        | APIKeyHeader | 없음                 | `{"supported_voices": [{...}]}`                                                  |
| `/v1/audio`                  | POST   | 오디오 파일 업로드                                                                                                | APIKeyHeader | `multipart/form-data` (`file`: 바이너리 오디오 파일)                                 | `{"url": "string"}`                                                            |
| `/v1/portrait`               | POST   | 이미지 파일 업로드                                                                                                | APIKeyHeader | `multipart/form-data` (`file`: 바이너리 이미지 파일)                                 | `{"url": "string"}`                                                            |
| `/v1/characters`             | POST   | 캐릭터 생성 작업 초기화 (talking head avatar)                                                                    | APIKeyHeader | JSON (`text`, `voiceId`, `voiceUrl`, `avatarImage`, `aspectRatio`, `audioSource`, `avatarImageInput`) | `{"jobId": "string"}`                                                           |
| `/v1/projects`               | GET    | 현재 사용자의 모든 프로젝트 조회                                                                                    | APIKeyHeader | 없음                 | `{"projects": [{...}]}`                                                          |
| `/v1/projects/{project_id}` | GET    | 특정 프로젝트 정보 조회                                                                                           | APIKeyHeader | 없음                 | `{"id": "string", "createdAt": "datetime", ...}`                               |
| `/v1/projects/{project_id}` | DELETE | 특정 프로젝트 삭제                                                                                                | APIKeyHeader | 없음                 | `null`                                                                          |
| `/v1/projects/{project_id}/sharing` | POST | 특정 프로젝트 공유/공유 해제                                                                                         | APIKeyHeader | 없음                 | `null`                                                                          |
| `/v1/user/register`          | POST   | 사용자 등록                                                                                                        | 없음       | JSON (`residence_not_blocked`, `tos_accepted`, `tos_version`, ...) | `{"data": {"userId": "string", ...}}`                                           |
| `/v1/images/text-to-image`   | POST   | 텍스트 프롬프트 기반 이미지 생성                                                                                      | JWTBearer  | JSON (`prompt`, `num_inference_steps`, `controlnets`, `ip_adapters`, ...)     | `{"images": [{...}], "timings": {...}, "seed": 0, "has_nsfw_concepts": [...]}` |

**주요 데이터 모델 (스키마) 정의**

(자세한 내용은 원본 OpenAPI 정의 파일을 참고하세요.)

*   **Voice:** 음성 정보 (voice\_id, service, name, description 등)
*   **AvatarProjectItem:** 프로젝트 정보 (id, createdAt, videoUrl, avatarImageUrl, status 등)
*   **ImageGenerationRequestBody:** 이미지 생성 요청 Body (prompt, num\_inference\_steps, controlnets, ip\_adapters 등)
*   **ImageGenerationResponseBody:** 이미지 생성 응답 Body (images, timings, seed, has\_nsfw\_concepts 등)
*   **UserInfo:** 사용자 정보 (userId, username, accountTier, avatarProjectCreditLimit 등)

**추가 참고 사항**

*   위 내용은 제공해주신 명세서의 핵심 내용을 요약한 것입니다.  더 자세한 정보는 원본 OpenAPI 정의 파일을 참고하세요.
*   API를 사용하기 전에 각 endpoint에 필요한 파라미터, 요청 body, 인증 방식 등을 꼼꼼히 확인하세요.
*   오류가 발생하면 응답 코드와 메시지를 확인하고, 필요에 따라 API 제공자에게 문의하세요.
*   API 사용량 제한 (rate limiting) 및 가격 정책에 대한 정보는 별도로 확인해야 합니다.

이 문서를 필요에 따라 수정하고, 내용을 추가하거나 삭제하여 사용하시면 됩니다.  파일로 저장할 때는 Markdown (.md) 또는 텍스트 (.txt) 형식으로 저장하는 것이 좋습니다.