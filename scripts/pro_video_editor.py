#!/usr/bin/env python3
"""Professional guardrails for a Video Use based automatic editor."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "professional_editing.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def command_version(command: str) -> str | None:
    if shutil.which(command) is None:
        return None
    result = subprocess.run(
        [command, "-version"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout.splitlines()[0] if result.stdout else "installed"


def elevenlabs_key_present() -> bool:
    return bool(os.environ.get("ELEVENLABS_API_KEY", "").strip())


def assert_setup(video_use_path: Path | None = None) -> int:
    ffmpeg = command_version("ffmpeg")
    ffprobe = command_version("ffprobe")
    missing = []
    if ffmpeg is None:
        missing.append("ffmpeg")
    if ffprobe is None:
        missing.append("ffprobe")

    print("Configuração profissional de edição automática")
    print(f"Config: {CONFIG_PATH}")
    print(f"ffmpeg: {ffmpeg or 'NÃO INSTALADO'}")
    print(f"ffprobe: {ffprobe or 'NÃO INSTALADO'}")
    print(f"ElevenLabs API key: {'presente' if elevenlabs_key_present() else 'ausente'}")

    if video_use_path:
        skill = video_use_path / "SKILL.md"
        helpers = video_use_path / "helpers"
        print(f"Video Use: {video_use_path}")
        print(f"Video Use skill: {'ok' if skill.exists() else 'não encontrado'}")
        print(f"Video Use helpers: {'ok' if helpers.exists() else 'não encontrado'}")

    if missing:
        print("\nERRO: instale as dependências antes de continuar:")
        print("- Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg")
        print("- macOS/Homebrew: brew install ffmpeg")
        return 2

    if not elevenlabs_key_present():
        print("\nERRO: defina ELEVENLABS_API_KEY no ambiente ou em .env antes de transcrever.")
        return 3

    print("\nSetup básico validado. Próxima etapa: analisar o vídeo e gerar transcrição word-level com ElevenLabs Scribe.")
    return 0


def create_job(args: argparse.Namespace) -> int:
    config = load_config()
    edit_dir = Path(args.output_dir).expanduser().resolve() / config["subdirectory"]
    edit_dir.mkdir(parents=True, exist_ok=True)

    subtitles = args.subtitles.lower()
    if subtitles == "yes" and not args.subtitle_style:
        print("ERRO: informe --subtitle-style quando --subtitles yes.")
        return 4

    project = {
        "input_video": str(Path(args.input_video).expanduser().resolve()),
        "output_dir": str(edit_dir),
        "language": config["language"],
        "style": args.style,
        "priority": config["priority"],
        "subtitles": subtitles == "yes",
        "subtitle_style": args.subtitle_style if subtitles == "yes" else None,
        "flow": [
            "análise completa",
            "transcrição word-level ElevenLabs Scribe",
            "detecção de silêncios/repetições/erros/falsos começos/frases abandonadas",
            "decisão REMOVER/MANTER/REVISAR com ambiguidade=MANTER",
            "preview.mp4",
            "revisão de naturalidade",
            "final.mp4",
            "verificação final com ffprobe",
        ],
    }

    (edit_dir / "project.md").write_text(render_project_md(project), encoding="utf-8")
    (edit_dir / "edl.json").write_text(json.dumps({"cuts": [], "review": [], "policy": config["decision_policy"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    (edit_dir / "takes_packed.md").write_text("# Takes packed\n\nAguardando análise e transcrição.\n", encoding="utf-8")
    print(f"Projeto configurado em: {edit_dir}")
    print("Próximo comando/etapa: validar setup, transcrever com ElevenLabs Scribe e gerar preview.mp4.")
    return 0


def render_project_md(project: dict) -> str:
    lines = ["# Projeto de edição automática", ""]
    for key, value in project.items():
        if key == "flow":
            lines.append("## Fluxo obrigatório")
            lines.extend(f"{idx}. {item}" for idx, item in enumerate(value, 1))
        else:
            lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("Regra principal: natural + fluido + profissional + boa qualidade + sem alterar o sentido original.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("setup")
    setup.add_argument("--output-dir", required=True)
    setup.add_argument("--video-use-path", type=Path)

    plan = sub.add_parser("plan")
    plan.add_argument("--input-video", required=True)
    plan.add_argument("--output-dir", required=True)
    plan.add_argument("--subtitles", choices=["yes", "no"], required=True)
    plan.add_argument("--subtitle-style", default="")
    plan.add_argument("--style", choices=["LIMPO E NATURAL", "DINÂMICO", "AGRESSIVO", "DOCUMENTAL"], default="LIMPO E NATURAL")

    args = parser.parse_args()
    if args.command == "setup":
        Path(args.output_dir).expanduser().resolve().mkdir(parents=True, exist_ok=True)
        return assert_setup(args.video_use_path)
    if args.command == "plan":
        return create_job(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
