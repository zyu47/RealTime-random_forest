import numpy as np
from itertools import chain
from ..fusion.conf.postures import left_arm_motions, right_arm_motions


def extract_data(a, rgb):
    if rgb:
        base, offset = 3, range(2, 4)
        joints_to_consider = np.arange(18)
    else:
        base, offset = 9, range(9, 12)
        joints_to_consider = list(np.arange(12)) + list(np.arange(20, 25))

    indices = list(chain(*[[(k * base + j) for j in offset] for k in joints_to_consider]))
    data = [a[i] for i in indices]
    return data



def prune_joints(data, body_part, rgb= False):
    if rgb:
        base = 2
        if body_part == 'arms':
            joints, offset = [1, 3, 4, 6, 7], range(2)
        elif body_part == 'RA':
            joints, offset = [2, 3, 4], range(2)
        elif body_part == 'LA':
            joints, offset = [5, 6, 7], range(2)
        elif body_part == 'head':
            joints, offset = [0, 1, 14, 15, 16, 17], range(2)
    else:
        base = 3
        if body_part == 'arms':
            joints, offset = [5, 6, 7, 9, 10, 11, 12], range(3)
        elif body_part == 'RA':
            joints, offset = [8, 9, 10, 11, 0], range(3)
        elif body_part == 'LA':
            joints, offset = [4, 5, 6, 7, 0], range(3)
        elif body_part == 'arms_x':
            joints, offset = [5, 6, 7, 9, 10, 11], range(1)
        elif body_part == 'arms_y':
            joints, offset = [5, 6, 7, 9, 10, 11], range(1, 2)

    indices = list(chain(*[[(k * base + j) for j in offset] for k in joints]))
    return data[:, indices]


#Normalization by other joints
def normalize_by_joint(data, joint_index, rgb, verbose=False):
    dims = 2 if rgb else 3
    #print 'normalization joint index is: ', joint_index
    b = np.copy(data)
    b = b.astype(np.float64)
    joint = np.zeros(dims)

    for i in range(dims):
        joint[i] = np.mean(b[:, (joint_index*dims + i)])

    m, n = b.shape
    for i in range(n):
        b[:, i] -= joint[i % dims]


    if verbose:
        print 'data before normalization: ', data
        print 'mean of the spine joint:', joint
        print 'data after normalization: ', b

    return b



def normalize_joint_dataset(data_list, joint_index, rgb, verbose=False):
    return [normalize_by_joint(data, joint_index, rgb, verbose=verbose) for data in data_list]


def check_wave_motion(data, rgb):
    dims=2 if rgb else 3
    ELBOW, WRIST = 1, 2

    elbow_x = data[:, ELBOW*dims]
    elbow_y = data[:, ELBOW*dims+1]
    wrist_x = data[:, WRIST*dims]
    wrist_y = data[:, WRIST*dims+1]

    y_truth = list((wrist_y - elbow_y) >0)
    x_truth = list((wrist_x - elbow_x) > 0)

    if np.all(y_truth) and x_truth.count(True)> 0 and x_truth.count(False) >0:
        return True
    else:
        return False


def calculate_direction(data, body_part, rgb):
    if (body_part=='RA')or(body_part=='LA'):
        arm_motion_array = right_arm_motions if body_part =='RA' else left_arm_motions
        direction, probabilities = get_arm_motion(data, rgb)
        arm_motion_label = body_part + ':' + direction
        try:
            motion_encoding = arm_motion_array.index(arm_motion_label)
        except:
            motion_encoding = 26
        # print arm_motion_label
        return arm_motion_label, motion_encoding, probabilities

    elif (body_part=='arms_x') or (body_part=='arms_y'):
        return None



def calculate_magnitude(data): #this will give magnitude of every frame with 9 values
    return np.linalg.norm(data)


def magnitude(data):
    rows, cols = data.shape
    mag = 0
    for i in range(rows-1):
        mag += calculate_magnitude(data[i+1] - data[i])
    return mag


def get_direction(axis, sign):
    if axis == 0:
        direction = 'right' if sign>0 else 'left'
    elif axis == 1:
        direction = 'up' if sign>0 else 'down'
    elif axis == 2:
        direction = 'back' if sign>0 else 'front'
    return direction


