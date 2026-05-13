import pymunk


def _set_shape_collision_type(body, collision_type):
    for shape in body.shapes:
        shape.collision_type = collision_type


class RagdollSurfaceContacts:
    """counts when any of ``supported_bodies`` touches shapes of ``surface_collision_types``."""

    def __init__(self, space, surface_collision_types, supported_bodies):
        self._supported = frozenset(supported_bodies)
        self._contact_counts = {}
        if isinstance(surface_collision_types, (tuple, list)):
            types_ = tuple(surface_collision_types)
        else:
            types_ = (surface_collision_types,)
        for ct in types_:
            space.on_collision(
                collision_type_a=ct,
                collision_type_b=None,
                begin=self._begin,
                separate=self._separate,
                data=self,
            )

    def _supported_body(self, arbiter):
        for shape in arbiter.shapes:
            if shape is None or shape.body is None:
                continue
            if shape.body in self._supported:
                return shape.body
        return None

    def _begin(self, arbiter, space_, data):
        body = data._supported_body(arbiter)
        if body is None:
            return
        data._contact_counts[body] = data._contact_counts.get(body, 0) + 1

    def _separate(self, arbiter, space_, data):
        body = data._supported_body(arbiter)
        if body is None:
            return
        count = data._contact_counts.get(body, 0)
        if count <= 1:
            data._contact_counts.pop(body, None)
        else:
            data._contact_counts[body] = count - 1

    def body_supported(self, body):
        return self._contact_counts.get(body, 0) > 0

    def any_supported(self, bodies):
        return any(self.body_supported(body) for body in bodies)


class GroundTracker:
    def __init__(self, space, floor_collision_type):
        self._contact_counts = {}
        space.on_collision(
            collision_type_a=floor_collision_type,
            collision_type_b=None,
            begin=self._begin,
            separate=self._separate,
            data=self,
        )

    def _dynamic_body(self, arbiter):
        for shape in arbiter.shapes:
            if shape is None or shape.body is None:
                continue
            if shape.body.body_type != pymunk.Body.STATIC:
                return shape.body
        return None

    def _begin(self, arbiter, space_, data):
        body = data._dynamic_body(arbiter)
        if body is None:
            return
        data._contact_counts[body] = data._contact_counts.get(body, 0) + 1

    def _separate(self, arbiter, space_, data):
        body = data._dynamic_body(arbiter)
        if body is None:
            return
        count = data._contact_counts.get(body, 0)
        if count <= 1:
            data._contact_counts.pop(body, None)
        else:
            data._contact_counts[body] = count - 1

    def body_on_floor(self, body):
        return self._contact_counts.get(body, 0) > 0

    def ragdoll_on_floor(self, bodies):
        return any(self.body_on_floor(body) for body in bodies)

    def movement_allowed(self, bodies, torso, upward_speed_limit=120):
        if torso.velocity.y < -upward_speed_limit:
            return False
        return self.ragdoll_on_floor(bodies)
