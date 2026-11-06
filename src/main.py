import argparse
import sys
import json
import urllib.request
from urllib.error import URLError, HTTPError
from typing import List, Dict, Set, Tuple


def get_arg_parser() -> argparse.ArgumentParser:
    """Создает и настраивает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Анализатор графа Cargo.")
    parser.add_argument("package", help="Имя анализируемого пакета")
    parser.add_argument("--repo", required=True, help="URL или путь к репо")
    parser.add_argument("--version", required=True, help="Версия пакета")
    parser.add_argument("--test-mode", action="store_true", help="Тестовый режим")
    parser.add_argument("--ascii", action="store_true", help="ASCII-вывод")
    return parser


def get_test_deps(repo_path: str, pkg: str) -> List[str]:
    """Получает зависимости из тестового локального файла."""
    try:
        with open(repo_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            # В тестовом графе пакеты названы большими буквами
            return data.get(pkg.upper(), [])
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Ошибка файла: {repo_path}", file=sys.stderr)
        return []


def get_direct_deps(repo: str, pkg: str, ver: str, test_mode: bool) -> List[str]:
    """Получает прямые зависимости (сеть или тестовый файл)."""
    if test_mode:
        return get_test_deps(repo, pkg)
    
    url = f"{repo}/{pkg}/{ver}/dependencies"
    try:
        with urllib.request.urlopen(url) as res:
            data = json.loads(res.read().decode("utf-8"))
            deps = [dep["crate_id"] for dep in data.get("dependencies", [])]
            return list(set(deps))  # Убираем дубликаты
    except (HTTPError, URLError, json.JSONDecodeError):
        return []


def bfs_recursive(queue: List[Tuple[str, str]], graph: Dict[str, List[str]], 
                  visited: Set[str], repo: str, test_mode: bool) -> None:
    """Рекурсивный обход BFS для построения полного графа."""
    if not queue:
        return
        
    pkg, ver = queue.pop(0)
    
    if pkg in visited:
        bfs_recursive(queue, graph, visited, repo, test_mode)
        return
        
    visited.add(pkg)
    deps = get_direct_deps(repo, pkg, ver, test_mode)
    graph[pkg] = deps
    
    for dep in deps:
        if dep not in visited and dep not in [q[0] for q in queue]:
            # В реальности нужна точная версия, для графа передаем заглушку
            queue.append((dep, "1.0.0"))
            
    bfs_recursive(queue, graph, visited, repo, test_mode)


def main() -> None:
    """Главная функция приложения (Этап 3)."""
    parser = get_arg_parser()
    try:
        args = parser.parse_args()
        
        graph: Dict[str, List[str]] = {}
        visited: Set[str] = set()
        queue = [(args.package, args.version)]
        
        bfs_recursive(queue, graph, visited, args.repo, args.test_mode)
        
        print(f"--- Граф зависимостей {args.package} ---")
        print(json.dumps(graph, indent=2, ensure_ascii=False))
        
    except SystemExit as err:
        print("Ошибка ввода. Проверьте флаги.", file=sys.stderr)
        sys.exit(err.code)


if __name__ == "__main__":
    main()