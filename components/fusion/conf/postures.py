left_hand_postures = ['blank', 'hands together', 'other', 'lh beckon', 'lh claw down',
                      'lh claw front', 'lh claw right', 'lh claw up', 'lh closed back',
                      'lh closed down', 'lh closed front', 'lh closed right', 'lh fist',
                      'lh five front', 'lh four front', 'lh inch', 'lh l', 'lh one front',
                      'lh open back', 'lh open down', 'lh open right', 'lh point down',
                      'lh point front', 'lh point right', 'lh stop', 'lh three back',
                      'lh three front', 'lh thumbs down', 'lh thumbs up', 'lh to face',
                      'lh two back', 'lh two front', 'blind']

right_hand_postures = ['blank', 'hands together', 'other', 'rh beckon', 'rh claw down',
                       'rh claw front', 'rh claw left', 'rh claw up', 'rh closed back',
                       'rh closed down', 'rh closed front', 'rh closed left', 'rh fist',
                       'rh five front', 'rh four front', 'rh inch', 'rh l', 'rh one front',
                       'rh open back', 'rh open down', 'rh open left', 'rh point down',
                       'rh point front', 'rh point left', 'rh stop', 'rh three back',
                       'rh three front', 'rh thumbs down', 'rh thumbs up', 'rh to face',
                       'rh two back', 'rh two front', 'blind']

left_arm_motions = ['LA: move right', 'LA: move left', 'LA: move up', 'LA: move down', 'LA: move back',
                    'LA: move front', 'LA: move right up', 'LA: move right down', 'LA: move right back',
                    'LA: move right front', 'LA: move left up', 'LA: move left down', 'LA: move left back',
                    'LA: move left front', 'LA: move up back', 'LA: move up front', 'LA: move down back',
                    'LA: move down front', 'LA: move right up back', 'LA: move right up front',
                    'LA: move right down back', 'LA: move right down front', 'LA: move left up back',
                    'LA: move left up front', 'LA: move left down back', 'LA: move left down front', 'LA: still',
                    'LA: apart X', 'LA: together X', 'LA: apart Y', 'LA: together Y', 'LA: wave', 'blind']

right_arm_motions = ['RA: move right', 'RA: move left', 'RA: move up', 'RA: move down', 'RA: move back',
                     'RA: move front', 'RA: move right up', 'RA: move right down', 'RA: move right back',
                     'RA: move right front', 'RA: move left up', 'RA: move left down', 'RA: move left back',
                     'RA: move left front', 'RA: move up back', 'RA: move up front', 'RA: move down back',
                     'RA: move down front', 'RA: move right up back', 'RA: move right up front',
                     'RA: move right down back', 'RA: move right down front', 'RA: move left up back',
                     'RA: move left up front', 'RA: move left down back', 'RA: move left down front', 'RA: still',
                     'RA: apart X', 'RA: together X', 'RA: apart Y', 'RA: together Y', 'RA: wave', 'blind']

head_postures = ['head nod', 'head shake', 'other', 'blind']

body_postures = ['emblem', 'motion', 'neutral', 'oscillate', 'still']

# Create vector form for each posture
_engage_vec = [ 1 << 0 ]
_vecs = _engage_vec + [1 << i for i in range(1, len(left_hand_postures + right_hand_postures + left_arm_motions + right_arm_motions + head_postures + body_postures) + 1)]
_postures = ["engage"] + left_hand_postures + right_hand_postures + left_arm_motions + right_arm_motions + head_postures + body_postures

from_vec = dict(zip(_vecs, _postures))
to_vec = dict(zip(_postures, _vecs))