def get_arm_motion(data, rgb):
    orientation = []

    axes = 2 if rgb else 3
    arm_threshold = 40.0 if rgb else 0.15  #Change this value
    axis_threshold = 0.5 if rgb else 0.3  #May change after including z axis
    proba_array = [0] * 6

    data = data[:,:(axes*3)] #considering only shoulder, elbow and wrist for arm motions


    if magnitude(data) >= arm_threshold:
        # print 'Magnitude threshold satisfied'
        delta = data[-1]-data[0]
        mag = calculate_magnitude(delta)
        # print 'magnitude of total deviation is: ', mag

        for k in range(axes):
            delta_in_axis = [j for (i, j) in enumerate(delta) if (i % axes == k)]

            mag_contrib_in_axis = sum(np.square(delta_in_axis)) / float(mag**2)
            mag_contrib_in_axis = round(mag_contrib_in_axis, 2)

            if mag_contrib_in_axis>= axis_threshold:
                orient_sign = sum(delta_in_axis)
                #Reversing direction only for RGB mode
                if rgb:
                    orient_sign = -orient_sign


                direction = get_direction(k, orient_sign)
                # print 'orientation sign is: ', orient_sign, 'direction reported is: ', direction
                orientation.append(direction)
                proba_index = k*2 if orient_sign>0 else (k*2+1)
                proba_array[proba_index] = mag_contrib_in_axis

        direction = ' move ' + ' '.join(orientation)
    else:
        direction = ' still'

    return direction, proba_array


def collect_all_results(map_array, point_array, proba_array, value):
    return map_array + list(chain(*point_array)) + list(chain(*proba_array)) + [value]


def send_default_values(body_parts, value_to_add= 26):
    proba_array, encoding_array, active_arm_array = [], [], []

    #Adding probability of 1.0 to still label for the 5 class probaility list
    #<Emblem>, <Motion>, <Neutral>, <Oscillate>, <Still>
    proba_array.append([0.0, 0.0, 0.0, 0.0, 1.0])

    for b in body_parts:
        proba_array.append([0] * 6), encoding_array.append(value_to_add), active_arm_array.append(0)


    #Adding index of 'body still' to the default values
    encoding_array.append(4)
    return encoding_array, active_arm_array, proba_array




def check_active_arm(data, rgb):
    dims = 2 if rgb else 3
    y_axis = np.array([0, 1]) if rgb else np.array([0, 1, 0])
    # ref_y, ref_z = -0.582, 1.6
    SPINE_BASE = 4
    avg = np.mean(data[:, [SPINE_BASE*3, SPINE_BASE*3+1, SPINE_BASE*3+2]], axis=0)
    ref_y, ref_z = avg[1], avg[2]

    first_shoulder = data[0][(0 * dims):(1 * dims)]
    first_elbow = data[0][(1 * dims):(2 * dims)]
    first_wrist = data[0][(2*dims):(3*dims)]

    first_shoulder_elbow = (first_elbow - first_shoulder)/np.linalg.norm((first_elbow - first_shoulder))
    first_elbow_wrist = (first_wrist - first_elbow) / np.linalg.norm((first_wrist - first_elbow))
    # first_shoulder_elbow_wrist = np.degrees(np.arccos(np.dot(first_shoulder_elbow, first_elbow_wrist)))


    last_shoulder = data[-1][(0 * dims):(1 * dims)]
    last_elbow = data[-1][(1 * dims):(2 * dims)]
    last_wrist = data[-1][(2 * dims):(3 * dims)]

    last_shoulder_elbow = (last_elbow - last_shoulder) / np.linalg.norm((last_elbow - last_shoulder))
    last_elbow_wrist = (last_wrist - last_elbow) / np.linalg.norm((last_wrist - last_elbow))
    # last_shoulder_elbow_wrist = np.degrees(np.arccos(np.dot(last_shoulder_elbow, last_elbow_wrist)))

    # print first_shoulder_elbow_wrist, last_shoulder_elbow_wrist
    # if 30>first_shoulder_elbow_wrist>-30 and 30>last_shoulder_elbow_wrist>-30:
    #     return False
    # else:
    #     return True


    threshold_z = 0.08  # 0.090
    # print np.abs(first_shoulder[-1] - ref_z), np.abs(last_shoulder[-1] - ref_z)
    if np.abs(first_wrist[-1] - ref_z) > threshold_z and np.abs(last_wrist[-1] - ref_z) > threshold_z:
        # print 'Active'
        return True
    else:
        # print 'Dangling'
        return False




