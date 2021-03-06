#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Milan Ondrašovič <milan.ondrasovic@gmail.com>

import pathlib
import sys
import csv
import click
import tabulate
import dataclasses
import configparser

from typing import Optional, Iterable, Any

from domjudge import DOMJudgeManager


################################################################################
@click.command(context_settings={'ignore_unknown_options': True})
@click.option("-s","--server", help="DOMjudge server base URL.")
@click.option("-u", "--username", help="DOMjudge server user name.")
@click.option("-p", "--passwd", help="User name password.")
@click.option(
    "--teams-subset-file-path", type=click.Path(),
    help="a *.txt file where each line contains a team name that will not be "
         "filtered from reports.")
@click.option(
    "--get-contests", is_flag=True, help="Print a list of all contests.")
@click.option(
    "-c", "--contest", type=int,
    help="Apply commands to the given contest specified by ID.")
@click.option(
    "--get-teams", is_flag=True,
    help="Print a list of teams for the given contest specified by ID.")
@click.option(
    "--get-problems", is_flag=True,
    help="Print a list of problems for the given contest specified by ID.")
@click.option(
    "--get-submissions", is_flag=True,
    help="Print a list of submissions for the given contest specified by ID.")
@click.option(
    "--submissions-dir-path", type=click.Path(),
    help="Directory path to download submission source files to.")
@click.option(
    "--csv-file-path", type=click.Path(),
    help="save the table content to a CSV file.")
@click.option(
    "-v", "--verbose", is_flag=True, show_default=True,
    help="Activate verbose mode.")
def main(
        server: str, username: Optional[str], passwd: Optional[str],
        teams_subset_file_path: Optional[str], get_contests: bool,
        contest: Optional[int], get_teams: bool, get_problems: bool,
        get_submissions: bool, submissions_dir_path: click.Path,
        csv_file_path: click.Path, verbose: bool) -> int:
    teams_subset = None
    cfg_params = (server, username, passwd, teams_subset_file_path)
    
    if any(param is None for param in cfg_params):
        cfg = configparser.ConfigParser(allow_no_value=True)
        cfg.read("config.cfg")
        
        server = server or cfg.get('server', 'base_url')
        username = username or cfg.get('login', 'username')
        passwd = passwd or cfg.get('login', 'password')
        
        teams_subset_file_path = teams_subset_file_path or cfg.get(
            'data', 'teams_subset_file_path')
        if teams_subset_file_path:
            teams_subset = _read_teams_subset(teams_subset_file_path)
    
    dj_man = DOMJudgeManager(server, username, passwd, teams_subset)
    
    csv_file_path = str(csv_file_path) if csv_file_path else csv_file_path
    
    if get_contests:
        _print_table(dj_man.get_contests(), csv_file_path)
    
    if get_teams:
        _assure_contest_is_set('--get-teams', contest)
        _print_table(dj_man.get_teams(contest), csv_file_path)
    if get_problems:
        _assure_contest_is_set('--get-problems', contest)
        _print_table(dj_man.get_problems(contest), csv_file_path)
    if get_submissions:
        _assure_contest_is_set('--get-submissions', contest)
        _print_table(dj_man.get_submissions(contest), csv_file_path)
    
    if submissions_dir_path:
        _assure_contest_is_set('--submissions-dir-path', contest)
        dj_man.download_submission_files(
            contest, str(submissions_dir_path), verbose)
    
    return 0


################################################################################
def _assure_contest_is_set(option_name: str, contest: Optional[int]) -> None:
    if contest is None:
        raise click.BadOptionUsage(
            option_name=option_name,
            message=f"the {option_name} option may only be used with a "
                    f"specific contest provided by -c, --contest")


################################################################################
def _get_printable_fields(item) -> Iterable[dataclasses.Field]:
    return (
        field
        for field in dataclasses.fields(item)
        if field.metadata and ('header_name' in field.metadata))


################################################################################
def _print_table(
        items: Iterable[Any], csv_file_path: Optional[str] = None) -> None:
    rows, headers = [], []
    
    for i, item in enumerate(items):
        row_data = []
        for field in _get_printable_fields(item):
            if field.metadata:
                if i == 0:
                    headers.append(field.metadata['header_name'].upper())
                val = getattr(item, field.name)
                row_data.append(val)
        rows.append(row_data)
    
    if headers:
        print(tabulate.tabulate(rows, headers=headers))
    else:
        print("No results retrieved.")
    
    if csv_file_path is not None:
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            row_dicts = (dict(zip(headers, row)) for row in rows)
            writer.writeheader()
            writer.writerows(row_dicts)


################################################################################
def _read_teams_subset(file_path):
    lines = map(str.strip, pathlib.Path(file_path).read_text().splitlines())
    return tuple(line for line in lines if len(line) > 0)


################################################################################
if __name__ == '__main__':
    sys.exit(main())
