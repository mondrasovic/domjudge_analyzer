#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Milan Ondrašovič <milan.ondrasovic@gmail.com>

import abc

from typing import Any, Sequence, Type, cast

from domjudge import Contest, Team, Problem, Submission


################################################################################
_presenters_registry = {}


################################################################################
def _register_presenter(
        inst_type: Type[Any], presenter: Type['TablePresenter']) -> None:
    _presenters_registry[inst_type] = presenter


################################################################################
def get_presenter(inst_type: Type[Any]) -> 'TablePresenter':
    klass = _presenters_registry[inst_type]
    return cast(TablePresenter, klass())


################################################################################
class TablePresenter(abc.ABC):
    
    def __init_subclass__(cls, inst_type, **kwargs):
        super().__init_subclass__(**kwargs)
        _register_presenter(inst_type, cls)
    
    @abc.abstractmethod
    def get_headers(self) -> Sequence[str]:
        pass
    
    @abc.abstractmethod
    def get_row_data(self, inst: Any) -> Sequence[Any]:
        pass


################################################################################
class ContestPresenter(TablePresenter, inst_type=Contest):
    def get_headers(self) -> Sequence[str]:
        return ['ID', 'long name', 'short name']

    def get_row_data(self, inst: Contest) -> Sequence[Any]:
        return [inst.id, inst.long_name, inst.short_name]


################################################################################
class TeamPresenter(TablePresenter, inst_type=Team):
    def get_headers(self) -> Sequence[str]:
        return ['ID', 'name']

    def get_row_data(self, inst: Team) -> Sequence[Any]:
        return [inst.id, inst.name]


################################################################################
class SubmissionPresenter(TablePresenter, inst_type=Submission):
    def get_headers(self) -> Sequence[str]:
        return ['ID', 'language', 'max. run time', 'judgement']

    def get_row_data(self, inst: Submission) -> Sequence[Any]:
        return [
            inst.id, inst.language_id, inst.max_run_time,
            inst.judgement_type_id]


################################################################################
class ProblemPresenter(TablePresenter, inst_type=Problem):
    def get_headers(self) -> Sequence[str]:
        return ['ID', 'long name', 'short name']

    def get_row_data(self, inst: Problem) -> Sequence[Any]:
        return [inst.id, inst.long_name, inst.short_name]

