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
            return data.get(pkg.upper(), [])
    except (FileNotFoundError, json.JSONDecodeError):
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
            return list(set(deps))
    except (HTTPError, URLError, json.JSONDecodeError):
        return []


def bfs_recursive(queue: List[Tuple[str, str]], graph: Dict[str, List[str]], 
                  visited: Set[str], order: List[str], repo: str, test_mode: bool) -> None:
    """Рекурсивный обход BFS для построения полного графа."""
    if not queue:
        return
        
    pkg, ver = queue.pop(0)
    
    if pkg in visited:
        bfs_recursive(queue, graph, visited, order, repo, test_mode)
        return
        
    visited.add(pkg)
    order.append(pkg)
    deps = get_direct_deps(repo, pkg, ver, test_mode)
    graph[pkg] = deps
    
    for dep in deps:
        if dep not in visited and dep not in [q[0] for q in queue]:
            queue.append((dep, "1.0.0"))
            
    bfs_recursive(queue, graph, visited, order, repo, test_mode)


def print_d2_graph(graph: Dict[str, List[str]]) -> None:
    """Выводит граф в формате языка диаграмм D2 на экран."""
    print("\n--- Код для диаграммы D2 (Этап 5) ---")
    for pkg, deps in graph.items():
        if not deps:
            print(f"{pkg}")
        for dep in deps:
            print(f"{pkg} -> {dep}")
    print("-------------------------------------\n")


def print_ascii_tree(graph: Dict[str, List[str]], node: str, prefix: str, 
                     visited: Set[str]) -> None:
    """Рекурсивно выводит ASCII-дерево зависимостей."""
    if node in visited:
        print(prefix + f"└── {node} (уже в дереве/цикл)")
        return
        
    visited.add(node)
    print(prefix + f"└── {node}")
    deps = graph.get(node, [])
    
    for i, dep in enumerate(deps):
        is_last = (i == len(deps) - 1)
        next_prefix = prefix + ("    " if is_last else "│   ")
        print_ascii_tree(graph, dep, next_prefix, visited.copy())


def main() -> None:
    """Главная функция приложения."""
    parser = get_arg_parser()
    try:
        args = parser.parse_args()
        
        graph: Dict[str, List[str]] = {}
        visited: Set[str] = set()
        order: List[str] = []
        queue = [(args.package, args.version)]
        
        # Строим граф
        bfs_recursive(queue, graph, visited, order, args.repo, args.test_mode)
        
        # Вывод порядка (Этап 4)
        print(f"Порядок загрузки пакетов:")
        print(" -> ".join(order))
        
        # Вывод диаграммы D2 (Этап 5)
        print_d2_graph(graph)
        
        # Вывод ASCII-дерева (Этап 5)
        if args.ascii:
            print("--- ASCII-дерево зависимостей ---")
            print_ascii_tree(graph, args.package, "", set())
            
    except SystemExit as err:
        sys.exit(err.code)


if __name__ == "__main__":
    main()