import pygame
from pytmx.util_pygame import load_pygame

from entities.entity import Entity
from entities.player import Player
from entities.world import World
from entities.static_objects import StaticObject
from entities.plant import Plant
from entities.trader import Trader
from entities.npc_milo import MiloNPC

from components.collider import Collider
from core.collision_layers import LAYER_WORLD, LAYER_FARMABLE, LAYER_TOOL
from core.inventory import Item, _load_icon

from systems.collision_system import CollisionSystem, get_mtv
from systems.render_system import RenderSystem
from systems.sound_system import SoundSystem
from systems.camera_system import CameraSystem
from systems.hud_system import HudSystem
from systems.input_system import InputState
from systems.sky_system import SkySystem
from systems.shop_system import ShopSystem
from core.settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT


class WorldGame:
    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen
        self.entities: list[Entity] = []

        self.animation_counter: int = 0
        self.animation_step: int = 15
        self.tool_animation_active: bool = False
        self.tool_animation_timer: int = 0

        self.sound_system: SoundSystem = SoundSystem()
        self.render_system: RenderSystem = RenderSystem(self.screen)
        self.collision_system: CollisionSystem = CollisionSystem()
        self.hud_system: HudSystem = HudSystem()
        self.debug_colliders: bool = True

        # Plantas ativas: mapeadas por posicao de tile
        self.plants: dict[tuple[int, int], Plant] = {}

        self.sky_system: SkySystem = SkySystem()
        self.shop_system: ShopSystem = ShopSystem()
        self._sleep_font: pygame.font.Font = pygame.font.SysFont(None, 36)

        # Cria e adiciona entidade do mundo
        self.world = World()
        self.add_entity(self.world)
        self.world.start_music()

        # Cria e adiciona entidade do player
        self.player = Player(self.world.spawn)
        self.add_entity(self.player)

        self.trader = Trader(self.world.trader_position)
        self.add_entity(self.trader)

        self.milo: MiloNPC = MiloNPC(self.world.milo_position)
        self.add_entity(self.milo)

        # Cria os objetos estaticos do mapa
        self.load_static_objects()

        self.camera_system = CameraSystem(
            self.screen.get_width(),
            self.screen.get_height(),
            self.world.rect.width,
            self.world.rect.height,
        )

    def load_static_objects(self) -> None:
        tmx_data = load_pygame('assets/map/map.tmx')

        for obj in tmx_data.get_layer_by_name('Trees'):
            self.add_entity(StaticObject(
                name='Tree',
                position=pygame.Vector2(obj.x, obj.y),
                surface=obj.image
            ))

        for obj in tmx_data.get_layer_by_name('Decoration'):
            self.add_entity(StaticObject(
                name='Decoration',
                position=pygame.Vector2(obj.x, obj.y),
                surface=obj.image
            ))

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def _resolve_animation_state(self, input_state: InputState) -> str:
        moving: bool = (
            input_state['move_up'] or input_state['move_down']
            or input_state['move_left'] or input_state['move_right']
        )

        if input_state['move_up']:
            self.player.current_direction = 'up'
        elif input_state['move_down']:
            self.player.current_direction = 'down'
        elif input_state['move_left']:
            self.player.current_direction = 'left'
        elif input_state['move_right']:
            self.player.current_direction = 'right'

        if moving:
            return f'walk_{self.player.current_direction}'

        return f'idle_{self.player.current_direction}'

    def _update_player_animation(self, input_state: InputState) -> None:
        animation = self.player.get_component('animation')

        if self.tool_animation_active:
            self.tool_animation_timer += 1
            if self.tool_animation_timer >= self.animation_step * 2:
                self.tool_animation_active = False
                self.tool_animation_timer = 0
                animation.set_state(f'idle_{self.player.current_direction}')
        else:
            target_state: str = self._resolve_animation_state(input_state)
            animation.set_state(target_state)

        self.animation_counter += 1
        if self.animation_counter >= self.animation_step:
            animation.advance_frame()
            self.animation_counter = 0

        current_frame: pygame.Surface = animation.get_current_frame()
        self.player.get_component('sprite').set_surface(current_frame)

    def _move_player(self, dt: float, input_state: InputState) -> None:
        speed: float = 350 if input_state['sprint'] else 250
        self.player.set_speed(speed)

        move_x: float = 0.0
        move_y: float = 0.0

        if input_state['move_up']:
            move_y -= self.player.speed * dt
        if input_state['move_down']:
            move_y += self.player.speed * dt
        if input_state['move_left']:
            move_x -= self.player.speed * dt
        if input_state['move_right']:
            move_x += self.player.speed * dt

        self.player.move(move_x, move_y)
        self._clamp_player_to_world()

    def _clamp_player_to_world(self) -> None:
        max_x: float = max(0, self.world.rect.width - self.player.rect.width)
        max_y: float = max(0, self.world.rect.height - self.player.rect.height)

        self.player.rect.x = max(0, min(self.player.rect.x, max_x))
        self.player.rect.y = max(0, min(self.player.rect.y, max_y))

    def _update_camera(self) -> None:
        target_x: float = self.player.rect.centerx
        target_y: float = self.player.rect.centery
        self.camera_system.update(target_x, target_y)

    def _is_facing_trader(self) -> bool:
        tool_rect = self.player.get_component('tool_collider').get_rect()
        return tool_rect.colliderect(self.trader.rect)

    def _is_facing_milo(self) -> bool:
        tool_rect = self.player.get_component('tool_collider').get_rect()
        return tool_rect.colliderect(self.milo.rect)

    def _get_front_tile(self) -> tuple[int, int]:
        center: pygame.Vector2 = pygame.Vector2(
            self.player.get_component('collider').get_rect().center
        )
        tile_x: int = int(center.x // TILE_SIZE)
        tile_y: int = int(center.y // TILE_SIZE)
        direction: str = self.player.current_direction
        if direction == 'right':
            delta: pygame.Vector2 = pygame.Vector2(1, 0)
        elif direction == 'left':
            delta = pygame.Vector2(-1, 0)
        elif direction == 'down':
            delta = pygame.Vector2(0, 1)
        else:  # up
            delta = pygame.Vector2(0, -1)
        return int(tile_x + delta.x), int(tile_y + delta.y)

    def update(self, dt: float, input_state: InputState) -> None:
        if not self.milo.dialog_box.is_open:
            self._move_player(dt, input_state)
            self._update_player_animation(input_state)
        self.player.update_tool_collider()
        self._update_camera()
        self.collision_process()
        self.sky_system.update(dt)
        self.milo.dialog_box.update(dt)

        self.screen.fill((0, 0, 0))
        self.render(dt)
        if not self.shop_system.is_open and not self.milo.dialog_box.is_open:
            self._draw_tool_indicator()
        pygame.display.flip()

        # AI call after flip so the "..." frame is already visible to the player
        if self.milo.dialog_box.has_pending_input:
            user_msg: str = self.milo.dialog_box.get_and_clear_pending()
            response: str = self.milo.send_message(user_msg)
            self.milo.dialog_box.show_response(response)

    def render(self, dt: float) -> None:
        camera_offset: pygame.Vector2 = pygame.Vector2(
            self.camera_system.offset_x,
            self.camera_system.offset_y,
        )

        world_sprite = self.world.get_component('sprite')
        if world_sprite:
            self.render_system.render(self.screen, world_sprite, camera_offset=camera_offset)

        dynamic = sorted(
            (e for e in self.entities if e is not self.world),
            key=lambda e: e.rect.bottom,
        )
        for entity in dynamic:
            sprite = entity.get_component('sprite')
            if sprite is None:
                continue
            self.render_system.render(self.screen, sprite, camera_offset=camera_offset)

        if self.debug_colliders:
            self._draw_colliders()

        self.sky_system.render(self.screen)

        if self.sky_system.is_near_bed(
            pygame.Vector2(self.player.rect.center),
            self.world.bed_position,
        ):
            text: pygame.Surface = self._sleep_font.render(
                'Pressione Z para dormir', True, (255, 255, 255)
            )
            self.screen.blit(
                text,
                (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 160)
            )

        if self.shop_system.is_open:
            self.shop_system.render(self.screen, self.player)
        elif self.milo.dialog_box.is_open:
            pass  # dialog renders below HUD
        elif self._is_facing_trader():
            hint: pygame.Surface = self._sleep_font.render(
                'Pressione F para interagir', True, (255, 255, 255)
            )
            self.screen.blit(
                hint,
                (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 160)
            )
        elif self._is_facing_milo():
            hint = self._sleep_font.render(
                'Pressione F para conversar', True, (255, 255, 255)
            )
            self.screen.blit(
                hint,
                (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 160)
            )

        self.hud_system.render(self.screen, self.player.inventory, self.player)

        if self.milo.dialog_box.is_open:
            self.milo.dialog_box.render(self.screen)

    def _draw_colliders(self) -> None:
        for entity in self.entities:
            colliders = self.collision_system.get_colliders(entity)
            for collider in colliders:
                if collider.layer == LAYER_WORLD:
                    color: tuple[int, int, int] = (255, 0, 0)
                elif collider.layer == LAYER_FARMABLE:
                    color = (255, 220, 0)
                elif collider.layer == LAYER_TOOL:
                    color = (0, 220, 255)
                else:
                    color = (180, 0, 255)

                rect = collider.get_rect()
                screen_pos: pygame.Vector2 = self.camera_system.to_screen(
                    pygame.Vector2(rect.x, rect.y)
                )
                debug_rect = pygame.FRect(screen_pos.x, screen_pos.y, rect.width, rect.height)
                pygame.draw.rect(self.screen, color, debug_rect, 2)

    def _draw_tool_indicator(self) -> None:
        tool_collider = self.player.get_component('tool_collider')
        if tool_collider is None:
            return
        rect = tool_collider.get_rect()
        screen_pos: pygame.Vector2 = self.camera_system.to_screen(
            pygame.Vector2(rect.x, rect.y)
        )
        indicator_rect = pygame.FRect(screen_pos.x, screen_pos.y, rect.width, rect.height)
        pygame.draw.rect(self.screen, (255, 255, 255), indicator_rect, 2)

    def collision_process(self) -> None:
        player_collider: Collider | None = self.player.get_component('collider')
        if player_collider is None:
            return

        for entity in self.entities:
            if entity is self.player:
                continue

            for collider in self.collision_system.get_colliders(entity):
                if not player_collider.can_collide_with(collider):
                    continue

                mtv: pygame.Vector2 | None = get_mtv(
                    player_collider.get_rect(),
                    collider.get_rect()
                )
                if mtv is not None:
                    self.player.rect.x += mtv.x
                    self.player.rect.y += mtv.y

    def _use_hoe(self, tx: int, ty: int) -> None:
        matrix = self.world.matrix_components
        if not (0 <= ty < len(matrix) and 0 <= tx < len(matrix[ty])):
            return
        if matrix[ty][tx].user_data != 'farmable':
            return

        matrix[ty][tx].user_data = 'tilled'
        self.world.remove_component(f'farmable_{tx}_{ty}')

        tilled_surf: pygame.Surface = pygame.image.load(
            'assets/images/soil/x.png'
        ).convert_alpha()
        self.world.surface.blit(tilled_surf, (tx * TILE_SIZE, ty * TILE_SIZE))

        self.player.hoe_tile(tx, ty)

    def _use_water(self, tx: int, ty: int) -> None:
        matrix = self.world.matrix_components
        if not (0 <= ty < len(matrix) and 0 <= tx < len(matrix[ty])):
            return
        if matrix[ty][tx].user_data not in ('tilled', 'tilled_watered'):
            return
        if matrix[ty][tx].user_data == 'tilled_watered':
            return

        matrix[ty][tx].user_data = 'tilled_watered'

        water_surf: pygame.Surface = pygame.image.load(
            'assets/images/soil_water/0.png'
        ).convert_alpha()
        self.world.surface.blit(water_surf, (tx * TILE_SIZE, ty * TILE_SIZE))

        if (tx, ty) in self.plants:
            self.plants[(tx, ty)].is_watered_today = True

    def _plant_seed(self, tx: int, ty: int, seed_name: str) -> bool:
        matrix = self.world.matrix_components
        if not (0 <= ty < len(matrix) and 0 <= tx < len(matrix[ty])):
            return False
        if matrix[ty][tx].user_data != 'tilled':
            return False
        if (tx, ty) in self.plants:
            return False

        plant: Plant = Plant(name=seed_name, tile_pos=(tx, ty))
        self.plants[(tx, ty)] = plant
        self.add_entity(plant)
        return True

    def _harvest_plant(self, tx: int, ty: int) -> bool:
        planta: Plant | None = self.plants.get((tx, ty))
        if planta is None or not planta.is_fully_grown:
            return False

        icon: pygame.Surface = _load_icon(
            f'assets/images/overlay/{planta.name}.png'
        )
        fruto: Item = Item(planta.name, 'fruit', 1, icon)
        self.player.inventory.add_item(fruto)

        self.entities.remove(planta)
        self.plants.pop((tx, ty))

        self.world.matrix_components[ty][tx].user_data = 'tilled'
        soil_surf: pygame.Surface = pygame.image.load(
            'assets/images/soil/x.png'
        ).convert_alpha()
        self.world.surface.blit(soil_surf, (tx * TILE_SIZE, ty * TILE_SIZE))

        return True

    def advance_day(self) -> None:
        dry_surf: pygame.Surface = pygame.image.load(
            'assets/images/soil/x.png'
        ).convert_alpha()

        matrix = self.world.matrix_components
        for row_y in range(len(matrix)):
            for col_x in range(len(matrix[row_y])):
                if matrix[row_y][col_x].user_data == 'tilled_watered':
                    matrix[row_y][col_x].user_data = 'tilled'
                    self.world.surface.blit(dry_surf, (col_x * TILE_SIZE, row_y * TILE_SIZE))

        for plant in self.plants.values():
            plant.advance_day()

    def handle_events(self, input_state: InputState) -> None:
        if self.milo.dialog_box.is_open:
            self.milo.dialog_box.handle_input(input_state)
            return

        if input_state['plant']:
            if self.shop_system.is_open:
                self.shop_system.close()
            elif self._is_facing_trader():
                self.shop_system.open(self.trader.SHOP_CATALOG)
            elif self._is_facing_milo():
                self.milo.open_dialog()

        if input_state['close_shop'] and self.shop_system.is_open:
            self.shop_system.close()

        if self.shop_system.is_open:
            if input_state['arrow_up']:
                self.shop_system.navigate(-1)
            if input_state['arrow_down']:
                self.shop_system.navigate(1)
            if input_state['confirm']:
                self.shop_system.confirm(self.player)
            return

        if input_state['selected_slot'] is not None:
            self.player.inventory.select(input_state['selected_slot'])

        if input_state['use_tool'] and not self.tool_animation_active:
            direction: str = self.player.current_direction
            animation = self.player.get_component('animation')
            tx, ty = self._get_front_tile()

            if self._harvest_plant(tx, ty):
                return

            item = self.player.inventory.get_selected()
            if item is None:
                return

            if item.item_type == 'tool' and item.name == 'hoe':
                animation.set_state(f'{direction}_hoe')
                self.sound_system.play_sound(self.player.get_component('hoe_sound'))
                self.tool_animation_active = True
                self.tool_animation_timer = 0
                self._use_hoe(tx, ty)

            elif item.item_type == 'tool' and item.name == 'water':
                animation.set_state(f'{direction}_water')
                self.sound_system.play_sound(self.player.get_component('water_sound'))
                self.tool_animation_active = True
                self.tool_animation_timer = 0
                self._use_water(tx, ty)

            elif item.item_type == 'seed':
                if self._plant_seed(tx, ty, item.name):
                    self.player.inventory.remove_one(self.player.inventory.selected_index)

        if input_state['next_day']:
            self.advance_day()

        if input_state['sleep']:
            player_center: pygame.Vector2 = pygame.Vector2(self.player.rect.center)
            if self.sky_system.is_near_bed(player_center, self.world.bed_position):
                self.sky_system.advance_day()
                self.advance_day()

        if input_state['toggle_debug']:
            self.debug_colliders = not self.debug_colliders