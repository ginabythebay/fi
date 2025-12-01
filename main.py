import sys

import click

import time

from pathlib import Path
from datetime import date, datetime, timedelta, timezone

from typing import Iterable, Tuple, Optional, Callable

PDF_DIR = '~/Downloads'
DST_DIR = '~/gdrive/finances/filed'

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


def die(msg: str) -> None:
    click.echo(click.style(msg, fg='red'), err=True)
    sys.exit(1)


@click.command()
@click.option('--days', default=1, type=click.IntRange(1))
@click.option('--skip_invalid_names', '-s', is_flag=True)
@click.option('--force', '-f', is_flag=True)
def main(days: int, skip_invalid_names: bool, force: bool) -> None:
    file_root = Path(DST_DIR).expanduser()
    if not file_root.is_dir():
        die(f'{file_root} does not exist')
    click.echo(click.style('Hello from fi!', fg='blue'))
    pdfs = list(src_pdfs(PDF_DIR, days))
    check_all_pdf_names(pdfs, skip_invalid_names, die)
    missing_dirs = check_all_dests(file_root, pdfs, force, die)
    for d in missing_dirs:
        d.mkdir()
    check_all_dests(file_root, pdfs, force, die)


def check_all_dests(file_root: Path, pdfs: Iterable[Path], force: bool, die_fn: Callable[[str], None]) -> None:
    all_missing = set()
    for p in pdfs:
        _, sender = is_src_name(p.stem)
        dest = file_root / sender
        if not dest.is_dir():
            all_missing.add(dest)
    if not all_missing:
        return

    all_missing = sorted(all_missing)
    if force:
        for m in all_missing:
            click.echo(f'creating {m}')
            m.mkdir()
    else:
        for m in all_missing:
            click.echo('missing destination directory ' + click.style(m, fg='red'), err=True)
        click.echo('\n', err=True)
        die_fn('to automatically create missing directories use the --force option')


def check_all_pdf_names(pdfs: Iterable[Path], skip_invalid_names: bool, die_fn: Callable[[str], None]) -> None:
    invalid_name_cnt = 0
    for p in pdfs:
        year, sender = is_src_name(p.stem)
        if year:
            print(f'{p} -> {year}/{sender}')
        if not year:
            click.echo(click.style(f'unexpected file [{p}]', fg='red'), err=True)
            invalid_name_cnt += 1
    if invalid_name_cnt and not skip_invalid_names:
        files = 'file' if invalid_name_cnt == 1 else 'files'
        die_fn(f'found {invalid_name_cnt} unexpected {files}.  To continue, use the --skip_invalid_names option')


if __name__ == "__main__":
    main()
