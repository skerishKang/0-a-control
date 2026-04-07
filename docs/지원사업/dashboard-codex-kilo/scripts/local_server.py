#!/usr/bin/env python3
"""
지원사업 대시보드 로컬 웹 서버
라우팅만 담당 (표준 라이브러리만 사용)
"""

import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse

# 경로 설정
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "db" / "notices.sqlite3"

# 모듈 import (분리된 구조)
import repositories.notice_repo as notice_repo
import services.notice_service as notice_service
import renderers.pages as pages


# HTTP 서버 클래스
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            notices = notice_repo.fetch_notices()
            content = pages.render_main_page(notices)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        
        elif parsed.path.startswith('/notice/'):
            notice_id = parsed.path.split('/')[-1]
            try:
                notice_id = int(notice_id)
            except:
                self.send_error(400, "Invalid notice ID")
                return
            
            notice = notice_repo.fetch_notice_by_id(notice_id)
            if not notice:
                self.send_error(404, "Notice not found")
                return
            
            content = pages.render_detail_page(notice)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        
        elif parsed.path == '/api/notices':
            notices = notice_repo.fetch_notices()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(notices, ensure_ascii=False).encode('utf-8'))
        
        else:
            self.send_error(404, "Not found")
    
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        if parsed.path == '/collect':
            try:
                print("[server] POST /collect start", flush=True)
                data = json.loads(body)
                url = data.get('url', '')
                
                if not url:
                    self.send_json({'success': False, 'error': 'URL is required'})
                    return
                
                print(f"[server] collect url={url}", flush=True)
                notice_id = notice_service.collect_notice(url)
                notice = notice_repo.fetch_notice_by_id(notice_id)
                print(f"[server] POST /collect done: notice_id={notice_id}", flush=True)
                
                self.send_json({
                    'success': True,
                    'notice_id': notice_id,
                    'title': notice['title'] if notice else ''
                })
            except Exception as e:
                print(f"[server] POST /collect error: {e}", flush=True)
                self.send_json({'success': False, 'error': str(e)})
        
        elif parsed.path == '/update':
            try:
                data = json.loads(body)
                notice_id = data.get('notice_id')
                status = data.get('status')
                note = data.get('note')
                summary = data.get('summary')
                
                result = notice_repo.update_notice(
                    notice_id=notice_id,
                    status=status,
                    note=note,
                    summary=summary
                )
                
                self.send_json({
                    'success': result is not None,
                    'error': None if result is not None else 'Update failed'
                })
            except Exception as e:
                self.send_json({'success': False, 'error': str(e)})
                
        elif parsed.path == '/update-ai':
            try:
                data = json.loads(body)
                notice_id = data.get('notice_id')
                ai_fit_score = data.get('ai_fit_score')
                ai_summary = data.get('ai_summary')
                ai_strengths = data.get('ai_strengths')
                ai_risks = data.get('ai_risks')
                ai_next_actions = data.get('ai_next_actions')
                ai_model = data.get('ai_model')
                ai_raw_json = data.get('ai_raw_json')
                
                # Convert empty strings to None for numeric fields
                if ai_fit_score == '':
                    ai_fit_score = None
                elif ai_fit_score is not None:
                    try:
                        ai_fit_score = float(ai_fit_score)
                    except ValueError:
                        ai_fit_score = None
                
                result = notice_repo.update_ai_analysis(
                    notice_id=notice_id,
                    ai_fit_score=ai_fit_score,
                    ai_summary=ai_summary,
                    ai_strengths=ai_strengths,
                    ai_risks=ai_risks,
                    ai_next_actions=ai_next_actions,
                    ai_model=ai_model,
                    ai_raw_json=ai_raw_json
                )
                
                self.send_json({
                    'success': result,
                    'error': None if result else 'Notice not found'
                })
            except Exception as e:
                self.send_json({'success': False, 'error': str(e)})
        
        elif parsed.path == '/analyze-ai':
            import ai_provider
            
            try:
                data = json.loads(body)
                notice_id = data.get('notice_id') or data.get('source_notice_id')
                mode = data.get('mode', 'quick')  # default: quick
                
                if not notice_id:
                    self.send_json({'success': False, 'error': 'notice_id is required'})
                    return
                
                # DB에서 공고 정보 조회
                notice = notice_repo.fetch_notice_by_source_id(notice_id)
                
                if not notice:
                    self.send_json({'success': False, 'error': 'Notice not found'})
                    return
                
                # AI 분석 실행 (mode 전달)
                result = ai_provider.analyze_notice(notice, mode=mode)
                
                if not result.get('success'):
                    self.send_json({
                        'success': False,
                        'error': result.get('error', 'Analysis failed')
                    })
                    return
                
                # 분석 결과를 DB에 저장 (mode/provider/fallback_used 포함)
                notice_repo.update_ai_analysis(
                    notice_id=notice_id,
                    ai_fit_score=result.get('fit_score'),
                    ai_summary=result.get('summary'),
                    ai_strengths=result.get('strengths'),
                    ai_risks=result.get('risks'),
                    ai_next_actions=result.get('next_actions'),
                    ai_model=result.get('model'),
                    ai_mode=result.get('mode'),
                    ai_provider=result.get('provider'),
                    ai_fallback_used=1 if result.get('fallback_used') else 0
                )
                
                self.send_json({
                    'success': True,
                    'result': {
                        'mode': result.get('mode'),
                        'provider': result.get('provider'),
                        'model': result.get('model'),
                        'fallback_used': result.get('fallback_used', False),
                        'fit_score': result.get('fit_score'),
                        'summary': result.get('summary'),
                        'strengths': result.get('strengths'),
                        'risks': result.get('risks'),
                        'next_actions': result.get('next_actions')
                    }
                })
            except Exception as e:
                self.send_json({'success': False, 'error': str(e)})
        
        elif parsed.path == '/delete':
            try:
                data = json.loads(body)
                notice_id = data.get('notice_id')
                
                if not notice_id:
                    self.send_json({'success': False, 'error': 'notice_id is required'})
                    return
                
                # 공고 삭제
                notice_repo.delete_notice(int(notice_id))
                
                self.send_json({'success': True})
            except Exception as e:
                self.send_json({'success': False, 'error': str(e)})
        
        else:
            self.send_error(404, "Not found")
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")


# 메인 실행 함수
def run_server(port=8766):
    host = '127.0.0.1'
    server = HTTPServer((host, port), RequestHandler)
    print(f"🚀 지원사업 대시보드 서버 실행 중: http://{host}:{port}")
    print(f"종료하려면 Ctrl+C를 누르세요")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    run_server(args.port)
