import pymunk

LIMB_STIFFNESS = 2400
LIMB_DAMPING = 75
LIMB_ANGULAR_DRAG = 0.94


def append_limb_stabilizers(joints, pairs):
    for parent, child in pairs:
        rest = child.angle - parent.angle
        joints.append(
            pymunk.DampedRotarySpring(
                parent,
                child,
                rest,
                LIMB_STIFFNESS,
                LIMB_DAMPING,
            )
        )


def damp_limb_spin(body, gravity, damping, dt):
    pymunk.Body.update_velocity(body, gravity, damping, dt)
    body.angular_velocity *= LIMB_ANGULAR_DRAG
