import subprocess
import sys

def run(cmd, silent=False):
    try:
        if silent:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f" Ошибка при выполнении: {cmd}")
                print(result.stdout)
                print(result.stderr)
                sys.exit(1)
        else:
            subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\nОстановлено пользователем")
        sys.exit(0)

def main():
    python = sys.executable

    print("Устанавливаем зависимости... ")
    sys.stdout.flush()
    run(f"{python} -m pip install -r requirements.txt", silent=True)

    print("Выполняем миграции...")
    run(f"{python} manage.py migrate")

    print("Запускаем сервер...")
    run(f"{python} manage.py runserver")


if __name__ == "__main__":
    main()
