import pytest
import requests
import json
from src import config

@pytest.fixture
def register_user():
    requests.delete(config.url + "clear/v1")
    user = requests.post(config.url + "auth/register/v2", json ={
        'email': 'cat@gmail.com',
        'password': 'password',
        'name_first': 'anna',
        'name_last': 'lee'
    })
    user_data = user.json()
    return user_data

##########################################
######### channels_create tests ##########
##########################################

# AccessError Invalid auth_user_id
def test_create_invalid_token():
    requests.delete(config.url + "clear/v1")

    # Public
    resp1 = requests.post(config.url + "channels/create/v2", json ={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjF9.csBzbal4Qczwb0lpZ8LzhpEdCpUbKgaaBV_bkYcriWw',
        'name': '1531_CAMEL',
        'is_public': True
    })

    resp2 = requests.post(config.url + "channels/create/v2", json ={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjJ9.jeXV_YsnPUUjY1Rjh3Sbzo4rw10xO0CUjuRV-JKqVYA',
        'name': '1531_CAMEL',
        'is_public': True
    })

    # Input Error
    assert resp1.status_code == 403
    assert resp2.status_code == 403

    # Private
    resp3 = requests.post(config.url + "channels/create/v2", json ={
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjF9.csBzbal4Qczwb0lpZ8LzhpEdCpUbKgaaBV_bkYcriWw',
            'name': '1531_CAMEL',
            'is_public': False
    })

    resp4 = requests.post(config.url + "channels/create/v2", json ={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjJ9.jeXV_YsnPUUjY1Rjh3Sbzo4rw10xO0CUjuRV-JKqVYA',
        'name': '1531_CAMEL',
        'is_public': False
    })

    assert resp3.status_code == 403
    assert resp4.status_code == 403

    # invalid token with invalid channel name
    resp5 = requests.post(config.url + "channels/create/v2", json ={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjF9.csBzbal4Qczwb0lpZ8LzhpEdCpUbKgaaBV_bkYcriWw',
        'name': ' ',
        'is_public': False
    })

    resp6 = requests.post(config.url + "channels/create/v2", json ={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjJ9.jeXV_YsnPUUjY1Rjh3Sbzo4rw10xO0CUjuRV-JKqVYA',
        'name': 'a' * 50,
        'is_public': True
    })

    assert resp5.status_code == 400
    assert resp6.status_code == 400

# InputError when length of name is less than 1 or more than 20 characters
def test_create_invalid_name(register_user):

    token1 = register_user['token']
    resp1 = requests.post(config.url + "channels/create/v2", json ={
        'token': token1,
        'name': '',
        'is_public': True
    })

    resp2 = requests.post(config.url + "channels/create/v2", json ={
        'token': token1,
        'name': '  ',
        'is_public': True
    })

    resp3 = requests.post(config.url + "channels/create/v2", json ={
        'token': token1,
        'name': '                      ',
        'is_public': True
    })

    resp4 = requests.post(config.url + "channels/create/v2", json ={
        'token': token1,
        'name': 'a' * 21,
        'is_public': True
    })

    resp5 = requests.post(config.url + "channels/create/v2", json ={
        'token': token1,
        'name': 'a' * 50,
        'is_public': True
    })

    assert resp1.status_code == 400
    assert resp2.status_code == 400
    assert resp3.status_code == 400
    assert resp4.status_code == 400
    assert resp5.status_code == 400

# Assert channel_id can never be a negative number
def test_create_negative_channel_id(register_user):

    token1 = register_user['token']
    resp = requests.post(config.url + "channels/create/v2", json ={
        'token': token1,
        'name': '1531_CAMEL',
        'is_public': False
    })
    channel_id1 = json.loads(resp.text)['channel_id']
    assert channel_id1 > 0

##### Implementation #####
# Assert channel_id for one, two and three channels created by two different users
def test_create_valid_channel_id(register_user):

    auth_user_id1 = register_user['token']
    resp1 = requests.post(config.url + "channels/create/v2", json ={
        'token': auth_user_id1,
        'name': '1531_CAMEL_1',
        'is_public': True
    })
    assert resp1.status_code == 200

    resp2 = requests.post(config.url + "channels/create/v2", json ={
        'token': auth_user_id1,
        'name': '1531_CAMEL_2',
        'is_public': True
    })
    assert resp2.status_code == 200

    id2 = requests.post(config.url + "auth/register/v2", json ={
        'email': 'abc2@gmail.com',
        'password': 'password',
        'name_first': 'bfirst',
        'name_last': 'blast'
    })
    auth_user_id2 = json.loads(id2.text)['token']

    resp3 = requests.post(config.url + "channels/create/v2", json ={
        'token': auth_user_id2,
        'name': '1531_CAMEL_3',
        'is_public': True
    })
    assert resp3.status_code == 200

    id3 = requests.post(config.url + "auth/register/v2", json ={
        'email': 'abc3@gmail.com',
        'password': 'password',
        'name_first': 'cfirst',
        'name_last': 'clast'
    })

    auth_user_id3 = json.loads(id3.text)['token']
    resp4 = requests.post(config.url + "channels/create/v2", json ={
        'token': auth_user_id3,
        'name': '1531_CAMEL_3',
        'is_public': False
    })
    assert resp4.status_code == 200

##########################################
######### channels_list tests ############
##########################################

# test when an user does not create a channel
def test_no_channel(register_user):

    token = register_user['token']
    list = requests.get(config.url + 'channels/list/v2', params ={
        'token': token
    })
    assert json.loads(list.text) == {'channels': []}
    assert list.status_code == 200

# test one user creates a channel and can be appended in the list
def test_channel_list(register_user):

    token = register_user['token']

    channel = requests.post(config.url + "channels/create/v2", 
        json = {
            'token': token,
            'name': '1531_CAMEL',
            'is_public': False
        })
    channel_id1 = json.loads(channel.text)['channel_id']
    assert channel_id1 > 0
    
    list1 = requests.get(config.url + 'channels/list/v2', params ={
        'token': token
    })
    assert (json.loads(list1.text) == 
        {
        'channels':[
            {
                'channel_id': channel_id1,
                'name': '1531_CAMEL',
            }
        ],
    })
    assert list1.status_code == 200

##########################################
######### channels_listall tests #########
##########################################

def test_listall_no_channel(register_user): 

    token = register_user['token']
    listall = requests.get(config.url + 'channels/listall/v2', params ={
        'token': token
    })
    assert json.loads(listall.text) == {'channels': []}
    assert listall.status_code == 200

def test_listall(register_user): 

    token1 = register_user['token']
    
    channel1 = requests.post(config.url + "channels/create/v2", 
        json = {
        'token': token1,
        'name': 'channel1',
        'is_public': True
    })
    channel_id1 = json.loads(channel1.text)['channel_id']
    
    assert channel_id1 != None

    listall1 = requests.get(config.url + "channels/listall/v2", params ={ 
            'token': token1
    })

    assert (json.loads(listall1.text) == 
        {
        'channels':[
            {
                'channel_id': channel_id1,
                'name': 'channel1',
            }
        ],
    })
    assert listall1.status_code == 200