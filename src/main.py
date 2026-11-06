import argparse
import sys


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


def main() -> None:
    """Главная функция запуска прототипа с обработкой ошибок."""
    parser = get_arg_parser()
    try:
        # Пытаемся распарсить переданные аргументы
        args = parser.parse_args()
        print_config(args)
    except SystemExit as err:
        # Демонстрация перехвата и обработки ошибок ввода
        print(f"Ошибка ввода параметров. Убедитесь, что переданы все флаги.", file=sys.stderr)
        sys.exit(err.code)


if __name__ == "__main__":
    main()