import subprocess
import sys


def run(cmd):
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nОстановлено пользователем")
        sys.exit(0)


def main():
    python = sys.executable

    print("Устанавливаем зависимости...")
    run(f"{python} -m pip install -r requirements.txt")

    print("Выполняем миграции...")
    run(f"{python} manage.py migrate")

    print("Запускаем сервер...")
    run(f"{python} manage.py runserver")


if __name__ == "__main__":
    main()
