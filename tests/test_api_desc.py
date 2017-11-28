import pytest
import requests

APP_URL = 'http://minikep-db.herokuapp.com'
API_DESC_URL = f'{APP_URL}/api/desc'


# GET api/desc?head=GDP

# Returns:
#   {'head':'GDP', 'ru':'Цена нефти Brent'}  on head
#   All descriptions (head and unit) without parameter

# GET api/desc?unit=rog&lang=en

# Returns:
#    {unit:'rog', en:'rate of growth to previous period'}
#    All descriptions (head and unit) without parameter

# POST api/desc

# Payload:
# [dict(head='BRENT', ru='Цена нефти Brent', en='Brent oil price')
# dict(head='GDP', ru='Валовый внутренний продукт', en='Gross domestic product')
# dict(unit='rog', ru='темп роста к пред. периоду', en='rate of growth to previous period')
# dict(unit='yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')]

# DELETE api/desc?unit=rog
# DELETE api/desc?head=BRENT

sample_post_payload = [
    dict(head='test_BRENT', ru='Цена нефти Brent', en='Brent oil price'),
    dict(head='test_GDP', ru='Валовый внутренний продукт', en='Gross domestic product'),
    dict(unit='test_rog', ru='темп роста к пред. периоду', en='rate of growth to previous period'),
    dict(unit='test_yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')
]

@pytest.mark.webtest
class Test_ApiDesc:
    def teardown(self):
        pass

    def test_get_without_params_should_fail(self):
        response = requests.get(API_DESC_URL)
        assert response.status_code != 200

    def test_post_with_valid_params_is_ok(self):
        response = requests.post(API_DESC_URL, json=sample_post_payload)
        assert response.status_code == 200

    def test_posting_dublicate_data_should_fail(self):
        response = requests.post(API_DESC_URL, json=sample_post_payload)
        assert response.status_code != 200

    def test_getting_posted_data_is_ok(self):
        for desc in sample_post_payload:
            response = requests.get(API_DESC_URL, params={
                'head': desc.get('head'),
                'unit': desc.get('unit')
            })
            assert desc == response.json()

    def test_deleting_posted_data_is_ok(self):
        for desc in sample_post_payload:
            response = requests.delete(API_DESC_URL, params={
                'head': desc.get('head'),
                'unit': desc.get('unit')
            })
            assert response.status_code == 200