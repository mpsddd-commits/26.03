## streamlit 알아보기

- [streamlit](https://streamlit.io/)

#### 실행 명령어

```bash
uv run streamlit run main.py
```

## trafilatura 알아보기

- [trafilatura](https://pypi.org/project/trafilatura/)
- [Document](https://trafilatura.readthedocs.io/en/latest/)
- `trafilatura` 설치
```bash
uv add trafilatura
```

## Ollama 알아보기 : `LLM 서버`

- [앱 다운받기](https://ollama.com/download)
- [LLM 모델 검색](https://ollama.com/search)

#### 1. 서버 PC 설정
- Ollama 버젼 확인
```bash
ollama --version
```

- `GPT-OSS:20b` 모델 받기
```bash
ollama pull gpt-oss:20b
```

- 환경 변수 추가 : `외부 접속 허용`
```bash
OLLAMA_HOST=0.0.0.0
```

- 방화벽 포트 허용 : `인바운드 규칙` 추가
```bash
이름 : OLLAMA
프로토콜 : TCP
포트 : 11434
```

- CLI 방식으로 서버 실행 : `log` 확인 가능
```bash
ollama serve
```

- 모델 확인 `get` 요청
```bash
curl http://localhost:11434/api/tags
```

- 프롬프트 `post` 요청
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:8b",
    "prompt": "Ollma에 대해 간단하게 설명해주세요.",
    "stream": false
  }'
```

#### 2. 로컬 (클라이언트) PC

- 환경 변수 추가 : `ollama 서버 URL`
```bash
OLLAMA_HOST=http://192.168.0.203:11434
```

- ollama 모듈 설치
```bash
uv add ollama
```

- 요청코드
```python
import ollama

response = ollama.chat(
  model='gpt-oss:20b',
  messages=[{'role': 'user', 'content': '안녕하세요'}]
)
```