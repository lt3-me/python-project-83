import page_analyzer
from flask import Flask


def test_app():
    assert isinstance(page_analyzer.app, Flask)
