from os import name
import sys
from typing import Sequence
from serv import Serv
from sdk.__main__ import Test
from schema_entry import EntryPoint


def main(argv: Sequence[str]) -> None:
    app = EntryPoint(name="echo")
    app.regist_sub(Serv)
    app.regist_sub(Test)
    app(argv)


if __name__ == "__main__":
    main(sys.argv[1:])
