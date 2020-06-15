from . import Leap
from .qt import np_format
import numpy as np


class LeapListener(Leap.Listener):
    # finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
    # bone_names = ["Metacarpal", "Proximal", "Intermediate", "Distal"]

    def set_params(self, data):
        self.reading_rate_hz = 100
        self.data = data

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        # self.data.clear()
        self.data["frame_id"] = frame.id
        self.data["frame_timestamp"] = frame.timestamp
        self.data["frame_hands"] = len(frame.hands)
        self.data["frame_fingers"] = len(frame.fingers)

        # Get hands
        hand_check = {}
        for hand in frame.hands:
            handType = "left" if hand.is_left else "right"
            hand_check[handType] = True

            if handType not in self.data:
                self.data[handType] = {}

            # Get the hand's normal vector and direction
            hdir = hand.direction
            self.data[handType]["direction"] = np_format(hdir)
            self.data[handType]["direction_pyr"] = np.array([hdir.pitch, hdir.yaw, hdir.roll])
            pnor = hand.palm_normal
            self.data[handType]["palm_normal"] = np_format(pnor)
            self.data[handType]["palm_normal_pyr"] = np.array([pnor.pitch, pnor.yaw, pnor.roll])
            self.data[handType]["palm_position"] = np_format(hand.palm_position)
            self.data[handType]["wrist_position"] = np_format(hand.wrist_position)

            # fingers
            for finger_index in range(0, 5):
                for ip in range(4):
                    bone = hand.fingers[finger_index].bone(ip)
                    fname = "finger_{}_{}".format(finger_index, ip)
                    self.data[handType][fname + "_prev_joint"] = np_format(bone.prev_joint)
                    self.data[handType][fname + "_next_joint"] = np_format(bone.next_joint)
                    d = bone.direction
                    self.data[handType][fname + "_direction"] = np_format(d)
                    self.data[handType][fname + "_pyr"] = np.array([d.pitch, d.yaw, d.roll])

            # === leap table coordinate system ===
            #
            # 0: increase right
            # 1: increase up
            # 2: increase closer to self
            #
            # therefore, up = 1+, forward = 2-
            #
            # right handed
            # yaw: increase cw   (axis 1)
            #      start from forward
            # pitch: increase cw (axis 0)
            #        start from forward
            # roll: increase ccw (axis 2)
            #       start from down

        # time.sleep(1 / 100.0)

        self.data["finished"] = True

        # # clear data from hands that aren't visible
        # if "left" not in hand_check and "left" in self.data:
        #     self.data["left"] = None

        # if "right" not in hand_check and "right" in self.data:
        #     self.data["right"] = None


data = {}
listener = LeapListener()
listener.set_params(data)
controller = Leap.Controller()
controller.set_policy(controller.POLICY_OPTIMIZE_HMD)


def start():
    # controller.set_paused(False)
    controller.add_listener(listener)


def stop():
    # controller.set_paused(True)
    controller.remove_listener(listener)
