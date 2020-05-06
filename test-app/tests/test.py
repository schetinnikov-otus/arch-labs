import requests
import os
import faker
from requests_toolbelt.utils import dump

API_URL='http://{SERVICE_NAME}:{SERVICE_PORT}'.format(
    SERVICE_NAME=os.environ.get('SERVICE_NAME', ''),
    SERVICE_PORT=os.environ.get('SERVICE_PORT', '')
)

def print_request(r, *args, **kw):
    print(dump.dump_all(r).decode('utf-8'))

def assertResponse(assertion, success, failed):
    if assertion:
        print(success)
    else:
        print(failed)
        raise AssertionError("Test FAILED")

def assertStatusCode(r, status_code):
    assertResponse(
        r.status_code == status_code,
        success="OK: Status code is {}".format(status_code),
        failed="FAILED: Status code is not {}, it's {}".format(
            status_code,
            r.status_code
        )
    )

def assertHasKey(r, key):
    assertResponse(
        key in r.json(),
        success="OK: {} in response".format(key),
        failed="FAILED: not {} in response {}".format(key, r.json())
    )

def assertHasValue(r, key, value):
    assertHasKey(r, key)
    assertResponse(
        r.json()[key] == value,
        success="OK: {} is valid".format(key),
        failed="FAILED: expecting {} is {}, but got {}".format(
            key,
            value,
            r.json()[key])
    )

def test():
    hooks = dict(response=print_request)

    # test_data
    from faker import Faker
    fake = Faker()
    user = {
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "login": fake.simple_profile()['username']
    }

    # test creation
    r = requests.post(
        API_URL+'/api/v1/users/',
        json=user,
        hooks=hooks
    )
    assertStatusCode(r, 200)
    assertHasKey(r, 'objectId')
    user_id = r.json()['objectId']

    # test get
    r = requests.get(
        API_URL+'/api/v1/users/{}'.format(user_id),
        hooks=hooks
    )
    assertStatusCode(r, 200)
    assertHasValue(r, 'firstName', user['firstName'])
    assertHasValue(r, 'lastName', user['lastName'])
    assertHasValue(r, 'login', user['login'])

    # test update
    # really patch
    r = requests.put(
        API_URL+'/api/v1/users/{}'.format(user_id),
        json={"lastName": "Konstantinov"},
        hooks=hooks
    )
    assertStatusCode(r, 200)
    assertHasValue(r, 'lastName', 'Konstantinov')

    # test delete
    r = requests.delete(
        API_URL+'/api/v1/users/{}'.format(user_id),
        hooks=hooks
    )
    # assertStatusCode(r, 201)
    r = requests.get(
        API_URL+'/api/v1/users/{}'.format(user_id),
        hooks=hooks
    )
    # assertStatusCode(r, 404)

if __name__=='__main__':
    test()
