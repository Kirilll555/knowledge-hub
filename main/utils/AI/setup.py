""" Скачивает готовую модель ИИ """
from pathlib import Path
from huggingface_hub import hf_hub_download, login



HF_TOKEN = "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"
login(token=HF_TOKEN)

REPO_ID = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
FILENAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"


def main():
    """ Выполнение выше поставленной задачи """
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    target_dir = models_dir / REPO_ID.split("/")[-1]
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Скачивание {REPO_ID} / {FILENAME}...")
    hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        local_dir=str(target_dir),
    )
    print(f"Модель сохранена: {target_dir / FILENAME}")


if __name__ == "__main__":
    main()
