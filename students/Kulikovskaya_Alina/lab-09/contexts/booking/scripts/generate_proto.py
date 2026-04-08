"""
Генерация Python кода из .proto файлов.
"""

import subprocess
import sys
from pathlib import Path


PROTO_DIR = Path("shared/protobuf")
OUT_DIR = Path("src/generated")
PROTOC = "python -m grpc_tools.protoc"


def generate():
    """Генерация gRPC кода."""
    
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    proto_files = list(PROTO_DIR.glob("*.proto"))
    
    for proto_file in proto_files:
        print(f"Генерация {proto_file.name}...")
        
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"--proto_path={PROTO_DIR}",
            f"--python_out={OUT_DIR}",
            f"--grpc_python_out={OUT_DIR}",
            str(proto_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Ошибка: {result.stderr}")
            return False
    
    # Создаём __init__.py для пакетов
    for subdir in OUT_DIR.rglob("*"):
        if subdir.is_dir():
            (subdir / "__init__.py").touch()
    
    # Фиксим импорты (относительные → абсолютные)
    fix_imports()
    
    print("Генерация завершена!")
    return True


def fix_imports():
    """Исправление импортов в сгенерированных файлах."""
    
    for py_file in OUT_DIR.rglob("*_pb2*.py"):
        content = py_file.read_text()
        
        # Заменяем относительные импорты на абсолютные
        content = content.replace(
            "from common import",
            "from generated.common import"
        )
        content = content.replace(
            "import common_pb2",
            "from generated import common_pb2"
        )
        
        py_file.write_text(content)


if __name__ == "__main__":
    generate()