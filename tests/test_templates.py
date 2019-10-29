import os

import pytest

import voila.app
from lxml import etree

BASE_DIR = os.path.dirname(__file__)


class VoilaTest(voila.app.Voila):
    def listen(self):
        pass  # the ioloop is taken care of by the pytest-tornado framework


@pytest.fixture
def voila_app(voila_args, voila_config):
    voila_app = VoilaTest.instance()
    voila_app.initialize(voila_args + ['--no-browser'])
    voila_config(voila_app)
    nbconvert_template_path = os.path.join(
        BASE_DIR, '..', 'share/jupyter/voila/templates/gridstack/nbconvert_templates/')
    template_path = os.path.join(
        BASE_DIR, '..', 'share/jupyter/voila/templates/gridstack/templates')
    voila_app.nbconvert_template_paths.insert(0, nbconvert_template_path)
    voila_app.template_paths.insert(0, template_path)
    voila_app.start()
    yield voila_app
    voila_app.stop()
    voila_app.clear_instance()


@pytest.fixture
def app(voila_app):
    return voila_app.app


@pytest.fixture
def voila_config():
    return lambda app: None


@pytest.fixture
def voila_args():
    nb_path = os.path.join(BASE_DIR, 'nb.ipynb')
    return [nb_path, '--VoilaTest.config_file_paths=[]']


@pytest.mark.gen_test
def test_template_test(http_client, base_url):
    response = yield http_client.fetch(base_url)
    assert response.code == 200
    html_body = response.body.decode('utf-8')
    assert 'data-gs-width="6"' in html_body
    assert 'data-gs-height="5"' in html_body
    parser = etree.HTMLParser()
    tree = etree.fromstring(html_body, parser=parser)

    # test width/height params
    elem = tree.xpath("//pre[text()='Hi !\n']/ancestor::div[@class='grid-stack-item']")[0]
    assert elem.attrib['data-gs-width'] == '6'
    assert elem.attrib['data-gs-height'] == '5'

    # test hidden cell
    elem = tree.xpath("//*[text()='This is a hidden cell.']")
    assert not elem

