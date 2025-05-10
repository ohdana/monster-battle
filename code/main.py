from settings import *
from support import *
from timer import Timer
from monster import *
from random import choice
from ui import *
from attack import AttackAnimationSprite

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True
        self.import_assets()
        self.player_active = True

        # groups 
        self.all_sprites = pygame.sprite.Group()
        
        # data
        player_monster_list = ['Sparchu', 'Cleaf', 'Jacana', 'Gulfin', 'Pouch', 'Larvea']
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        self.monster = self.player_monsters[0]
        self.all_sprites.add(self.monster)
        opponent_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)
        
        # ui
        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)
        
        # timers
        self.timers = {'player_end': Timer(1000, func = self.opponent_turn), 'opponent_end': Timer(1000, func = self.player_turn)}
        
    def get_input(self, state, data = None):
        if state == 'attack':
            self.apply_attack(self.opponent, data)
            
        elif state == 'heal':
            self.monster.health += 50
            AttackAnimationSprite(self.monster, self.attack_frames['green'], self.all_sprites)
        
        elif state == 'switch':
            self.monster.kill()
            self.monster = data
            self.all_sprites.add(self.monster)
            self.ui.monster = self.monster
            
        elif state == 'escape':
            self.running = False
            
        self.player_active = False
        self.timers['player_end'].activate()
            
    def apply_attack(self, target, attack):
        attack_data = ABILITIES_DATA[attack]
        
        # element
        attack_element = attack_data['element']
        attack_multiplier = ELEMENT_DATA[attack_element][target.element] 
        
        target.health -= attack_data['damage'] * attack_multiplier
        AttackAnimationSprite(target, self.attack_frames[attack_data['animation']], self.all_sprites)
    
    def opponent_turn(self):
        if self.opponent.health <= 0:
            self.player_active = True
            self.opponent.kill()
            monster_name = choice(list(MONSTER_DATA.keys()))
            self.opponent = Opponent(monster_name, self.front_surfs[monster_name], self.all_sprites)
            self.opponent_ui.monster = self.opponent
        else:
            attack = choice(self.opponent.abilities)
            self.apply_attack(self.monster, attack)
            self.timers['opponent_end'].activate()
    
    def player_turn(self):
        self.player_active = True
        if self.monster.health <= 0:
            available_monsters = [monster for monster in self.player_monsters if monster.health > 0]
            if available_monsters:
                self.monster.kill()
                self.monster = available_monsters[0]
                self.all_sprites.add(self.monster)
                self.ui.monster = self.monster
            else:
                self.running = False
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
    def import_assets(self):
        self.front_surfs = folder_importer('images', 'front')
        self.back_surfs = folder_importer('images', 'back')
        self.bg_surfs = folder_importer('images', 'other')
        self.simple_surfs = folder_importer('images', 'simple')
        self.attack_frames = tile_importer(4, 'images', 'attacks')

    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Creature):
                floor_surf = self.bg_surfs['floor']
                floor_rect = floor_surf.get_frect(center = sprite.rect.midbottom + pygame.Vector2(0,-10))
                self.display_surface.blit(floor_surf, floor_rect)
            
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
           
            # update
            self.update_timers()
            self.all_sprites.update(dt)
            if self.player_active:
                self.ui.update()

            # draw  
            self.display_surface.blit(self.bg_surfs['bg'], (0,0))
            self.draw_monster_floor()
            self.all_sprites.draw(self.display_surface)
            self.ui.draw()
            self.opponent_ui.draw()
            pygame.display.update()
        
        pygame.quit()
    
if __name__ == '__main__':
    game = Game()
    game.run()