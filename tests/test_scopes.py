#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `scopes` package."""

import os

print(os.getenv('PYTHONPATH'))

import pytest

from click.testing import CliRunner

from scopes import scopes
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


# t1------
# |   |  |
# v   v  |
# t2  t3 |
# \  /  /  t6
#  v   |   |
#  t4<----/
#
#  t5 (skipped)


@pytest.fixture
def tasks():
    scopes.tasks = []

    @scopes.task({'x': None})
    def t1():
        return {'x': True}


    @scopes.task({'y': None}, lambda d: 'x' in d)
    def t2(dep):
        return {'y': 1, **dep}


    @scopes.task({'z': None}, lambda d: d == {'x': None})
    def t3(dep):
        return {'z': 1, **dep}


    @scopes.task({'a': None}, lambda _: True)
    def t4(dep):
        return {'a': 2, **dep}


    # shouldn't resolve any dependencies
    @scopes.task({'b': None}, lambda _: False)
    def t5(dep):
        return {'b': 3, **dep}


    @scopes.task({'c': None})
    def t6():
        yield {'c': 4}
        yield {'c': 5}


@pytest.fixture
def G():
    return scopes.init()


def test_task_decorator(tasks):
    assert len(scopes.tasks) == 6
    assert callable(scopes.tasks[0][0])
    assert scopes.tasks[0][1] == {'x': None}


def test_task_dag(G, tasks):
    scopes.build_graph(G)

    assert len(G.nodes) == 5
    assert len(G.edges) == 6


def test_task_traversal(G, tasks):
    scopes.build_graph(G)
    results = scopes.traverse_graph(G)

    assert results == [
            {'x': True},
            {'c': 4},
            {'c': 5},
            {'x': True, 'y': 1},
            {'x': True, 'z': 1},
            {'x': True, 'a': 2},
            {'x': True, 'y': 1, 'a': 2},
            {'x': True, 'z': 1, 'a': 2},
            {'a': 2, 'c': 4},
            {'a': 2, 'c': 5}
            ]
