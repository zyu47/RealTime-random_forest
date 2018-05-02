import sys
import time
import argparse
import struct
import Queue

import numpy as np

from .automata import bi_state_machines as bsm
from .automata import tri_state_machines as tsm
from .automata.state_machines import GrabStateMachine
from .fusion_thread import Fusion
from .remote_thread import Remote
from . import thread_sync
from .conf import streams
from .conf import postures


class App:

    def __init__(self, state_machines, debug):
        self._start()

        # Initialize the state manager
        self.state_machines = state_machines

        # For performance evaluation
        self.skipped = 0
        self.received = 0
        self.debug = debug

    def _stop(self):
        # Stop the fusion thread
        self.fusion.stop()
        self.started = False

        # Stop the remote output thread
        self.remote.stop()
        self.remote_started = False

        # Stop the remote GUI thread
        self.gui.stop()
        self.gui_started = False

        # Clear sync queque in case resetting
        self._clear_synced_data()

        self.skipped = 0
        self.received = 0

    def _clear_synced_data(self):
        not_empty = True
        while not_empty:
            try:
                thread_sync.synced_msgs.get_nowait()
            except Queue.Empty:
                not_empty = False

    def _start(self):
        # Start fusion thread
        self.fusion = Fusion()
        self.fusion.start()
        self.started = True

        # Start server thread for Brandeis
        self.remote = Remote('Brandeis', 'brandeis', thread_sync.remote_events, thread_sync.remote_connected)
        self.remote.start()
        self.remote_started = True

        # Start server thread for GUI
        self.gui = Remote('GUI', 'gui', thread_sync.gui_events, thread_sync.gui_connected)
        self.gui.start()
        self.gui_started = True

    def _print_summary(self):
        """
        Prints a summary of skipped timestamps to keep up with the input rate
        :return: Nothing
        """
        if self.received > 0:
            print "Skipped percentage: " + str(self.skipped * 100.0 / self.received)

    def _exit(self):
        """
        Exits the application by printing a summary, stopping all the background network threads, and exiting
        :return:
        """
        self._print_summary()
        self._stop()
        sys.exit(0)

    def run(self):
        try:
            while True:
                self._update()
        except KeyboardInterrupt:
            self._exit()

    def _update(self):
        """
        Updates the latest synced data, and requests updating the latest gesture
        Also prints debugging messages related to sync queue
        :return:
        """
        try:
            # Get synced data without blocking with timeout
            self.latest_s_msg = thread_sync.synced_msgs.get(False, 0.2)
            if self.debug:
                print "Latest synced message: ", self.latest_s_msg, "\n"
            #
            self._update_queues()
            self.received += 1
            if thread_sync.synced_msgs.qsize() <= 15:
                if self.debug:
                    print "Backlog queue size exceeded limit: {}".format(thread_sync.synced_msgs.qsize())
            else:
                self.skipped += 1
                print "Skipping because backlog too large: {}".format(thread_sync.synced_msgs.qsize())
        except Queue.Empty:
            pass

    def _get_probs(self):

        if streams.is_active("Body"):
            body_msg = self.latest_s_msg["Body"]
            engaged = body_msg.data.engaged
            larm_probs, rarm_probs = np.array(body_msg.data.p_l_arm), np.array(body_msg.data.p_r_arm)
            body_probs = np.array([body_msg.data.p_emblem, body_msg.data.p_motion, body_msg.data.p_neutral,
                               body_msg.data.p_oscillate, body_msg.data.p_still])
        else:
            engaged = True
            larm_probs, rarm_probs = np.zeros(6), np.zeros(6)
            body_probs = np.zeros(5)

        lhand_probs = np.array(self.latest_s_msg["LH"].data.probabilities) \
            if streams.is_active("LH") else np.zeros(len(postures.left_hand_postures))
        rhand_probs = np.array(self.latest_s_msg["RH"].data.probabilities) \
            if streams.is_active("RH") else np.zeros(len(postures.right_hand_postures))
        head_probs = np.array(self.latest_s_msg["Head"].data.probabilities) \
            if streams.is_active("Head") else np.zeros(len(postures.head_postures))

        return engaged, larm_probs, rarm_probs, lhand_probs, rhand_probs, head_probs, body_probs

    def _prepare_probs(self):
        engaged, larm_probs, rarm_probs, lhand_probs, rhand_probs, head_probs, body_probs = self._get_probs()
        all_probs = list(np.concatenate((larm_probs, rarm_probs, lhand_probs, rhand_probs, head_probs, body_probs), axis=0))
        return struct.pack("<" + str(len(all_probs)) + "f", *all_probs)

    def _get_pose_vectors(self, low_threshold=0.1, high_threshold=0.5):

        engaged, larm_probs, rarm_probs, lhand_probs, rhand_probs, head_probs, body_probs = self._get_probs()

        if streams.is_active("Body"):
            body_msg = self.latest_s_msg["Body"]
            idx_l_arm, idx_r_arm, idx_body = body_msg.data.idx_l_arm, body_msg.data.idx_r_arm, body_msg.data.idx_body
        else:
            idx_l_arm, idx_r_arm, idx_body = len(postures.left_arm_motions) - 1, len(
                postures.right_arm_motions) - 1, len(postures.body_postures) - 1

        hand_labels = np.array(range(len(lhand_probs)))
        high_lhand_labels = hand_labels[lhand_probs >= high_threshold]
        low_lhand_labels = hand_labels[np.logical_and(lhand_probs >= low_threshold, lhand_probs < high_threshold)]
        high_rhand_labels = hand_labels[rhand_probs >= high_threshold]
        low_rhand_labels = hand_labels[np.logical_and(rhand_probs >= low_threshold, rhand_probs < high_threshold)]

        head_labels = np.array(range(len(head_probs)))
        high_head_labels = head_labels[head_probs >= high_threshold]

        # High pose uses max probability arm labels, max probability body label
        # head labels with probabilities in [high_threshold, 1.0],
        # and hand labels with probabilities in [low_threshold, high_threshold)
        high_pose = 1 if engaged else 0
        high_pose |= postures.to_vec[postures.left_arm_motions[idx_l_arm]]
        high_pose |= postures.to_vec[postures.right_arm_motions[idx_r_arm]]
        high_pose |= postures.to_vec[postures.body_postures[idx_body]]

        for l in high_lhand_labels:
            high_pose |= postures.to_vec[postures.left_hand_postures[l]]
        for l in high_rhand_labels:
            high_pose |= postures.to_vec[postures.right_hand_postures[l]]
        for l in high_head_labels:
            high_pose |= postures.to_vec[postures.head_postures[l]]

        # Low pose uses max probability arm labels, and max probability body label
        # no head labels,
        # and hand labels with probabilities in [low_threshold, high_threshold)
        low_pose = 1 if engaged else 0
        low_pose |= postures.to_vec[postures.left_arm_motions[idx_l_arm]]
        low_pose |= postures.to_vec[postures.right_arm_motions[idx_r_arm]]
        low_pose |= postures.to_vec[postures.body_postures[idx_body]]

        for l in low_lhand_labels:
            low_pose |= postures.to_vec[postures.left_hand_postures[l]]
        for l in low_rhand_labels:
            low_pose |= postures.to_vec[postures.right_hand_postures[l]]

        return engaged, high_pose, low_pose

    def _get_events(self):

        engaged, high_pose, low_pose = self._get_pose_vectors()
        if streams.is_active("Body"):
            body_msg = self.latest_s_msg["Body"]
            lx, ly, var_l = body_msg.data.pos_l_x, body_msg.data.pos_l_y, body_msg.data.var_l
            rx, ry, var_r = body_msg.data.pos_r_x, body_msg.data.pos_r_y, body_msg.data.var_r
        else:
            lx, ly, var_l, rx, ry, var_r = (float("-inf"),)*6

        word = self.latest_s_msg["Speech"].data.command if streams.is_active("Speech") else ""

        # More than one output data is possible from multiple state machines
        all_events_to_send = []

        ts = "{0:.3f}".format(time.time())

        for state_machine in self.state_machines:
            # Input the combined label to the state machine
            # State machine could be binary or tristate
            changed = state_machine.input(engaged, high_pose, low_pose)
            cur_state = state_machine.get_state()

            # If it is the binary state machine for continuous points
            # and is in start state, append pointer message contents to the sent message
            if state_machine is bsm.left_continuous_point:
                if state_machine.is_started():
                    all_events_to_send.append("P;l,{0:.2f},{1:.2f};{2:.2f};{3:s}".format(lx, ly, var_l, ts))
            elif state_machine is bsm.right_continuous_point:
                if state_machine.is_started():
                    all_events_to_send.append("P;r,{0:.2f},{1:.2f};{2:.2f};{3:s}".format(rx, ry, var_r, ts))
            # Else, check if current input caused a transition
            elif changed:
                # For the special case of binary state machines for left point vec and right point vec
                # append x,y coordinates to state
                if state_machine is tsm.left_point_vec or state_machine is bsm.left_point_vec:
                    if state_machine.is_started():
                        cur_state += ",{0:.2f},{1:.2f}".format(lx, ly)
                elif state_machine is tsm.right_point_vec or state_machine is bsm.right_point_vec:
                    if state_machine.is_started():
                        cur_state += ",{0:.2f},{1:.2f}".format(rx, ry)
                # Finally create a timestamped message
                all_events_to_send.insert(0, "G;" + cur_state + ";" + ts)

        if engaged and len(word) > 0:
            all_events_to_send.append("S;" + word + ";" + ts)

        if not engaged:
            self._clear_synced_data()

        return all_events_to_send

    def _prepare_events(self):
        raw_events_to_send = []
        all_events_to_send = self._get_events()

        for e in all_events_to_send:
            ev_type, ev, timestamp = e.split(';')
            if ev_type != 'P':
                print ev_type.ljust(5) + ev.ljust(30) + timestamp + "\n\n"
            raw_events_to_send.append(struct.pack("<i" + str(len(e)) + "s", len(e), e))

        return raw_events_to_send

    def _update_queues(self):
        """
        Update the queues for events to be sent.
        Currently, two queues are updated: Remote GUI and Remote Client (Brandeis)
        :return: None
        """

        raw_events_list = self._prepare_events()
        raw_probs = self._prepare_probs()

        # Include a check to see if the destination is connected or not
        for e in raw_events_list:
            if thread_sync.remote_connected.wait(0.0):
                thread_sync.remote_events.put(e)
        if len(raw_events_list) > 0:
            #print(len(raw_events_list))
            #print(raw_events_list)
            pass

        if thread_sync.gui_connected.wait(0.0):
            ev_count = struct.pack("<i", len(raw_events_list))
            new_ev = ev_count + ''.join(raw_events_list) + raw_probs
            thread_sync.gui_events.put(new_ev)


gsm = GrabStateMachine()

brandeis_events = [bsm.engage, bsm.left_continuous_point, bsm.right_continuous_point, bsm.wave,
                   tsm.count_five, tsm.count_four, tsm.count_three, tsm.count_two, tsm.count_one,
                   gsm,
                   tsm.negack, tsm.posack,
                   tsm.push_back, tsm.push_front, tsm.push_left, tsm.push_right,
                   tsm.right_point_vec, tsm.left_point_vec]

csu_events = brandeis_events + [tsm.unknown, tsm.servo_left, tsm.servo_right]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['csu', 'brandeis'], default='brandeis', type=str,
                        help="the mode in which fusion server is run")
    parser.add_argument('-D', '--debug', dest='debug_mode', default=False, action='store_true', help='enable the debug mode')
    args = parser.parse_args()

    if args.mode == 'brandeis':
        print "Running in Brandeis mode"
        event_set = brandeis_events
    elif args.mode == 'csu':
        print "Running in CSU mode"
        event_set = csu_events
    else:
        event_set = None

    a = App(event_set, args.debug_mode)
    a.run()
