import argparse
import sys
import json
import urllib.request
from urllib.error import URLError, HTTPError
from typing import List


def get_arg_parser() -> argparse.ArgumentParser:
    """Создает и настраивает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Анализатор графа зависимостей Cargo.")
    parser.add_argument("package", help="Имя анализируемого пакета")
    parser.add_argument("--repo", required=True, help="URL или путь к репозиторию")
    parser.add_argument("--version", required=True, help="Версия пакета")
    parser.add_argument("--test-mode", action="store_true", help="Включить тестовый режим")
    parser.add_argument("--ascii", action="store_true", help="Вывод в формате ASCII-дерева")
    return parser


def print_config(args: argparse.Namespace) -> None:
    """Выводит настраиваемые параметры в формате ключ-значение."""
    print("--- Текущая конфигурация ---")
    print(f"Имя пакета: {args.package}")
    print(f"Путь/URL к репозиторию: {args.repo}")
    print(f"Версия пакета: {args.version}")
    print(f"Тестовый режим: {args.test_mode}")
    print(f"ASCII вывод: {args.ascii}")
    print("----------------------------\n")


def get_direct_dependencies(repo: str, pkg: str, ver: str) -> List[str]:
    """Получает прямые зависимости конкретной версии пакета через API."""
    url = f"{repo}/{pkg}/{ver}/dependencies"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            # В API crates.io зависимости лежат в массиве dependencies
            return [dep["crate_id"] for dep in data.get("dependencies", [])]
    except HTTPError as err:
        print(f"Ошибка HTTP {err.code}: Не удалось найти пакет {pkg} v{ver}.")
        return []
    except URLError as err:
        print(f"Ошибка сети: {err.reason}.")
        return []
    except json.JSONDecodeError:
        print("Ошибка обработки данных (неверный JSON).")
        return []


def main() -> None:
    """Главная функция запуска приложения с получением зависимостей."""
    parser = get_arg_parser()
    try:
        args = parser.parse_args()
        print_config(args)
        
        # Получение и вывод зависимостей для 2 этапа
        print(f"Прямые зависимости пакета {args.package} (v{args.version}):")
        dependencies = get_direct_dependencies(args.repo, args.package, args.version)
        
        if dependencies:
            for dep in dependencies:
                print(f"- {dep}")
        else:
            print("Прямых зависимостей нет, или пакет не найден.")
            
    except SystemExit as err:
        print("Ошибка ввода параметров. Убедитесь, что переданы все флаги.", file=sys.stderr)
        sys.exit(err.code)


if __name__ == "__main__":
    main()