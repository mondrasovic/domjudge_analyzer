#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Milan Ondrašovič <milan.ondrasovic@gmail.com>

import sys
import click
import tabulate
import configparser

from typing import Optional, Iterable, Any

from domjudge import DOMJudgeManager
from presenter import get_presenter


################################################################################
@click.command(context_settings={'ignore_unknown_options': True})
@click.option("-s","--server", help="DOMjudge server base URL.")
@click.option("-u", "--username", help="DOMjudge server user name.")
@click.option("-p", "--passwd", help="User name password.")
@click.option(
    "--get-contests", is_flag=True, help="Print a list of all contests.")
@click.option(
    "--get-teams", type=int,
    help="Print a list of all teams for the given contest specified by ID.")
@click.option(
    "--get-problems", type=int,
    help="Print a list of all problems for the given contest specified by ID.")
@click.option(
    "--submissions-dir-path", type=click.Path(),
    help="Directory path to download submission source files to.")
@click.option(
    "-v", "--verbose", is_flag=True, show_default=True,
    help="Activate verbose mode.")
def main(
        server: str, username: Optional[str], passwd: Optional[str],
        get_contests: bool, get_teams: Optional[int],
        get_problems: Optional[int], submissions_dir_path: click.Path,
        verbose: bool) -> int:
    if any(param is None for param in (server, username, passwd)):
        cfg = configparser.ConfigParser()
        cfg.read("config.cfg")
        
        server = server or cfg.get('server', 'base_url')
        username = username or cfg.get('login', 'username')
        passwd = passwd or cfg.get('login', 'password')
    
    dj_man = DOMJudgeManager(server, username, passwd)
    
    if get_contests:
        print_items(dj_man.get_contests())
    if get_teams:
        print_items(dj_man.get_teams(get_teams))
    if get_problems:
        print_items(dj_man.get_problems(get_problems))
    
    if submissions_dir_path:
        pass
    
    return 0


################################################################################
def print_items(items: Iterable[Any]) -> None:
    rows = []
    presenter = None
    
    for item in items:
        presenter = presenter or get_presenter(item.__class__)
        rows.append(presenter.get_row_data(item))
    
    if presenter:
        headers = tuple(map(str.upper, presenter.get_headers()))
        print(tabulate.tabulate(rows, headers=headers))
    else:
        print("No results retrieves.")


################################################################################
if __name__ == '__main__':
    sys.exit(main())
