from dataclasses import dataclass, field

import pygame


@dataclass
class Item:
    name: str
    item_type: str
    quantity: int = 1
    icon: pygame.Surface | None = field(default=None, compare=False)


def _load_icon(path: str) -> pygame.Surface:
    return pygame.transform.scale(
        pygame.image.load(path).convert_alpha(), (48, 48)
    )


class Inventory:
    SLOTS: int = 9

    def __init__(self) -> None:
        self.slots: list[Item | None] = [None] * self.SLOTS
        self.selected_index: int = 0

    def get_selected(self) -> Item | None:
        return self.slots[self.selected_index]

    def select(self, index: int) -> None:
        if 0 <= index < self.SLOTS:
            self.selected_index = index

    def add_item(self, item: Item) -> bool:
        for slot in self.slots:
            if slot is not None and slot.name == item.name:
                slot.quantity += item.quantity
                return True
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = item
                return True
        return False

    def remove_one(self, index: int) -> None:
        item = self.slots[index]
        if item is None:
            return
        item.quantity -= 1
        if item.quantity <= 0:
            self.slots[index] = None

    @staticmethod
    def create_default() -> 'Inventory':
        inv = Inventory()
        inv.slots[0] = Item('hoe',    'tool', 1, _load_icon('assets/images/overlay/hoe.png'))
        inv.slots[1] = Item('water',  'tool', 1, _load_icon('assets/images/overlay/water.png'))
        inv.slots[2] = Item('corn',   'seed', 5, _load_icon('assets/images/overlay/corn.png'))
        inv.slots[3] = Item('tomato', 'seed', 5, _load_icon('assets/images/overlay/tomato.png'))
        return inv
