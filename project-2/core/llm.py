"""Small Responses-compatible transport for the task evaluators and local Ollama."""
import json
from types import SimpleNamespace
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import URLError
from uuid import uuid4

LOCAL_MODEL = 'qwen3:1.7b'
DEFAULT_JUDGE = 'gpt-6-luna'
MODELS = {'gpt-5-nano': 'GPT-5 nano', DEFAULT_JUDGE: 'GPT-6 Luna',
          LOCAL_MODEL: 'Qwen3 1.7B (local · Ollama)'}
RESULT_MODELS = {model: label for model, label in MODELS.items() if model != LOCAL_MODEL}
JUDGES = {DEFAULT_JUDGE: MODELS[DEFAULT_JUDGE], LOCAL_MODEL: MODELS[LOCAL_MODEL]}
OLLAMA_URL = 'http://127.0.0.1:11434'


def local_request(path, payload=None, timeout=10):
    request = Request(OLLAMA_URL + path, data=json.dumps(payload).encode() if payload is not None else None,
                      headers={'Content-Type': 'application/json'})
    try:
        # Loopback traffic must never travel through a configured HTTP proxy.
        with build_opener(ProxyHandler({})).open(request, timeout=timeout) as response:
            return json.load(response)
    except (URLError, TimeoutError) as exc:
        raise RuntimeError('Ollama is unavailable. Start Ollama and run: ollama pull qwen3:1.7b') from exc


def check_local():
    models = local_request('/api/tags').get('models', [])
    if not any(m.get('name') == LOCAL_MODEL or m.get('model') == LOCAL_MODEL for m in models):
        raise RuntimeError('Local model is missing. Run: ollama pull qwen3:1.7b')
    return 'Ollama is ready with Qwen3 1.7B.'


class Record(SimpleNamespace):
    def model_dump(self, **kwargs):
        return {k: v.model_dump(**kwargs) if hasattr(v, 'model_dump') else v for k, v in vars(self).items()}


class Client:
    """Bind a client to a role so legacy hardcoded judge IDs cannot change routing."""
    def __init__(self, model, hosted=None):
        if model not in MODELS:
            raise ValueError('Unsupported model')
        self.model, self.hosted = model, hosted
        self.responses = self

    def create(self, **request):
        request['model'] = self.model
        if self.model != LOCAL_MODEL:
            return self.hosted.responses.create(**request)
        fmt = request.get('text', {}).get('format', {})
        payload = dict(model=self.model, stream=False, think=False,
                       messages=[{'role': 'system', 'content': request.get('instructions', '')},
                                 {'role': 'user', 'content': request['input']}],
                       format=fmt.get('schema', 'json'),
                       options={'num_ctx': 40960, 'num_predict': request.get('max_output_tokens', 8192), 'temperature': 0})
        data = local_request('/api/chat', payload, timeout=900)
        content = data.get('message', {}).get('content', '')
        if data.get('model') != self.model:
            raise ValueError('Ollama returned an unexpected model')
        return Record(id='ollama-' + uuid4().hex, model=data['model'], output_text=content,
                      status='completed' if data.get('done') and data.get('done_reason') == 'stop' and content.strip() else 'incomplete',
                      usage=Record(input_tokens=data.get('prompt_eval_count'), output_tokens=data.get('eval_count')),
                      raw_ollama=data)

    def parse(self, text_format, **request):
        if self.model != LOCAL_MODEL:
            return self.hosted.responses.parse(model=self.model, text_format=text_format,
                                              **{k: v for k, v in request.items() if k != 'model'})
        request['text'] = {'format': {'schema': text_format.model_json_schema()}}
        result = self.create(**request)
        result.output_parsed = text_format.model_validate_json(result.output_text) if result.status == 'completed' else None
        return result


def clients(candidate, judge):
    if candidate not in MODELS or judge not in JUDGES:
        raise ValueError('Unsupported candidate or judge')
    if LOCAL_MODEL in (candidate, judge):
        check_local()
    hosted = None
    required = {candidate, judge} - {LOCAL_MODEL}
    if required:
        from openai import OpenAI
        hosted = OpenAI(base_url='https://api.openai.com/v1', timeout=240, max_retries=0)
        if not required <= {m.id for m in hosted.models.list()}:
            raise RuntimeError('Exact candidate or judge model unavailable; no model substituted')
    return Client(candidate, hosted), Client(judge, hosted)
