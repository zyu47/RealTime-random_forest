from .state_machines import BinaryStateMachine
from . import rules

posack = BinaryStateMachine(["posack start", "posack stop"], {
    "posack stop": {
        "posack start": rules.match_any('rh thumbs up', 'lh thumbs up', 'head nod')
    },
    "posack start": {
        "posack stop": rules.mismatch_all('rh thumbs up', 'lh thumbs up', 'head nod')
    }
}, "posack stop")


negack = BinaryStateMachine(["negack start", "negack stop"], {
    "negack stop": {
        "negack start": rules.match_any('rh thumbs down', 'lh thumbs down', 'rh stop', 'lh stop', 'head shake')
    },
    "negack start": {
        "negack stop": rules.mismatch_all('rh thumbs down', 'lh thumbs down', 'rh stop', 'lh stop', 'head shake')
    }
}, "negack stop")


engage = BinaryStateMachine(["engage start", "engage stop"], {
    "engage stop": {
        "engage start": rules.match_any('engage')
    },
    "engage start": {
        "engage stop": rules.mismatch_all('engage')
    }
}, "engage stop", 1)

left_point_vec = BinaryStateMachine(["left point start", "left point stop"], {
    "left point stop": {
        "left point start": rules.and_rules(
            rules.match_all('LA: still'),
            rules.match_any('lh point down', 'lh point right', 'lh point front')
        )
    },
    "left point start": {
        "left point stop": rules.or_rules(
            rules.mismatch_any('LA: still'),
            rules.mismatch_all('lh point down', 'lh point right', 'lh point front')
        )
    }
}, "left point stop")

right_point_vec = BinaryStateMachine(["right point start", "right point stop"], {
    "right point stop": {
        "right point start": rules.and_rules(
            rules.match_all('RA: still'),
            rules.match_any('rh point down', 'rh point left', 'rh point front')
        )
    },
    "right point start": {
        "right point stop": rules.or_rules(
            rules.mismatch_any('RA: still'),
            rules.mismatch_all('rh point down', 'rh point left', 'rh point front')
        )
    }
}, "right point stop")

left_continuous_point = BinaryStateMachine(["left continuous point start", "left continuous point stop"], {
    "left continuous point stop": {
        "left continuous point start": rules.match_any('lh point down', 'lh point right', 'lh point front')
    },
    "left continuous point start": {
        "left continuous point stop": rules.mismatch_all('lh point down', 'lh point right', 'lh point front')
    }
}, "left continuous point stop", 3)

right_continuous_point = BinaryStateMachine(["right continuous point start", "right continuous point stop"], {
    "right continuous point stop": {
        "right continuous point start": rules.match_any('rh point down', 'rh point left', 'rh point front')
    },
    "right continuous point start": {
        "right continuous point stop": rules.mismatch_all('rh point down', 'rh point left', 'rh point front')
    }
}, "right continuous point stop", 3)

grab = BinaryStateMachine(["grab start", "grab stop"], {
    "grab stop": {
        "grab start": rules.match_any('rh claw down', 'lh claw down')
    },
    "grab start": {
        "grab stop": rules.mismatch_all('rh claw down', 'lh claw down')
    }
}, "grab stop")


grab_move_right = BinaryStateMachine(["grab move right start", "grab move right stop"], {
    "grab move right start": {
        "grab move right stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move right'),
            rules.mismatch_any('lh claw down', 'LA: move right')
        )
    },
    "grab move right stop": {
        "grab move right start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move right'),
            rules.match_all('lh claw down', 'LA: move right')
        )
    }
}, "grab move right stop")


grab_move_left = BinaryStateMachine(["grab move left start", "grab move left stop"], {
    "grab move left start": {
        "grab move left stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move left'),
            rules.mismatch_any('lh claw down', 'LA: move left')
        )
    },
    "grab move left stop": {
        "grab move left start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move left'),
            rules.match_all('lh claw down', 'LA: move left')
        )
    }
}, "grab move left stop")


grab_move_up = BinaryStateMachine(["grab move up start", "grab move up stop"], {
    "grab move up start": {
        "grab move up stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move up'),
            rules.mismatch_any('lh claw down', 'LA: move up')
        )
    },
    "grab move up stop": {
        "grab move up start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move up'),
            rules.match_all('lh claw down', 'LA: move up')
        )
    }
}, "grab move up stop")


