#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Milan Ondrašovič <milan.ondrasovic@gmail.com>

import json
import base64
import pathlib
import requests
import dataclasses

from datetime import datetime
from typing import Optional, Iterator, Iterable, Any, Dict, Callable, Type, Set


################################################################################
import tqdm


def _field(
        field_type: Type[Any],
        header_name: Optional[str] = None) -> dataclasses.Field:
    metadata = {'header_name': header_name} if header_name else None
    return dataclasses.field(default_factory=field_type, metadata=metadata)


################################################################################
@dataclasses.dataclass(frozen=True)
class Contest:
    id: int = _field(int, 'id')
    long_name: str = _field(str, 'long name')
    short_name: str = _field(str, 'short name')
    start_time: datetime = _field(datetime)
    end_time: datetime = _field(datetime)
    
    @staticmethod
    def build_from_json(content: Dict) -> 'Contest':
        return Contest(
            content['id'],
            content['formal_name'],
            content['shortname'],
            datetime.fromisoformat(content['start_time']),
            datetime.fromisoformat(content['end_time']))


################################################################################
@dataclasses.dataclass(frozen=True)
class Team:
    id: int = _field(int, 'id')
    name: str = _field(str, 'name')
    
    @staticmethod
    def build_from_json(content: Dict) -> 'Team':
        return Team(content['id'], content['name'])


################################################################################
@dataclasses.dataclass(frozen=True)
class Problem:
    id: int = _field(int, 'id')
    long_name: str = _field(str, 'long name')
    short_name: str = _field(str, 'short name')
    
    @staticmethod
    def build_from_json(content: Dict) -> 'Problem':
        return Problem(content['id'], content['name'], content['short_name'])


################################################################################
@dataclasses.dataclass(frozen=True)
class Submission:
    id: int = _field(int, 'id')
    team_id: int = _field(int)
    team_name: int = _field(int, 'team name')
    problem_id: int = _field(int)
    problem_name: str = _field(str, 'problem name')
    language_id: str = _field(str, 'language')
    time: datetime = _field(datetime)
    max_run_time: float = _field(float, 'max. run time')
    judgement_type_id: str = _field(str, 'judgement')
    
    @staticmethod
    def build_from_json(content: Dict) -> 'Submission':
        return Submission(
            content['id'],
            content['team_id'],
            content['team_name'],
            content['problem_id'],
            content['problem_name'],
            content['language_id'],
            datetime.fromisoformat(content['time']),
            content['max_run_time'],
            content['judgement_type_id'])


################################################################################
@dataclasses.dataclass(frozen=True)
class SourceCode:
    id: int = _field(int, 'id')
    submission_id: int = _field(int, 'submission id')
    source_code: str = _field(str)
    
    @staticmethod
    def build_from_json(content: Dict) -> 'SourceCode':
        return SourceCode(
            content['id'],
            content['submission_id'],
            base64.b64decode(
                content['source']).decode('utf-8').replace("\r\n", "\n"))


################################################################################
def _build_index(
        instances: Iterable[Any],
        key: Callable[[Any], Any] = lambda x: x.id) -> Dict:
    return {key(inst):inst for inst in instances}


################################################################################
class DOMJudgeManager:
    def __init__(
            self, base_url: str, username: Optional[str] = None,
            password: Optional[str] = None,
            teams_subset: Optional[Iterable[str]] = None) -> None:
        self.base_url: str = base_url
        self.auth: Optional[requests.auth.HTTPBasicAuth] = None
        
        if teams_subset:
            self.teams_subset: Optional[Set[str]] = set(teams_subset)
        
        if None not in (username, password):
            self.auth = requests.auth.HTTPBasicAuth(username, password)
    
    def get_contests(self) -> Iterator[Contest]:
        url = self._build_api_url('contests')
        yield from self._yield_content_as_inst(url, Contest.build_from_json)
    
    def get_teams(self, contest_id: int) -> Iterator[Team]:
        url = self._build_api_url('contests', contest_id, 'teams')
        yield from self._yield_content_as_inst(url, Team.build_from_json)
    
    def get_problems(self, contest_id: int) -> Iterator[Problem]:
        url = self._build_api_url('contests', contest_id, 'problems')
        yield from self._yield_content_as_inst(url, Problem.build_from_json)
    
    def get_submissions(self, contest_id: int) -> Iterator[Submission]:
        submissions_url = self._build_api_url(
            'contests', contest_id, 'submissions')
        judgements_url = self._build_api_url(
            'contests', contest_id, 'judgements')
        
        teams = _build_index(self.get_teams(contest_id))
        problems = _build_index(self.get_problems(contest_id))
        
        judgements = self._get_url_content(judgements_url)
        submission_to_judgement = _build_index(
            judgements, lambda x: x['submission_id'])
        relevant_keys = ('max_run_time', 'judgement_type_id')
        
        def _build_submission_with_judgement(content: Dict) -> Submission:
            submission_id = content['id']
            judgement = submission_to_judgement[submission_id]
            judgement_content = {k:judgement[k] for k in relevant_keys}
            
            team_name = teams[content['team_id']].name
            problem_short_name = problems[content['problem_id']].short_name
            
            content_expanded = {
                **content, **judgement_content,
                **{'team_name': team_name, 'problem_name': problem_short_name}}
            
            return Submission.build_from_json(content_expanded)
        
        yield from self._yield_content_as_inst(
            submissions_url, _build_submission_with_judgement)
    
    def get_source_code(
            self, contest_id: int, submission_id: int) -> SourceCode:
        url = self._build_api_url(
            'contests', contest_id, 'submissions', submission_id, 'source-code')
        return next(
            self._yield_content_as_inst(url, SourceCode.build_from_json))
        
    def download_submission_files(
            self, contest_id: int, output_dir_path: str,
            verbose: bool = False) -> None:
        teams = _build_index(self.get_teams(contest_id))
        problems = _build_index(self.get_problems(contest_id))
        
        output_dir = pathlib.Path(output_dir_path)
        
        submissions = self.get_submissions(contest_id)
        if verbose:
            submissions = tqdm.tqdm(submissions, desc="downloading submissions")
        
        for submission in submissions:
            problem = problems[submission.problem_id]
            team = teams[submission.team_id]
            source_code = self.get_source_code(contest_id, submission.id)
            
            output_file_path = (
                    output_dir /
                    problem.short_name /
                    f"{team.name}_{submission.id}_"
                    f"{submission.judgement_type_id}.{submission.language_id}")
            
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            output_file_path.write_text(
                source_code.source_code, encoding='utf-8')
    
    def _build_api_url(self, *args) -> str:
        return self.base_url + '/'.join(map(str, args))

    def _yield_content_as_inst(self, url, inst_builder) -> Iterator[Any]:
        content = self._get_url_content(url)
        yield from map(inst_builder, content)

    def _get_url_content(self, url) -> Dict:
        content = requests.get(url, auth=self.auth).content
        return json.loads(content.decode('utf-8'))
