#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
import endpoints

from protorpc import messages
from protorpc import message_types


class StringMessage(messages.Message):
    """Outbound response string message"""
    message = messages.StringField(1, required=True)

class PlayerName(messages.Message):
    """Outbound response string message"""
    player = messages.StringField(1, required=True)

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2)
)
