import sys
import logging
from pathlib import Path
from typing import Union

# Add src to sys.path so we can import from the source tree
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import click
import validators

from kodekloud_downloader.enums import Quality
from kodekloud_downloader.helpers import select_courses
from kodekloud_downloader.main import (
    download_course,
    download_quiz,
    parse_course_from_url,
)
from kodekloud_downloader.models.helper import collect_all_courses


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase log level verbosity")
def kodekloud(verbose):
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    if verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)


@kodekloud.command()
@click.argument("course_url", required=False)
@click.option(
    "--quality",
    "-q",
    default="1080p",
    type=click.Choice([quality.value for quality in Quality]),
    help="Quality of the video to be downloaded.",
)
@click.option(
    "--output-dir",
    "-o",
    default=Path.home() / "Downloads",
    help="Output directory where downloaded files will be store.",
)
@click.option(
    "--cookie",
    "-c",
    required=False,
    help="Cookie file. Course should be accessible via this.",
)
@click.option(
    "--token",
    "-t",
    required=False,
    help="Token authorization bearer token.",
)
@click.option(
    "--max-duplicate-count",
    "-mdc",
    default=3,
    type=int,
    help="If same video is downloaded this many times, then download stops",
)
@click.pass_context
def dl(
    ctx,
    course_url,
    quality: str,
    output_dir: Union[Path, str],
    cookie,
    token,
    max_duplicate_count: int,
):
    if not token and not cookie:
        raise click.UsageError(
            "You must provide either --token or --cookie for authentication."
        )

    if course_url is None:
        courses = collect_all_courses()
        selected_courses = select_courses(courses)
        for selected_course in selected_courses:
            download_course(
                course=selected_course,
                cookie=cookie,
                quality=quality,
                output_dir=output_dir,
                max_duplicate_count=max_duplicate_count,
                token=token,
            )
    elif validators.url(course_url):
        course_detail = parse_course_from_url(course_url)
        download_course(
            course=course_detail,
            cookie=cookie,
            quality=quality,
            output_dir=output_dir,
            max_duplicate_count=max_duplicate_count,
            token=token,
        )
    else:
        logging.error("Please enter a valid URL")
        SystemExit(1)


@kodekloud.command()
@click.option(
    "--output-dir",
    "-o",
    default=Path.home() / "Downloads",
    help="Output directory where quiz markdown file will be saved.",
)
@click.option(
    "--sep",
    is_flag=True,
    show_default=True,
    default=False,
    help="Write in seperate markdown files.",
)
def dl_quiz(output_dir: Union[Path, str], sep: bool):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    download_quiz(output_dir, sep)


if __name__ == "__main__":
    kodekloud()