grab_move_down = BinaryStateMachine(["grab move down start", "grab move down stop"], {
    "grab move down start": {
        "grab move down stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move down'),
            rules.mismatch_any('lh claw down', 'LA: move down')
        )
    },
    "grab move down stop": {
        "grab move down start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move down'),
            rules.match_all('lh claw down', 'LA: move down')
        )
    }
}, "grab move down stop")


grab_move_front = BinaryStateMachine(["grab move front start", "grab move front stop"], {
    "grab move front start": {
        "grab move front stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move front'),
            rules.mismatch_any('lh claw down', 'LA: move front')
        )
    },
    "grab move front stop": {
        "grab move front start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move front'),
            rules.match_all('lh claw down', 'LA: move front')
        )
    }
}, "grab move front stop")


grab_move_back = BinaryStateMachine(["grab move back start", "grab move back stop"], {
    "grab move back start": {
        "grab move back stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move back'),
            rules.mismatch_any('lh claw down', 'LA: move back')
        )
    },
    "grab move back stop": {
        "grab move back start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move back'),
            rules.match_all('lh claw down', 'LA: move back')
        )
    }
}, "grab move back stop")


grab_move_right_front = BinaryStateMachine(["grab move right front start", "grab move right front stop"], {
    "grab move right front start": {
        "grab move right front stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move right front'),
            rules.mismatch_any('lh claw down', 'LA: move right front')
        )
    },
    "grab move right front stop": {
        "grab move right front start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move right front'),
            rules.match_all('lh claw down', 'LA: move right front')
        )
    }
}, "grab move right front stop")


grab_move_left_front = BinaryStateMachine(["grab move left front start", "grab move left front stop"], {
    "grab move left front start": {
        "grab move left front stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move left front'),
            rules.mismatch_any('lh claw down', 'LA: move left front')
        )
    },
    "grab move left front stop": {
        "grab move left front start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move left front'),
            rules.match_all('lh claw down', 'LA: move left front')
        )
    }
}, "grab move left front stop")


grab_move_left_back = BinaryStateMachine(["grab move left back start", "grab move left back stop"], {
    "grab move left back start": {
        "grab move left back stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move left back'),
            rules.mismatch_any('lh claw down', 'LA: move left back')
        )
    },
    "grab move left back stop": {
        "grab move left back start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move left back'),
            rules.match_all('lh claw down', 'LA: move left back')
        )
    }
}, "grab move left back stop")


grab_move_right_back = BinaryStateMachine(["grab move right back start", "grab move right back stop"], {
    "grab move right back start": {
        "grab move right back stop": rules.and_rules(
            rules.mismatch_any('rh claw down', 'RA: move right back'),
            rules.mismatch_any('lh claw down', 'LA: move right back')
        )
    },
    "grab move right back stop": {
        "grab move right back start": rules.or_rules(
            rules.match_all('rh claw down', 'RA: move right back'),
            rules.match_all('lh claw down', 'LA: move right back')
        )
    }
}, "grab move right back stop")


push_left = BinaryStateMachine(["push left start", "push left stop"], {
    "push left start": {
        "push left stop": rules.or_rules(
            rules.mismatch_all('rh closed left', 'rh open left'),
            rules.mismatch_any('RA: move left')
        )
    },
    "push left stop": {
        "push left start": rules.and_rules(
            rules.match_any('rh closed left', 'rh open left'),
            rules.match_all('RA: move left')
        )
    }
}, "push left stop")


push_right = BinaryStateMachine(["push right start", "push right stop"], {
    "push right start": {
        "push right stop": rules.or_rules(
            rules.mismatch_all('lh closed right', 'lh open right'),
            rules.mismatch_any('LA: move right')
        )
    },
    "push right stop": {
        "push right start": rules.and_rules(
            rules.match_any('lh closed right', 'lh open right'),
            rules.match_all('LA: move right')
        )
    }
}, "push right stop")


push_front = BinaryStateMachine(["push front start", "push front stop"], {
    "push front start": {
        "push front stop": rules.and_rules(
            rules.mismatch_any('rh closed front', 'RA: move front'),
            rules.mismatch_any('lh closed front', 'LA: move front')
        )
    },
    "push front stop": {
        "push front start": rules.or_rules(
            rules.match_all('rh closed front', 'RA: move front'),
            rules.match_all('lh closed front', 'LA: move front')
        )
    }
}, "push front stop")


