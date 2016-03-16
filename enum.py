#!/usr/bin/env python
"""
Copyright 2016 Brian Quach
Licensed under MIT (https://github.com/brianquach/udacity-nano-fullstack-conference/blob/master/LICENSE)  # noqa
"""
from protorpc import messages


class HandState(messages.Enum):
    """Represents which game state the hand is in.

    Attributes:
        STARTING: Initial hand delt to player, pre-player card exchange.
        ENDING: Final hand of plaer, post-player card exchange.
    """
    STARTING = 1
    ENDING = 2
