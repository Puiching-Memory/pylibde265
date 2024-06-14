from typing import Generator

def get_version() -> str: ...

class pylibde265_decoder:
    def __init__(self, thread_number: int) -> None: ...
    def decode(self) -> Generator[dict, None, None]:
        yield
