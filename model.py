#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
from google.appengine.ext import ndb

class User(ndb.Model):
    """User profile.

    Attributes:
        name: Name of the player; must be unique.
        email: Email address of the player. Used to email player reminders and
            game relevant events
    """
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
