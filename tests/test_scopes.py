#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `scopes` package."""

import os

print(os.getenv('PYTHONPATH'))

import pytest

from click.testing import CliRunner

from scopes.tasks import tasks, bolt, spout, builder
from scopes.graph import G, build, topological_sort, traverse
from scopes import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'scopes.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


# t1---
# |   |
# v   v
# t2  t3
# \  /     t4
#  v       |
#  t5<----/


@pytest.fixture
def example():
    tasks.clear()
    G.clear()

    @spout({'x': None})
    def t1():
        yield {'x': 'east'}
        yield {'x': 'west'}


    @bolt({'y': None}, lambda d: 'x' in d)
    def t2(dep):
        return {'y': 1, **dep}


    @bolt({'z': None}, lambda d: d == {'x': None})
    def t3(dep):
        return {'z': 1, **dep}


    @spout({'c': None})
    def t4():
        yield {'c': 4, 'x': 'east'}
        yield {'c': 5, 'x': 'west'}


    @builder({'a': 2}, lambda _: True, 'x')
    def t5(obj, dep):
        obj.update(dep)


def test_task_decorator(example):
    assert len(tasks) == 5
    assert callable(tasks[0].func)
    assert tasks[0].obj == {'x': None}


def test_task_dag(example):
    build(tasks)

    assert len(G) == 5
    assert len(G.edges) == 6


def test_task_traversal(example):
    build(tasks)
    nodes = topological_sort()
    results = traverse(nodes)

    assert results == {
            't1': [{'x': 'east'}, {'x': 'west'}],
            't2': [{'x': 'east', 'y': 1}, {'x': 'west', 'y': 1}],
            't3': [{'x': 'east', 'z': 1}, {'x': 'west', 'z': 1}],
            't4': [{'x': 'east', 'c': 4}, {'x': 'west', 'c': 5}],
            't5': [
                {'a': 2, 'x': 'east', 'y': 1, 'z': 1, 'c': 4},
                {'a': 2, 'x': 'west', 'y': 1, 'z': 1, 'c': 5}
                ]
            }
