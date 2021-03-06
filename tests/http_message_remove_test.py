import pytest
import requests
import json
from src import config
from tests.fixture import global_owner, register_user2, register_user3, create_channel
from tests.fixture import user1_channel_message_id
from tests.fixture import VALID, ACCESSERROR, INPUTERROR

############################################
########## message/remove/v1 tests #########
############################################

# Test for invalid token
def test_channel_messages_invalid_token(global_owner, user1_channel_message_id):
    
    user1_token = global_owner['token']
    message1_id = user1_channel_message_id

    requests.post(config.url + "auth/logout/v1", json = {
        'token': user1_token
    })

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message1_id,
    })
    assert remove_message.status_code == ACCESSERROR

# Input error when message_id does not refer to a valid message 
# within a channel/DM that the authorised user has joined
    # 1. Negative message_id
def test_message_remove_invalid_message_id_negative(global_owner):

    user1_token = global_owner['token']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': -1,
    })
    assert remove_message.status_code == INPUTERROR

# Input error when message_id does not refer to a valid message 
# within a channel/DM that the authorised user has joined
    # 2. message_id is correct type (i.e. positive integer) but does not
    # exist with any message
def test_message_remove_invalid_message_id_nonexistant(global_owner):

    user1_token = global_owner['token']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': 256,
    })
    assert remove_message.status_code == INPUTERROR

# Input error when trying to remove a removed message
def test_cannot_remove_deleted_message(global_owner, user1_channel_message_id):
    token = global_owner['token']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': token,
        'message_id': user1_channel_message_id,
    })
    assert remove_message.status_code == VALID

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': token,
        'message_id': user1_channel_message_id,
    })
    assert remove_message.status_code == INPUTERROR

# Access error when message_id is valid, but the user does not belong to channel
def test_message_remove_invalid_message_id_not_belong_in_relevant_channel(global_owner, register_user2, user1_channel_message_id):

    user1_token = global_owner['token']
    message1_id = user1_channel_message_id

    user2_token = register_user2['token']
    assert user1_token != user2_token

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user2_token,
        'message_id': message1_id,
    })
    assert remove_message.status_code == ACCESSERROR

# Access error when message_id exists but does not belong to DM that user is part of
def test_message_remove_invalid_message_id_not_belong_in_relevant_DM_global_owner(global_owner, register_user2):

    user1_token = global_owner['token']
    user2_token = register_user2['token']

    user3 = requests.post(config.url + "auth/register/v2", json = {
        'email': 'larry@gmail.com',
        'password': 'password',
        'name_first': 'larry',
        'name_last': 'li'
    })
    user3_data = user3.json()
    u_id3 = user3_data['auth_user_id']

    create_dm1 = requests.post(config.url + "dm/create/v1", json = {
        'token': user2_token,
        'u_ids': [u_id3]
    })
    assert create_dm1.status_code == VALID
    dm1_id = json.loads(create_dm1.text)['dm_id']

    send_dm1_message = requests.post(config.url + "message/senddm/v1", json = {
        'token': user2_token,
        'dm_id': dm1_id,
        'message': 'hello there from dm1'
    })
    assert send_dm1_message.status_code == VALID
    message_id1 = json.loads(send_dm1_message.text)['message_id']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message_id1,
    })
    assert remove_message.status_code == ACCESSERROR

# Access error when:
    # the message was sent by an unauthorised user making this request
    # AND
    # the authorised user does NOT have owner permissions in the channel/DM
        # 1. User is member of channel but is not owner and did not send the message
        # that is being requested to remove
def test_message_remove_unauthorised_user_channel_not_send_message_and_not_owner(global_owner, register_user2, user1_channel_message_id, create_channel):

    # user 1 sent a message in the channel
    user1_token = global_owner['token']
    message1_id = user1_channel_message_id

    user2_token = register_user2['token']
    u_id2 = register_user2['auth_user_id']

    # invite user2 to join the channel
    channel1_id = create_channel['channel_id']
    requests.post(config.url + 'channel/invite/v2', json = {
        'token': user1_token,
        'channel_id': channel1_id,
        'u_id': u_id2
    })

    # user2 does not have permission to remove the message as a member
    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user2_token,
        'message_id': message1_id,
    })
    assert remove_message.status_code == ACCESSERROR

# Access error when:
    # the message was sent by an unauthorised user making this request
    # AND
    # the authorised user does NOT have owner permissions in the channel/DM
        # 2. User is member of DM but is not owner and did not send the message
        # that is being requested to remove
def test_message_remove_unauthorised_user_DM_not_send_message_and_not_owner(global_owner, register_user2):

    user1_token = global_owner['token']

    user2_token = register_user2['token']
    u_id2 = register_user2['auth_user_id']

    user3 = requests.post(config.url + "auth/register/v2", json = {
        'email': 'larry@gmail.com',
        'password': 'password',
        'name_first': 'larry',
        'name_last': 'li'
    })
    user3_token = json.loads(user3.text)['token']
    u_id3 = json.loads(user3.text)['auth_user_id']

    create_dm1 = requests.post(config.url + "dm/create/v1", json = {
        'token': user1_token,
        'u_ids': [u_id2, u_id3]
    })
    dm1_id = json.loads(create_dm1.text)['dm_id']

    send_dm1_message = requests.post(config.url + "message/senddm/v1", json = {
        'token': user2_token,
        'dm_id': dm1_id,
        'message': 'hello there from dm1'
    })
    message_id1 = json.loads(send_dm1_message.text)['message_id']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user3_token,
        'message_id': message_id1,
    })
    assert remove_message.status_code == ACCESSERROR

