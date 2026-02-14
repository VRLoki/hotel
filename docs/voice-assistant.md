# Voice Assistant

Hotel Intel includes a built-in voice assistant on the **Daily Brief** page. It lets you listen to the briefing, ask questions about it, and interact naturally by voice or text.

---

## Features

### 1. Text-to-Speech (Listen Buttons)

Two options to have the daily brief read aloud:

| Button | Engine | Latency | Cost | Quality |
|--------|--------|---------|------|---------|
| **Listen** | Browser TTS (Web Speech API) | Instant | Free | Robotic, varies by device |
| **Listen (OpenAI)** | OpenAI TTS API (`tts-1`) | ~1-3s | ~$0.015 / 1K chars | Natural, human-like |

**How "Listen (OpenAI)" works:**
1. The briefing text is split into chunks (~300 characters each)
2. All chunks are sent to OpenAI's TTS API in parallel
3. Playback starts as soon as the first chunk returns (~1-2 seconds)
4. Chunks play back-to-back seamlessly

**Language support:** A language selector lets you choose from 9 languages (English, French, Spanish, German, Italian, Portuguese, Chinese, Japanese, Arabic). For non-English languages, the text is first translated via GPT-4o-mini, then spoken by the TTS engine. The translation prompt ensures proper number localization (e.g., "1 200 €" in French instead of "€1,200").

**Voice selection:** 11 OpenAI voices available — Ash, Ballad, Coral, Sage, Shimmer, Verse, Alloy, Echo, Fable, Nova, Onyx. Each has a different tone and character. Recommended: **Ash** (default), **Sage** or **Nova** for French.

---

### 2. Voice Conversation — Realtime Mode

