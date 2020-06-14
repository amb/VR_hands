import numpy as np


def np_direction(d):
    # pitch roll yaw
    return np.array([d.pitch, d.roll, d.yaw])


def np_format(d):
    return np.array([d[0], d[1], d[2]])


def np_normalized(d):
    l = np.linalg.norm(d)
    # TODO: what to do when l is zero?
    return d / l if l != 0.0 else np.array([0.0, 0.0, -1.0])


def pyr_mat3x3(up, direction):
    xaxis = np.cross(up, direction)
    xaxis = np_normalized(xaxis)
    yaxis = np.cross(direction, xaxis)
    yaxis = np_normalized(yaxis)

    out = np.eye(3)
    out[0][0] = xaxis[0]
    out[1][0] = yaxis[0]
    out[2][0] = direction[0]
    out[0][1] = xaxis[1]
    out[1][1] = yaxis[1]
    out[2][1] = direction[1]
    out[0][2] = xaxis[2]
    out[1][2] = yaxis[2]
    out[2][2] = direction[2]
    return out


def q_axis_angle(axis, angle):
    s = np.sin(angle / 2.0)
    u = np_normalized(axis)
    return np.array([np.cos(angle / 2.0), u[0] * s, u[1] * s, u[2] * s])


def q_lookat(direction):
    fw = np_format(direction.forward)
    dr = np_format(direction)
    rotAxis = np_normalized(np.cross(fw, dr))
    if np.linalg.norm(rotAxis) == 0.0:
        rotAxis = np_format(direction.up)

    rotAngle = np.arccos(np.dot(fw, dr))
    return q_axis_angle(rotAxis, rotAngle)


def qb_lookat(dr):
    fw = np.array([0.0, 0.0, -1.0])
    dr = np_normalized(dr)
    rotAxis = np_normalized(np.cross(fw, dr))
    if np.linalg.norm(rotAxis) == 0.0:
        rotAxis = np.array([0.0, 1.0, 0.0])

    rotAngle = np.arccos(np.dot(fw, dr))
    return q_axis_angle(rotAxis, rotAngle)


def aangle_to_blender(direction, normal):
    qroll = q_axis_angle(np_format(direction.forward), normal.roll)
    qpitch = q_axis_angle(np_format(direction.left), direction.pitch)
    qyaw = q_axis_angle(np_format(direction.up), direction.yaw)
    return qroll * qpitch * qyaw


def q_from_vecs(a, b):
    c = np_normalized(np.cross(a, b))
    d = np.arccos(np.dot(a, b))
    return q_axis_angle(c, d)


def plane_project(vector, plane_normal):
    """ Input vectors must be unit vectors """
    d = np.dot(vector, plane_normal)
    if d < 0.0:
        d = np.dot(-vector, plane_normal)
    return vector - plane_normal * d