##### Implementation #####

# Base valid case
def test_message_remove_basic_valid(global_owner, create_channel, user1_channel_message_id):

    user1_token = global_owner['token']
    channel1_id = create_channel['channel_id']
    message1_id = user1_channel_message_id

    request_messages1 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user1_token,
        'channel_id': channel1_id,
        'start': 0
    })
    messages1 = json.loads(request_messages1.text)
    assert messages1['messages'][0]['message'] == 'hello'
    assert len(messages1['messages']) == 1

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message1_id,
    })
    assert remove_message.status_code == VALID

    request_messages2 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user1_token,
        'channel_id': channel1_id,
        'start': 0
    })
    messages2 = json.loads(request_messages2.text)
    assert len(messages2['messages']) == 0

# Message in channel was sent by the authorised user making this request
def test_message_remove_channel_authorised_user_request(global_owner, register_user2):

    user1_token = global_owner['token']
    u_id1 = global_owner['auth_user_id']

    user2_token = register_user2['token']
    channel1 = requests.post(config.url + "channels/create/v2", json = {
        'token': user2_token,
        'name': 'anna_channel',
        'is_public': False
    })
    channel1_id = json.loads(channel1.text)['channel_id']

    requests.post(config.url + 'channel/invite/v2', json = {
        'token': user2_token,
        'channel_id': channel1_id,
        'u_id': u_id1
    })
    send_message1 = requests.post(config.url + "message/send/v1", json = {
        'token': user1_token,
        'channel_id': channel1_id,
        'message': 'hello'
    })
    message1_id = json.loads(send_message1.text)['message_id']

    # Since user2 is the owner of 'anna_channel', user2 is able to remove user1's message in channel
    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user2_token,
        'message_id': message1_id,
    })
    assert remove_message.status_code == VALID

# Message in DM sent by authorised user is being removed that user
def test_message_remove_DM_authorised_user_request(global_owner, register_user2):

    user1_token = global_owner['token']

    user2_token = register_user2['token']
    u_id2 = register_user2['auth_user_id']

    user3 = requests.post(config.url + "auth/register/v2", json = {
        'email': 'larry@gmail.com',
        'password': 'password',
        'name_first': 'larry',
        'name_last': 'li'
    })
    user3_data = user3.json()
    u_id3 = user3_data['auth_user_id']

    create_dm1 = requests.post(config.url + "dm/create/v1", json = {
        'token': user1_token,
        'u_ids': [u_id2, u_id3]
    })
    dm1_id = json.loads(create_dm1.text)['dm_id']

    send_dm1_message = requests.post(config.url + "message/senddm/v1", json = {
        'token': user2_token,
        'dm_id': dm1_id,
        'message': 'hello there'
    })
    message_id1 = json.loads(send_dm1_message.text)['message_id']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user2_token,
        'message_id': message_id1,
    })
    assert remove_message.status_code == VALID

# Message in channel is being removed by authorised user who has owner permissions
def test_message_remove_channel_owner_request(global_owner, register_user2, create_channel):

    user1_token = global_owner['token']
    channel1_id = create_channel['channel_id']

    user2_token = register_user2['token']
    u_id2 = register_user2['auth_user_id']
    requests.post(config.url + 'channel/invite/v2', json = {
        'token': user1_token,
        'channel_id': channel1_id,
        'u_id': u_id2
    })

    send_message2 = requests.post(config.url + "message/send/v1", json = {
        'token': user2_token,
        'channel_id': channel1_id,
        'message': 'hello'
    })
    message2_id = json.loads(send_message2.text)['message_id']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message2_id,
    })

    assert remove_message.status_code == VALID

# Message in DM is being removed by authorised user who has owner permissions
def test_message_remove_DM_owner_request(global_owner, register_user2):

    user1_token = global_owner['token']

    user2_token = register_user2['token']
    u_id2 = register_user2['auth_user_id']

    user3 = requests.post(config.url + "auth/register/v2", json = {
        'email': 'larry@gmail.com',
        'password': 'password',
        'name_first': 'larry',
        'name_last': 'li'
    })
    user3_data = user3.json()
    u_id3 = user3_data['auth_user_id']

    create_dm1 = requests.post(config.url + "dm/create/v1", json = {
        'token': user1_token,
        'u_ids': [u_id2, u_id3]
    })
    dm1_id = json.loads(create_dm1.text)['dm_id']

    send_dm1_message = requests.post(config.url + "message/senddm/v1", json = {
        'token': user2_token,
        'dm_id': dm1_id,
        'message': 'hello there'
    })
    message_id1 = json.loads(send_dm1_message.text)['message_id']

    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message_id1,
    })
    assert remove_message.status_code == VALID