Uses [OpenAI's Realtime API](https://platform.openai.com/docs/guides/realtime) for continuous, low-latency voice conversation.

**How it works:**
1. You press the microphone button
2. Backend requests an **ephemeral session token** from OpenAI (your API key never reaches the browser)
3. A **WebRTC** audio stream connects directly from your browser to OpenAI's servers
4. The full daily briefing is injected as context in the system prompt
5. You speak naturally — the AI responds in real-time with voice + text
6. Tap the mic to mute/unmute, press "End" to disconnect

**Pipeline:** Browser mic → WebRTC → OpenAI Realtime → WebRTC → Browser speaker

**Cost:** ~$0.06/min for audio input + output combined. A typical 2-minute Q&A session costs ~$0.12.

**Pros:** Very low latency, natural conversation flow, interruption support
**Cons:** Higher cost per minute, voice/language selection not customizable (uses session defaults)

---

### 3. Voice Conversation — Studio Mode

A push-to-talk approach using separate STT, LLM, and TTS steps. More control, lower cost per interaction.

**How it works:**
1. You press the microphone → recording starts (button pulses red)
2. You press again → recording stops, audio is sent to the backend
3. Backend pipeline runs three steps sequentially:
   - **Step 1 — Speech-to-Text:** Audio sent to OpenAI Whisper (`gpt-4o-mini-transcribe`). Transcribes your speech to text.
   - **Step 2 — LLM Processing:** Your question + conversation history + full briefing context sent to GPT-4o-mini. Generates a concise answer.
   - **Step 3 — Text-to-Speech:** The answer is sent to OpenAI TTS (`tts-1`). Audio is returned and played in the browser.
4. Transcript is displayed on screen for both your question and the AI's answer

**Pipeline:** Browser mic → Record WebM → POST to backend → Whisper STT → GPT-4o-mini → OpenAI TTS → MP3 → Browser playback

**Cost per interaction:**

| Step | Model | Typical cost |
|------|-------|-------------|
| STT | `gpt-4o-mini-transcribe` | ~$0.003 per 15s of audio |
| LLM | `gpt-4o-mini` | ~$0.001 per Q&A (with briefing context) |
| TTS | `tts-1` | ~$0.005 per response (~300 chars) |
| **Total** | | **~$0.01 per question** |

**Pros:** Respects voice & language selectors, conversation history maintained, ~10x cheaper than Realtime
**Cons:** Higher latency (~3-5 seconds round trip), push-to-talk (not continuous)

---

### 4. Voice Conversation — Local Mode

Fully offline, zero-cost alternative using local models. Same push-to-talk UI as Studio mode.

**How it works:**
1. You press the microphone → recording starts
2. You press again → recording stops, audio is sent to the backend
3. Backend pipeline runs three local steps:
   - **Step 1 — Speech-to-Text:** Audio converted to 16kHz WAV via ffmpeg, then transcribed by **whisper-cli** (whisper.cpp, `base.en` model)
   - **Step 2 — LLM Processing:** Your question + conversation history + briefing context sent to **Ollama** (llama3.2, 3B parameters)
   - **Step 3 — Text-to-Speech:** Response synthesized by **Piper** TTS (ONNX neural voices)
4. WAV audio returned and played in the browser

**Pipeline:** Browser mic → Record WebM → POST to backend → ffmpeg → whisper.cpp → Ollama → Piper → WAV → Browser playback

**Cost per interaction: $0.00** (everything runs locally)

**Performance on Mac Mini M4:**

| Step | Model | Latency |
|------|-------|---------|
| STT | whisper.cpp (base.en) | ~1-2s |
| LLM | Ollama llama3.2 (3B) | ~2-3s |
| TTS | Piper (medium voice) | ~0.3s |
| **Total** | | **~4-7s per turn** |

**Available Piper voices:**
- English: `en_US-lessac-medium` (clear, professional)
- French: `fr_FR-siwis-medium` (natural French)
- More voices can be downloaded from [Piper Voices](https://huggingface.co/rhasspy/piper-voices)

**Local dependencies:**
- `whisper-cpp` (Homebrew) + `ggml-base.en.bin` model
- `ollama` with `llama3.2` model pulled
- `piper-tts` (Python package) + ONNX voice models
- `ffmpeg` for audio conversion

**Pros:** Zero cost, full data sovereignty, works offline, no API keys needed
**Cons:** Higher latency (~5-7s), lower voice quality than OpenAI TTS, limited to available Piper voices

---

### GPU Scaling — Performance with Dedicated Hardware

Local mode performance scales dramatically with better hardware:

| Component | Mac Mini M4 | RTX 4090 | A100 (80GB) |
|-----------|-------------|----------|-------------|
| Whisper (large-v3) | 1-2s | 0.2s | 0.1s |
| LLM (Llama 3.2 3B) | 2-3s | 0.3s | 0.2s |
| LLM (Llama 3.1 70B) | ❌ too large | 0.5-1s | 0.3-0.5s |
| Piper TTS | 0.3s | 0.1s | 0.1s |
| **Total round-trip** | **~5s** | **~1s** | **~0.5s** |

With a dedicated GPU, you could also run **Ultravox** — an open-source model that handles audio→audio natively (like OpenAI Realtime), achieving ~0.3s latency with zero API costs.

---

## Architecture

```
┌──────────────────────────────────────────┐
│            Browser (Frontend)             │
├──────────────────────────────────────────┤
│  Listen (Browser)  → Web Speech API      │  ← Free, local
│  Listen (OpenAI)   → /api/voice/tts      │  ← Chunked streaming
│  Realtime Mode     → WebRTC direct       │  ← Ephemeral token via /api/voice/session
│  Studio Mode       → /api/voice/studio   │  ← Record → POST → Play (OpenAI APIs)
│  Local Mode        → /api/voice/local    │  ← Record → POST → Play (all local)
└───────────────┬──────────────────────────┘
                │
┌───────────────▼──────────────────────────┐
│          Backend (FastAPI)                │
├──────────────────────────────────────────┤
│  POST /api/voice/session   → OpenAI Realtime Session API
│  POST /api/voice/tts       → (translate) → OpenAI TTS API
│  POST /api/voice/studio    → Whisper API → GPT-4o-mini → OpenAI TTS
│  POST /api/voice/local     → whisper.cpp → Ollama → Piper
└───────┬───────────────────────┬──────────┘
        │                       │
┌───────▼───────────┐  ┌───────▼───────────┐
│   OpenAI APIs     │  │   Local Models     │
├───────────────────┤  ├───────────────────┤
│  Realtime (WebRTC)│  │  whisper.cpp      │
│  Whisper API      │  │  Ollama (llama3.2)│
│  GPT-4o-mini      │  │  Piper TTS       │
│  TTS-1            │  │                   │
└───────────────────┘  └───────────────────┘
```

---

## Engine Comparison

| Feature | OpenAI Realtime | Studio (Cloud) | Local |
|---------|----------------|----------------|-------|
| Latency | ~0.5-1s | ~3-5s | ~4-7s |
| Cost/interaction | ~$0.06/min | ~$0.01 | $0.00 |
| Voice quality | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Data privacy | Cloud | Cloud | ★★★★★ Full local |
| Conversation style | Continuous | Push-to-talk | Push-to-talk |
| Language selector | No (session-level) | Yes | Yes (en/fr) |
| Voice selector | No | Yes (11 voices) | Per-language |
| Works offline | No | No | Yes |

---

## Configuration

**OpenAI API key** (for Realtime, Studio, and Listen OpenAI): stored server-side in `dashboard/.env`:

```
OPENAI_API_KEY=sk-...
```

The key is **never exposed to the browser**. For Realtime mode, the backend generates a short-lived ephemeral token.

**Local models** (for Local mode): stored in `models/` directory:
- `whisper-base.bin` — Whisper.cpp GGML model
- `piper-en.onnx` + `.json` — Piper English voice
- `piper-fr.onnx` + `.json` — Piper French voice

**Ollama:** must be running locally (`ollama serve`) with `llama3.2` pulled.

---

## Cost Summary

| Usage pattern | Realtime | Studio | Local |
|--------------|----------|--------|-------|
| Listen to briefing (TTS) | — | ~$0.03 | $0.00 |
| 5 questions | ~$0.30 | ~$0.05 | $0.00 |
| Full day usage (10 listens + 20 questions) | ~$1.50 | ~$0.50 | $0.00 |
| Listen + French translation | — | ~$0.04 | $0.00 |

All costs are approximate based on OpenAI pricing as of early 2026.
