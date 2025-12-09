#!/usr/bin/env -S uv run --script

import dataclasses
import sys

import click

import time

from pathlib import Path
from datetime import date, datetime, timedelta, timezone

from typing import Iterable, Optional, Callable, List

PDF_DIR = '~/Downloads'
DST_DIR = '~/gdrive/finances/filed'

@dataclasses.dataclass(frozen=True)
class SrcPdf:
    pdf: Path
    sender: str
    year: int

def candidate_pdf(c: Path, earliest: float) -> bool:
    suffix = c.suffix.lower()
    if suffix != '.pdf':
        return False
    return c.stat().st_mtime >= earliest

def file_cnt(cnt) -> str:
    return '1 file' if cnt == 1 else '%d files' % cnt


def src_pdfs(dir: str, days: int) -> Iterable[SrcPdf]:
    earliest = oldest_timestamp(days, time.time())
    d = Path(dir).expanduser()
    result: List[SrcPdf] = []
    for c in d.iterdir():
        if not candidate_pdf(c, earliest):
            continue
        p = is_src(c)
        if p:
            result.append(p)
    return result


def is_src(pdf: Path) -> Optional[SrcPdf]:
    name = pdf.stem
    d, _, rest = name.partition('_')
    if not rest:
        return None
    if len(d) != 8:
        return None
    if not d.isdigit():
        return None
    year = int(d[:4])
    if year < 1900:
        return None
    month = int(d[4:6])
    if month < 1 or month > 12:
        return None
    day = int(d[6:8])
    if day < 1 or day > 31:
        return None
    sender, _, rest = rest.partition('_')
    return SrcPdf(pdf, sender, year)


def oldest_timestamp(days: int, now: float) -> float:
    # https://stackoverflow.com/a/39079819
    tz = datetime.now(timezone.utc).astimezone().tzinfo
    today = date.fromtimestamp(now)
    earliest_date = today - timedelta(days=days-1)
    return datetime.combine(earliest_date, datetime.min.time(), tzinfo=tz).timestamp()


def die(msg: str) -> None:
    click.echo(click.style(msg, fg='red'), err=True)
    sys.exit(1)


def mkdir_dryrun(new_dir: Path) -> None:
    click.echo(f'would create {new_dir}')


def mv_dryrun(src_pdf: Path, dest_dir: Path) -> None:
    click.echo(f'would move {src_pdf} -> {dest_dir / src_pdf.name}')


def mkdir_real(new_dir: Path) -> None:
    click.echo(f'making {new_dir}')
    new_dir.mkdir()


def mv_real(src_pdf: Path, dest_dir: Path) -> None:
    click.echo(f'moving {src_pdf} -> {dest_dir / src_pdf.name}')
    src_pdf.rename(dest_dir / src_pdf.name)


@dataclasses.dataclass(frozen=True)
class Filer:
    mkdir_fn: Callable[[Path], None]
    mv_fn: Callable[[Path, Path], None]


@click.command()
@click.option('--days', default=1, type=click.IntRange(1))
@click.option('--skip_invalid_names', '-s', is_flag=True)
@click.option('--force', '-f', is_flag=True)
@click.option('--dryrun', '-d', is_flag=True)
def main(days: int, skip_invalid_names: bool, force: bool, dryrun) -> None:
    start_time = time.time()
    filer = Filer(mkdir_dryrun, mv_dryrun) if dryrun else Filer(mkdir_real, mv_real)
    file_root = Path(DST_DIR).expanduser()
    if not file_root.is_dir():
        die(f'{file_root} does not exist')
    click.echo(click.style('Hello from fi!', fg='blue'))
    pdfs = list(src_pdfs(PDF_DIR, days))
    paths = [
        p.pdf for p in pdfs
    ]
    check_all_dests(file_root, pdfs, force, die, filer.mkdir_fn)
    for pdf in pdfs:
        dest = file_root / pdf.sender / str(pdf.year)
        if not dest.is_dir():
            filer.mkdir_fn(dest)
        filer.mv_fn(pdf.pdf, dest)
    elapsed_time = time.time() - start_time
    click.echo('\n')
    click.echo(f'moved {file_cnt(len(pdfs))} in {elapsed_time} seconds')


def check_all_dests(file_root: Path,
                    pdfs: Iterable[SrcPdf],
                    force: bool,
                    die_fn: Callable[[str], None],
                    mkdir_fn: Callable[[Path], None]) -> None:
    all_missing = set()
    for p in pdfs:
        dest = file_root / p.sender
        if not dest.is_dir():
            all_missing.add(dest)
    if not all_missing:
        return

    all_missing = sorted(all_missing)
    if force:
        for m in all_missing:
            mkdir_fn(m)
    else:
        for m in all_missing:
            click.echo('missing destination directory ' + click.style(m, fg='red'), err=True)
        click.echo('\n', err=True)
        die_fn('to automatically create missing directories use the --force option')


if __name__ == "__main__":
    main()
