from components.collider import Collider
from entities.entity import Entity
from entities.player import Player


class CollisionSystem:
    def __init__(self):
        pass

    def get_colliders(self, entity: Entity):
        return entity.get_components_by_type(Collider)

    def is_collision(self, entity_a: Entity, entity_b: Entity):
        colliders_a: list[Collider] = self.get_colliders(entity_a)
        colliders_b: list[Collider] = self.get_colliders(entity_b)

        if not colliders_a or not colliders_b:
            return False

        for collider_a in colliders_a:
            rect_a = collider_a.get_rect()

            for collider_b in colliders_b:
                rect_b = collider_b.get_rect()
                if rect_a.colliderect(rect_b):
                    return True

        return False

    def check_collision(
        self,
        entity_a: Entity,
        entity_b: Entity,
        player_prev_pos: tuple[float, float] | None = None,
    ):
        if not self.is_collision(entity_a, entity_b):
            return False

        if player_prev_pos is None:
            return True

        player = None
        other = None

        if isinstance(entity_a, Player):
            player = entity_a
            other = entity_b
        elif isinstance(entity_b, Player):
            player = entity_b
            other = entity_a

        if player is None:
            return True

        prev_x, prev_y = player_prev_pos
        current_x, current_y = player.rect.x, player.rect.y
        delta_x = current_x - prev_x
        delta_y = current_y - prev_y

        try:
            player.rect.x = prev_x
            if not self.is_collision(player, other):
                return 'right' if delta_x > 0 else 'left'

            player.rect.x = current_x
            player.rect.y = prev_y
            if not self.is_collision(player, other):
                return 'down' if delta_y > 0 else 'up'

            return 'both'
        finally:
            player.rect.x = current_x
            player.rect.y = current_y
