def get_version() -> str: ...

class decoder:
    w: int
    h: int
    chroma: int
    bps: int
    pts: int
    ttd_max: int
    ttd: int
    
    wC: int
    hC: int

    def __init__(self, threads: int, buffer_size: int) -> None: ...
    def load(self, vedio_path: str) -> int: ...
    def decode(self) -> None: ...
    def free_image(self) -> None: ...