push_back = BinaryStateMachine(["push back start", "push back stop"], {
    "push back start": {
        "push back stop": rules.and_rules(
            rules.or_rules(
                rules.mismatch_all('rh open back', 'rh closed back'),
                rules.mismatch_any('RA: move back')
            ),
            rules.or_rules(
                rules.mismatch_all('lh open back', 'lh closed back'),
                rules.mismatch_any('LA: move back')
            ),
            rules.mismatch_all('rh beckon', 'lh beckon')
        )
    },
    "push back stop": {
        "push back start": rules.or_rules(
            rules.and_rules(
                rules.match_any('rh open back', 'rh closed back'),
                rules.match_all('RA: move back')
            ),
            rules.and_rules(
                rules.match_any('lh open back', 'lh closed back'),
                rules.match_all('LA: move back')
            ),
            rules.match_any('rh beckon', 'lh beckon')
        )
    }
}, "push back stop")


count_one = BinaryStateMachine(["count one start", "count one stop"], {
    "count one stop": {
        "count one start": rules.match_any('rh one front', 'lh one front')
    },
    "count one start": {
        "count one stop": rules.mismatch_all('rh one front', 'lh one front')
    }
}, "count one stop")


count_two = BinaryStateMachine(["count two start", "count two stop"], {
    "count two stop": {
        "count two start": rules.match_any('rh two front', 'rh two back', 'lh two front', 'lh two back')
    },
    "count two start": {
        "count two stop": rules.mismatch_all('rh two front', 'rh two back', 'lh two front', 'lh two back')
    }
}, "count two stop")


count_three = BinaryStateMachine(["count three start", "count three stop"], {
    "count three stop": {
        "count three start": rules.match_any('rh three front', 'rh three back', 'lh three front', 'lh three back')
    },
    "count three start": {
        "count three stop": rules.mismatch_all('rh three front', 'rh three back', 'lh three front', 'lh three back')
    }
}, "count three stop")


count_four = BinaryStateMachine(["count four start", "count four stop"], {
    "count four stop": {
        "count four start": rules.match_any('rh four front', 'lh four front')
    },
    "count four start": {
        "count four stop": rules.mismatch_all('rh four front', 'lh four front')
    }
}, "count four stop")


count_five = BinaryStateMachine(["count five start", "count five stop"], {
    "count five stop": {
        "count five start": rules.or_rules(
            rules.and_rules(
                rules.match_all('rh five front'),
                rules.mismatch_all('RA: wave')),
            rules.and_rules(
                rules.match_all('lh five front'),
                rules.mismatch_all('LA: wave'))
            )
    },
    "count five start": {
        "count five stop": rules.mismatch_all('rh five front', 'lh five front')
    }
}, "count five stop")


arms_apart_X = BinaryStateMachine(["arms apart X start", "arms apart X stop"], {
    "arms apart X stop": {
        "arms apart X start": rules.match_all('LA: apart X', 'RA: apart X')
    },
    "arms apart X start": {
        "arms apart X stop": rules.mismatch_any('LA: apart X', 'RA: apart X')
    }
}, "arms apart X stop")


arms_together_X = BinaryStateMachine(["arms together X start", "arms together X stop"], {
    "arms together X stop": {
        "arms together X start": rules.match_all('LA: together X', 'RA: together X')
    },
    "arms together X start": {
        "arms together X stop": rules.mismatch_any('LA: together X', 'RA: together X')
    }
}, "arms together X stop")


arms_apart_Y = BinaryStateMachine(["arms apart Y start", "arms apart Y stop"], {
    "arms apart Y stop": {
        "arms apart Y start": rules.match_all('LA: apart Y', 'RA: apart Y')
    },
    "arms apart Y start": {
        "arms apart Y stop": rules.mismatch_any('LA: apart Y', 'RA: apart Y')
    }
}, "arms apart Y stop")


arms_together_Y = BinaryStateMachine(["arms together Y start", "arms together Y stop"], {
    "arms together Y stop": {
        "arms together Y start": rules.match_all('LA: together Y', 'RA: together Y')
    },
    "arms together Y start": {
        "arms together Y stop": rules.mismatch_any('LA: together Y', 'RA: together Y')
    }
}, "arms together Y stop")

wave = BinaryStateMachine(["wave start", "wave stop"], {
    "wave stop": {
        "wave start": rules.match_any('LA: wave', 'RA: wave')
    },
    "wave start": {
        "wave stop": rules.mismatch_all('LA: wave', 'RA: wave')
    }
}, "wave stop")
