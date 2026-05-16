from components.collider import Collider
from entities.entity import Entity
from entities.player import Player

class CollisionSystem:
    def __init__(self):
        pass

    def get_colliders(self, entity: Entity):
        return entity.get_components_by_type(Collider)

    def check_colliders(self, entity_a: Entity, entity_b: Entity):
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
