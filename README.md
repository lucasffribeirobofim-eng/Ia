# IA de edição automática profissional

Este projeto configura um fluxo local, em português do Brasil, para usar o repositório [`browser-use/video-use`](https://github.com/browser-use/video-use) como base de edição automática com prioridade **QUALIDADE_ACIMA_DE_ECONOMIA**.

> Estado deste ambiente: `ffmpeg` e `ffprobe` não estão instalados, então a análise/renderização de vídeo deve parar até que eles estejam disponíveis no `PATH`.

## Saídas padrão

Todos os artefatos de cada trabalho ficam dentro da pasta de saída escolhida, preferencialmente em `edit/`:

- `takes_packed.md`
- `edl.json`
- `preview.mp4`
- `final.mp4`
- `project.md`
- `legendas.srt` apenas quando legendas forem solicitadas

## Uso

1. Copie `.env.example` para `.env` e preencha `ELEVENLABS_API_KEY` sem versionar a chave.
2. Instale `ffmpeg` e `ffprobe`.
3. Execute a checagem inicial:

```bash
python3 scripts/pro_video_editor.py setup --output-dir /caminho/da/pasta --video-use-path /caminho/para/video-use
```

4. Antes de editar, responda às perguntas de legendas e estilo.
5. Inicie um job apontando o vídeo:

```bash
python3 scripts/pro_video_editor.py plan --input-video /caminho/video.mp4 --output-dir /caminho/da/pasta --subtitles no
```

O comando `plan` cria a estrutura `edit/` e os arquivos iniciais de controle. A renderização deve ser executada somente depois de dependências, Video Use e ElevenLabs estarem validados.

## Política editorial padrão

- Estilo padrão: **LIMPO E NATURAL**.
- Idioma principal: `pt-BR`.
- Nunca cortar palavras no meio.
- Preferir manter quando houver ambiguidade.
- Preservar qualidade, resolução, FPS, proporção, áudio, sincronização e enquadramento.
- Não aplicar HyperFrames, Remotion, overlays, zoom, animações, transições ou efeitos exagerados sem pedido explícito.
