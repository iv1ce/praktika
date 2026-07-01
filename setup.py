import os
import secrets
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"


def prompt(question: str, default: str = "") -> str:
    if default:
        val = input(f"{question} [{default}]: ").strip()
        return val or default
    return input(f"{question}: ").strip()


def write_env(vars: dict):
    content = "\n".join(f"{k}={v}" for k, v in vars.items()) + "\n"
    ENV_PATH.write_text(content, encoding="utf-8")
    print(f"\n[OK] .env сохранён")


def db_exists(host, port, user, password, db_name):
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=db_name
        )
        conn.close()
        return True
    except Exception:
        return False


def create_db(host, port, user, password, db_name):
    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f'CREATE DATABASE "{db_name}"')
        cur.close()
        conn.close()
        print(f"[OK] База '{db_name}' создана")
    except Exception as e:
        print(f"[WARN] Не удалось создать БД: {e}")


def detect_pg() -> dict | None:
    """Пробует подключиться с дефолтными параметрами."""
    defaults = [
        {"DB_HOST": "localhost", "DB_PORT": "5432", "DB_USER": "postgres", "DB_PASSWORD": "", "DB_NAME": "praktika"},
        {"DB_HOST": "localhost", "DB_PORT": "5432", "DB_USER": "postgres", "DB_PASSWORD": "postgres", "DB_NAME": "praktika"},
    ]
    for cfg in defaults:
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=cfg["DB_HOST"], port=cfg["DB_PORT"],
                user=cfg["DB_USER"], password=cfg["DB_PASSWORD"],
                dbname=cfg["DB_NAME"]
            )
            conn.close()
            return cfg
        except Exception:
            try:
                conn = psycopg2.connect(
                    host=cfg["DB_HOST"], port=cfg["DB_PORT"],
                    user=cfg["DB_USER"], password=cfg["DB_PASSWORD"],
                    dbname="postgres"
                )
                conn.close()
                return cfg
            except Exception:
                continue
    return None


def main():
    print("=== Настройка подключения к БД ===\n")
    print("Оставь поля пустыми — будет SQLite (файл praktika.db)\n")

    env = {}
    env["SECRET_KEY"] = secrets.token_urlsafe(32)

    detected = detect_pg()
    if detected:
        use_pg = input(f"Найден PostgreSQL на {detected['DB_HOST']}:{detected['DB_PORT']}. Использовать? (Y/n): ").strip().lower()
        if use_pg != "n":
            env.update(detected)
            write_env(env)
            print("\nСоздаю таблицы...")
            os.chdir(BASE_DIR)
            subprocess.check_call(
                [sys.executable, "-c",
                 "from app.models import User, Task; "
                 "from app.database import Base, engine; "
                 "Base.metadata.create_all(bind=engine); "
                 "print('[OK] Таблицы созданы')"]
            )
            print("\n[OK] Готово! Запускай: python -m app.main")
            print("   http://127.0.0.1:8000")
            return

    use_pg = input("Использовать PostgreSQL? (y/N): ").strip().lower()

    if use_pg == "y":
        env["DB_HOST"] = prompt("Хост (если не знаешь — localhost)", "localhost")
        env["DB_PORT"] = prompt("Порт", "5432")
        env["DB_USER"] = prompt("Пользователь", "postgres")
        env["DB_PASSWORD"] = prompt("Пароль (если нет — просто Enter)", "")
        env["DB_NAME"] = prompt("Имя БД", "praktika")

        write_env(env)

        try:
            import psycopg2
        except ImportError:
            print("Устанавливаю psycopg2...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "psycopg2-binary"]
            )

        if not db_exists(
            env["DB_HOST"], env["DB_PORT"], env["DB_USER"],
            env["DB_PASSWORD"], env["DB_NAME"]
        ):
            print(f"\nБаза '{env['DB_NAME']}' не найдена.")
            if input("Создать? (Y/n): ").strip().lower() != "n":
                create_db(
                    env["DB_HOST"], env["DB_PORT"], env["DB_USER"],
                    env["DB_PASSWORD"], env["DB_NAME"]
                )

        print("\nСоздаю таблицы...")
        os.chdir(BASE_DIR)
        subprocess.check_call(
            [sys.executable, "-c",
             "from app.models import User, Task; "
             "from app.database import Base, engine; "
             "Base.metadata.create_all(bind=engine); "
             "print('[OK] Таблицы созданы')"]
        )
    else:
        write_env(env)

    print("\n[OK] Готово! Запускай: python -m app.main")
    print(f"   http://127.0.0.1:8000")


if __name__ == "__main__":
    main()
