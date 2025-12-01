import click

import time

from pathlib import Path
from datetime import date, datetime, timedelta, timezone

from typing import Iterable, Tuple, Optional

PDF_DIR = '~/Downloads'


def candidate_pdf(c: Path, earliest: float) -> bool:
    if c.suffix != '.pdf':
        return False
    return c.stat().st_mtime >= earliest


def src_pdfs(dir: str, days: int) -> Iterable[Path]:
    earliest = oldest_timestamp(days, time.time())
    d = Path(dir).expanduser()
    return [
        c for c in d.iterdir()
        if candidate_pdf(c, earliest)
    ]


def is_src_name(name: str) -> Tuple[Optional[int], Optional[str]]:
    d, _, rest = name.partition('_')
    if not rest:
        return None, None
    if len(d) != 8:
        return None, None
    if not d.isdigit():
        return None, None
    year = int(d[:4])
    if year < 1900:
        return None, None
    month = int(d[4:6])
    if month < 1 or month > 12:
        return None, None
    day = int(d[6:8])
    if day < 1 or day > 31:
        return None, None
    sender, _, rest = rest.partition('_')
    return year, sender


def oldest_timestamp(days: int, now: float) -> float:
    # https://stackoverflow.com/a/39079819
    tz = datetime.now(timezone.utc).astimezone().tzinfo
    today = date.fromtimestamp(now)
    earliest_date = today - timedelta(days=days-1)
    return datetime.combine(earliest_date, datetime.min.time(), tzinfo=tz).timestamp()


@click.command()
@click.option('--days', default=1, type=click.IntRange(1))
def main(days):
    print("Hello from fi!")
    for p in src_pdfs(PDF_DIR, days):
        year, sender = is_src_name(p.stem)
        if year:
            print(f'{p} -> {year}/{sender}')
        if not year:
            print(f'*** unexpected file [{p}]')
        


if __name__ == "__main__":
    main()