# Owner of UNSW Streams is able to remove message from any channel 
def test_message_edit_DM_global_owner_any_channel(global_owner, register_user2):

    user1_token = global_owner['token']

    user2_token = register_user2['token']

    user3 = requests.post(config.url + "auth/register/v2", json = {
        'email': 'larry@gmail.com',
        'password': 'password',
        'name_first': 'larry',
        'name_last': 'li'
    })
    user3_token = json.loads(user3.text)['token']

    channel1 = requests.post(config.url + "channels/create/v2", json = {
        'token': user2_token,
        'name': 'sally_channel',
        'is_public': False
    })
    channel1_id = json.loads(channel1.text)['channel_id']

    channel2 = requests.post(config.url + "channels/create/v2", json = {
        'token': user3_token,
        'name': 'larry_channel',
        'is_public': True
    })
    channel2_id = json.loads(channel2.text)['channel_id']

    send_message1 = requests.post(config.url + "message/send/v1", json = {
        'token': user2_token,
        'channel_id': channel1_id,
        'message': 'hello from user2'
    })
    message1_id = json.loads(send_message1.text)['message_id']

    send_message2 = requests.post(config.url + "message/send/v1", json = {
        'token': user3_token,
        'channel_id': channel2_id,
        'message': 'hello from user3'
    })
    message2_id = json.loads(send_message2.text)['message_id']

    request_messages1 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user2_token,
        'channel_id': channel1_id,
        'start': 0
    })
    messages1 = json.loads(request_messages1.text)
    assert len(messages1['messages']) == 1

    request_messages2 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user3_token,
        'channel_id': channel2_id,
        'start': 0
    })
    messages2 = json.loads(request_messages2.text)
    assert len(messages2['messages']) == 1

    remove_message1 = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message1_id,
    })
    assert remove_message1.status_code == VALID

    remove_message2 = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message2_id,
    })
    assert remove_message2.status_code == VALID

    # Checks that messages from user2 were edited by global owner of streams
    request_messages3 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user2_token,
        'channel_id': channel1_id,
        'start': 0
    })
    messages3 = json.loads(request_messages3.text)
    assert len(messages3['messages']) == 0

    # Checks that messages from user3 were edited by global owner of streams
    request_messages4 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user3_token,
        'channel_id': channel2_id,
        'start': 0
    })
    messages4 = json.loads(request_messages4.text)
    assert len(messages4['messages']) == 0

# Given 2 messages, check it deletes one 
def test_message_remove_channel_2_messages(global_owner, create_channel, user1_channel_message_id):

    user1_token = global_owner['token']
    channel1_id = create_channel['channel_id']
    message1_id = user1_channel_message_id

    send_message2 = requests.post(config.url + "message/send/v1", json = {
        'token': user1_token,
        'channel_id': channel1_id,
        'message': 'goodbye'
    })
    message2_id = json.loads(send_message2.text)['message_id']

    request_messages1 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user1_token,
        'channel_id': channel1_id,
        'start': 0
    })
    messages1 = json.loads(request_messages1.text)
    assert len(messages1['messages']) == 2

    remove_message1 = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message1_id
    })
    assert remove_message1.status_code == VALID

    request_messages1 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user1_token,
        'channel_id': channel1_id,
        'start': 0
    })
    messages1 = json.loads(request_messages1.text)
    assert len(messages1['messages']) == 1

    remove_message2 = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message2_id
    })
    assert remove_message2.status_code == VALID

    request_messages2 = requests.get(config.url + "channel/messages/v2", params = {
        'token': user1_token,
        'channel_id': channel1_id,
        'start': 0
    })
    messages2 = json.loads(request_messages2.text)
    assert len(messages2['messages']) == 0

# Removing message in a dm with 2 or more messages
def test_message_remove_dm_id_two_messages(global_owner, register_user2):
    # Registered users

    user1_token = global_owner['token']

    user2_id = register_user2['auth_user_id']
    
    # Created a dm
    dm1 = requests.post(config.url + "dm/create/v1", json = {
        'token': user1_token,
        'u_ids': [user2_id],
    })
    dm_id1 = json.loads(dm1.text)['dm_id']
    assert dm1.status_code == VALID

    # User 1 sends 2 messages in the dm
    send_message1 = requests.post(config.url + "message/senddm/v1", json = {
        'token': user1_token,
        'dm_id': dm_id1,
        'message': 'hello1'
    })
    message1_id = json.loads(send_message1.text)['message_id']
    assert send_message1.status_code == VALID

    send_message2 = requests.post(config.url + "message/senddm/v1", json = {
        'token': user1_token,
        'dm_id': dm_id1,
        'message': 'hello2'
    })
    assert send_message2.status_code == VALID

    # User 1 tries to edit a message wihin dm
    remove_message = requests.delete(config.url + "message/remove/v1", json = {
        'token': user1_token,
        'message_id': message1_id,
    })
    assert remove_message.status_code == VALID
