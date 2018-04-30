from .state_machines import TriStateMachine
from . import rules

engage = TriStateMachine("engage", rules.match_any('engage'), 1)

posack = TriStateMachine("posack",
                         rules.match_any('rh thumbs up', 'lh thumbs up'))

negack = TriStateMachine("negack",
                         rules.match_any('rh thumbs down', 'lh thumbs down', 'rh stop', 'lh stop'), 8)

left_point_vec = TriStateMachine("left point",
                                 rules.and_rules(
                                     rules.match_all('LA: still'),
                                     rules.match_any('lh point down', 'lh point right', 'lh point front')
                                     ))

right_point_vec = TriStateMachine("right point",
                                  rules.and_rules(
                                      rules.match_all('RA: still'),
                                      rules.match_any('rh point down', 'rh point left', 'rh point front')
                                      ))

grab = TriStateMachine("grab", rules.match_any('rh claw down', 'lh claw down'))

grab_move_up = TriStateMachine("grab move up",
                               rules.or_rules(
                                   rules.match_all('rh claw down', 'RA: move up'),
                                   rules.match_all('lh claw down', 'LA: move up')
                                   ))

grab_move_down = TriStateMachine("grab move down",
                                 rules.or_rules(
                                     rules.match_all('rh claw down', 'RA: move down'),
                                     rules.match_all('lh claw down', 'LA: move down')
                                     ))

grab_move_left = TriStateMachine("grab move left",
                                 rules.or_rules(
                                     rules.match_all('rh claw down', 'RA: move left'),
                                     rules.match_all('lh claw down', 'LA: move left')
                                     ))

grab_move_right = TriStateMachine("grab move right",
                                  rules.or_rules(
                                      rules.match_all('rh claw down', 'RA: move right'),
                                      rules.match_all('lh claw down', 'LA: move right')
                                      ))

grab_move_front = TriStateMachine("grab move front",
                                  rules.or_rules(
                                      rules.match_all('rh claw down', 'RA: move front'),
                                      rules.match_all('lh claw down', 'LA: move front')
                                      ))

grab_move_back = TriStateMachine("grab move back",
                                 rules.or_rules(
                                     rules.match_all('rh claw down', 'RA: move back'),
                                     rules.match_all('lh claw down', 'LA: move back')
                                     ))

push_left = TriStateMachine("push left",
                            rules.and_rules(
                                rules.match_any('rh closed left', 'rh open left'),
                                rules.match_all('RA: move left')
                                ))

push_right = TriStateMachine("push right",
                             rules.and_rules(
                                 rules.match_any('lh closed right', 'lh open right'),
                                 rules.match_all('LA: move right')
                                 ))

push_front = TriStateMachine("push front",
                             rules.or_rules(
                                 rules.match_all('rh closed front', 'RA: move front'),
                                 rules.match_all('lh closed front', 'LA: move front')
                                 ))

push_back = TriStateMachine("push back",
                            rules.or_rules(
                                rules.and_rules(
                                    rules.match_any('rh open back', 'rh closed back'),
                                    rules.match_all('RA: move back')
                                    ),
                                rules.and_rules(
                                    rules.match_any('lh open back', 'lh closed back'),
                                    rules.match_all('LA: move back')
                                    ),
                                rules.match_any('rh beckon', 'lh beckon')
                                ), 8)

unknown = TriStateMachine("unknown",
                          rules.and_rules(
                              rules.match_all('emblem'),
                              rules.mismatch_all('rh one front', 'lh one front', 'rh one front',
                                                 'rh two front', 'rh two back', 'lh two front', 'lh two back',
                                                 'rh three front', 'rh three back', 'lh three front', 'lh three back',
                                                 'rh four front', 'lh four front',
                                                 'rh five front', 'lh five front',
                                                 'rh inch', 'lh inch',
                                                 'rh l', 'lh l',
                                                 'rh stop', 'lh stop',
                                                 'rh thumbs up', 'lh thumbs up',
                                                 'rh thumbs down', 'lh thumbs down'
                                                 )
                              )
                          )

servo_left = TriStateMachine("servo left",
                             rules.and_rules(
                                 rules.match_any('rh closed left', 'rh open left'),
                                 rules.match_all('oscillate'))
                             )

servo_right = TriStateMachine("servo right",
                              rules.and_rules(
                                  rules.match_any('lh closed right', 'lh open right'),
                                  rules.match_all('oscillate'))
                              )

servo_front = TriStateMachine("servo front",
                              rules.and_rules(
                                  rules.match_any('rh closed front', 'lh closed front'),
                                  rules.match_all('oscillate'))
                              )

servo_back = TriStateMachine("servo back",
                             rules.and_rules(
                                 rules.match_any('rh closed back', 'lh closed back',
                                                 'rh open back', 'lh open back'),
                                 rules.match_all('oscillate'))
                             )


count_one = TriStateMachine("count one", rules.match_any('rh one front', 'lh one front'))

count_two = TriStateMachine("count two",
                            rules.match_any('rh two front', 'rh two back', 'lh two front', 'lh two back'))

count_three = TriStateMachine("count three",
                              rules.match_any('rh three front', 'rh three back', 'lh three front', 'lh three back'))

count_four = TriStateMachine("count four", rules.match_any('rh four front', 'lh four front'))

count_five = TriStateMachine("count five", rules.or_rules(
            rules.and_rules(
                rules.match_all('rh five front'),
                rules.mismatch_all('RA: wave')),
            rules.and_rules(
                rules.match_all('lh five front'),
                rules.mismatch_all('LA: wave'))
            ))
