import math

import pymunk

from globals import PLAYER_SKIN, shape_color_rgba
from ragdoll_tuning import append_limb_stabilizers

RAGDOLL_SCALE = 1.4


def _s(value):
    return value * RAGDOLL_SCALE


def make_box(space, pos, size, mass, group, color):
    moment = pymunk.moment_for_box(mass, size)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Poly.create_box(body, size)
    shape.friction = 0.95
    shape.elasticity = 0.05
    shape.filter = pymunk.ShapeFilter(group=group)
    shape.color = shape_color_rgba(color)
    space.add(body, shape)
    return body, shape


def make_circle(space, pos, radius, mass, group, color):
    moment = pymunk.moment_for_circle(mass, radius, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.friction = 0.95
    shape.elasticity = 0.05
    shape.filter = pymunk.ShapeFilter(group=group)
    shape.color = shape_color_rgba(color)
    space.add(body, shape)
    return body, shape


def make_player(space, x, y, group):
    sk = PLAYER_SKIN
    torso, _ = make_box(space, (x, y), (_s(30), _s(70)), _s(10), group, sk["torso"])
    head, _ = make_circle(space, (x, y - _s(50)), _s(15), _s(1), group, sk["head"])

    l_upper_arm, _ = make_box(
        space, (x - _s(30), y - _s(20)), (_s(14), _s(34)), _s(2), group, sk["upper_arm"]
    )
    l_upper_arm.angle = torso.angle + math.radians(45)

    l_lower_arm, _ = make_box(
        space, (x - _s(45), y + _s(5)), (_s(12), _s(30)), _s(1.5), group, sk["lower_arm"]
    )
    r_lower_arm, _ = make_box(
        space, (x + _s(45), y + _s(5)), (_s(12), _s(30)), _s(1.5), group, sk["lower_arm"]
    )

    r_upper_arm, _ = make_box(
        space, (x + _s(30), y - _s(20)), (_s(14), _s(34)), _s(2), group, sk["upper_arm"]
    )
    r_upper_arm.angle = torso.angle + math.radians(-45)

    l_upper_leg, _ = make_box(
        space, (x - _s(10), y + _s(60)), (_s(16), _s(38)), _s(3), group, sk["upper_leg"]
    )
    l_lower_leg, _ = make_box(
        space, (x - _s(10), y + _s(95)), (_s(14), _s(34)), _s(2.5), group, sk["lower_leg"]
    )
    r_upper_leg, _ = make_box(
        space, (x + _s(10), y + _s(60)), (_s(16), _s(38)), _s(3), group, sk["upper_leg"]
    )
    r_lower_leg, _ = make_box(
        space, (x + _s(10), y + _s(95)), (_s(14), _s(34)), _s(2.5), group, sk["lower_leg"]
    )

    joints = [
        pymunk.PinJoint(head, torso, (0, _s(16)), (0, -_s(35))),
        pymunk.RotaryLimitJoint(head, torso, -0.35, 0.35),
        pymunk.PinJoint(l_upper_arm, torso, (0, -_s(17)), (-_s(15), -_s(20))),
        pymunk.RotaryLimitJoint(l_upper_arm, torso, -1.2, 0.6),
        pymunk.PinJoint(r_upper_arm, torso, (0, -_s(17)), (_s(15), -_s(20))),
        pymunk.RotaryLimitJoint(r_upper_arm, torso, -0.6, 1.2),
        pymunk.PinJoint(l_lower_arm, l_upper_arm, (0, -_s(15)), (0, _s(17))),
        pymunk.RotaryLimitJoint(l_lower_arm, l_upper_arm, 0.08, 1.32),
        pymunk.PinJoint(r_lower_arm, r_upper_arm, (0, -_s(15)), (0, _s(17))),
        pymunk.RotaryLimitJoint(r_lower_arm, r_upper_arm, -1.32, -0.08),
        pymunk.PinJoint(l_upper_leg, torso, (0, -_s(19)), (-_s(8), _s(35))),
        pymunk.RotaryLimitJoint(l_upper_leg, torso, -0.7, 0.9),
        pymunk.PinJoint(r_upper_leg, torso, (0, -_s(19)), (_s(8), _s(35))),
        pymunk.RotaryLimitJoint(r_upper_leg, torso, -0.9, 0.7),
        pymunk.PinJoint(l_lower_leg, l_upper_leg, (0, -_s(17)), (0, _s(19))),
        pymunk.RotaryLimitJoint(l_lower_leg, l_upper_leg, 0.0, 1.35),
        pymunk.PinJoint(r_lower_leg, r_upper_leg, (0, -_s(17)), (0, _s(19))),
        pymunk.RotaryLimitJoint(r_lower_leg, r_upper_leg, 0.0, 1.35),
    ]
    append_limb_stabilizers(
        joints,
        [
            (torso, head),
            (torso, l_upper_arm),
            (torso, r_upper_arm),
            (torso, l_upper_leg),
            (torso, r_upper_leg),
        ],
    )
    return joints, torso, head, l_upper_arm, l_lower_arm, r_upper_arm, r_lower_arm, l_upper_leg, l_lower_leg, r_upper_leg, r_lower_leg
