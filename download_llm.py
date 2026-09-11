"""One-time LLM downloader using huggingface_hub (reliable, resumable)."""
from pathlib import Path
from huggingface_hub import hf_hub_download

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

# TinyLlama Q4 (~640 MB) - use the official repo
print("Downloading TinyLlama-1.1B-Chat Q4 (~640 MB) ...")
path = hf_hub_download(
    repo_id="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
    filename="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    local_dir=str(MODEL_DIR),
    local_dir_use_symlinks=False,
)
print(f"Saved: {path}")
print(f"Size: {Path(path).stat().st_size / 1024 / 1024:.1f} MB")
