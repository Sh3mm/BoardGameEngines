#! python3
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

parser = argparse.ArgumentParser()

parser.add_argument("GameName", help="name of the new board game")
parser.add_argument("--templates", "-t", default="templates/", help="the template folder")


def main(args: argparse.Namespace):
    name = args.GameName

    if Path(f"GameEngines/{name}").exists() or Path(f"src/{name}.rs").exists():
        raise FileExistsError("The Game already exists")

    python_templates = Path(args.templates) / "PythonGame"
    rust_templates = Path(args.templates) / "RustGame"

    # python template
    python_engine(name, python_templates)

    # rust template
    rust_engine(name, rust_templates)


def python_engine(name: str, python_templates):
    env = Environment(loader=FileSystemLoader(python_templates))
    for path in env.list_templates():
        template = env.get_template(path)
        result = template.render(GameName=name)

        out_file = (Path("GameEngines") / name / path[:-3].format(GameName=name))
        out_file.parent.mkdir(exist_ok=True, parents=True)
        out_file.write_text(result)


def rust_engine(name: str, rust_templates):
    env = Environment(loader=FileSystemLoader(rust_templates))
    template = env.get_template("RustGame.rs.j2")
    result = template.render(GameName=name)

    out_file = (Path("src") / f"{name}.rs")
    out_file.parent.mkdir(exist_ok=True, parents=True)
    out_file.write_text(result)


if __name__ == '__main__':
    main(args=parser.parse_args())