import sys
import os
import logging
import json
from urllib import request, error
try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def setup_logging() -> None:
    try:
        appdata = os.getenv('APPDATA') or os.path.expanduser('~')
        log_dir = os.path.join(appdata, 'VirtualDeskmate', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info('Logging initialized')
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logging.warning('Logging setup failed: %s', e)



class ChatClient:
    def __init__(self, api_key: str, model: str = 'gpt-4o-mini', base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        if not self.api_key:
            raise ValueError('OpenAI API key is missing')
        # If SDK available, initialize it; otherwise use HTTP fallback
        self.client = None
        if OpenAI is not None:
            kwargs = {'api_key': self.api_key}
            if self.base_url:
                kwargs['base_url'] = self.base_url.rstrip('/')
            self.client = OpenAI(**kwargs)  # type: ignore[arg-type]

    def chat(self, messages):
        # Prefer SDK when available; otherwise POST directly
        if self.client is not None:
            try:
                result = self.client.chat.completions.create(  # type: ignore[attr-defined]
                    model=self.model,
                    messages=messages,
                    temperature=0.7
                )
                if not result or not getattr(result, 'choices', None):
                    raise RuntimeError(f'Unexpected API response: {result}')
                message = result.choices[0].message
                content = getattr(message, 'content', None)
                if not content:
                    raise RuntimeError('No content in assistant message')
                return content
            except Exception as e:
                raise RuntimeError(f'Failed to call OpenAI API (SDK): {e}')
        else:
            # HTTP fallback (compatible with /v1)
            base = (self.base_url or 'https://api.openai.com').rstrip('/')
            url = f"{base}/v1/chat/completions"
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.7
            }
            data = json.dumps(payload).encode('utf-8')
            req = request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {self.api_key}')
            try:
                with request.urlopen(req, timeout=60) as resp:
                    body = resp.read()
                    parsed = json.loads(body.decode('utf-8'))
                    return parsed['choices'][0]['message']['content']
            except error.HTTPError as e:
                detail = e.read().decode('utf-8', errors='ignore')
                raise RuntimeError(f"API error {e.code}: {detail}")
            except Exception as e:
                raise RuntimeError(f"Failed to call OpenAI API (HTTP): {e}")