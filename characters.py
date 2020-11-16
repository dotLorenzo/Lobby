import pygame
import yaml
from snap_to_grid import SnaptoGrid
from utils import load_player_img, random_xy, sound

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file)

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
window_wall_width = config['WINDOW_WALL_WIDTH']
player_width = config['PLAYER_WIDTH']
player_height = config['PLAYER_HEIGHT']
grid_spacing = config['GRID_SPACING']
player_vel = config['PLAYER_VELOCITY']
bike_vel = player_vel * config['BIKE_VELOCITY_FACTOR']
bike_sound = config['BIKE_SOUND']
mushroom_sound = config['MUSHROOM_SOUND']


class Player:
    """Create a new player object."""

    def __init__(
        self,
        xy=(50, 70),
        player_id=0,
        username='Noob',
        width=15,
        height=19
    ):
        self.x, self. y = xy
        self.id = player_id
        self.username = username
        self.width = player_width
        self.height = player_height
        self._vel = player_vel  # Non-changing reference.
        self.vel = player_vel
        self.walk_count = 0
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.hit_slow = False  # Slow the players movement in grass/water.
        self.left = False
        self.right = False
        self.up = False
        self.down = True
        self.standing = True
        self.strafe = False
        self.setup_player_sprites()
        self.setup_bike_sprites()
        self.setup_bike_attributes()
        self.setup_mushroom_attributes()

    def setup_player_sprites(self) -> None:
        self.stand_left = load_player_img('left1')
        self.stand_right = load_player_img('right1')
        self.stand_up = load_player_img('up1')
        self.stand_down = load_player_img('down1')

        self.walk_left = [load_player_img('left2'), load_player_img('left3')]
        self.walk_right = [
            load_player_img('right2'), load_player_img('right3')
        ]
        self.walk_up = [load_player_img('up2'), load_player_img('up3')]
        self.walk_down = [load_player_img('down2'), load_player_img('down3')]

    def setup_bike_sprites(self) -> None:
        self.stand_left_bike = load_player_img('bike_left1')
        self.stand_right_bike = load_player_img('bike_right1')
        self.stand_up_bike = load_player_img('bike_up1')

        self.bike_left = [
            load_player_img('bike_left2'), load_player_img('bike_left3')
        ]
        self.bike_right = [
            load_player_img('bike_right2'), load_player_img('bike_right3')
        ]
        self.bike_up = [
            load_player_img('bike_up2'), load_player_img('bike_up3')
        ]
        self.bike_down = [
            load_player_img('bike_down2'), load_player_img('bike_down3')
        ]
        self.stand_down_bike = load_player_img('bike_down1')

    def setup_bike_attributes(self) -> None:
        self.bike = False
        self.bike_vel = bike_vel
        self.bike_sound = sound(bike_sound)

    def setup_mushroom_attributes(self) -> None:
        self.start_mushroom_ticks = 0
        self.mushroom = False
        self.mushroom_sound = sound(mushroom_sound)

    def walk_animation(self, direction, win):
        if not self.hit_slow:
            if not self.mushroom:
                win.blit(direction[self.walk_count//2], (self.x,self.y))
            else:
                self.enlarge(direction[self.walk_count//2], win)
        else: #we are in grass/water
                win.blit(direction[self.walk_count//2], (self.x,self.y), (0,0,SnaptoGrid.snap(self.width),self.height-self.height//4))

        self.walk_count += 1

    def stand_sprite(self, direction, win):
        if not self.hit_slow:
            if not self.mushroom:
                win.blit(direction, (self.x,self.y))
            else:
                self.enlarge(direction, win)
        else:
            if not self.mushroom:
                win.blit(direction, (self.x,self.y), (0,0,SnaptoGrid.snap(self.width),self.height-self.height//4))
            else:
                self.enlarge(direction, win)

    def enlarge(self, direction, win):
        '''scale up the player by 2x'''
        win.blit(pygame.transform.scale2x(direction), (self.x,self.y))

    #we send these attributes from the server to the client for multiplayer
    def attributes(self):
        attrs = {
        'x':self.x,
        'y':self.y,
        'L':self.left,
        'R':self.right,
        'U':self.up,
        'D':self.down,
        'standing':self.standing,
        'walk count':self.walk_count,
        'hit slow':self.hit_slow, #we are in a reduced movement area...chop bottom off
        'bike': self.bike,
        'mushroom': self.mushroom,
        'ID':self.id,
        'username':self.username,
        'map':self.map
        }
        return attrs

    #draw ash onto the screen
    #animate directions
    def draw(self, win):
        if self.walk_count + 1 > 4:
            self.walk_count = 0
        if not self.standing:
            if self.right:
                if self.bike:
                    self.walk_animation(self.bike_right, win)
                else: self.walk_animation(self.walk_right, win)
            elif self.left:
                if self.bike:
                    self.walk_animation(self.bike_left, win)
                else: self.walk_animation(self.walk_left, win)
            elif self.up:
                if self.bike:
                    self.walk_animation(self.bike_up, win)
                else: self.walk_animation(self.walk_up, win)
            elif self.down:
                if self.bike:
                    self.walk_animation(self.bike_down, win)
                else: self.walk_animation(self.walk_down, win)
        else:
            if self.right:
                if self.bike:
                    self.stand_sprite(self.stand_right_bike,win)
                else: self.stand_sprite(self.stand_right,win)
            elif self.left:
                if self.bike:
                    self.stand_sprite(self.stand_left_bike,win)
                else: self.stand_sprite(self.stand_left,win)
            elif self.up:
                if self.bike:
                    self.stand_sprite(self.stand_up_bike,win)
                else: self.stand_sprite(self.stand_up,win)
            elif self.down:
                if self.bike:
                    self.stand_sprite(self.stand_down_bike,win)
                else: self.stand_sprite(self.stand_down,win)



    def move(self, collision_zone, movement_cost_area, bikes=None, mushrooms=None):
        '''move amongst available nodes
            (no movement out of bounds and in object coordinates)
            movement cost in grass / water'''
        keys = pygame.key.get_pressed()
        mca = len(movement_cost_area)

        #simple collision detection:
        #check if player (x,y) is in the set of object coordinates
        #given player dimensions (w=15,h=19) setting +/- grid spacing (1 square) works ok
        bounds = (SnaptoGrid.snap(self.x),SnaptoGrid.snap(self.y+grid_spacing))
        #no movement through walls unless mushroomed
        hit_wall = True if bounds in collision_zone else False
        self.hit_slow = True if bounds in movement_cost_area else False

        if self.hit_slow:
            #slow movement speed
            if not self.mushroom:
                speed = self._vel if not self.bike else self.bike_vel
                slow_speed = speed - movement_cost_area[bounds]
                self.vel = slow_speed
            else:
                self.vel = self._vel if not self.bike else self.bike_vel
        else:
            self.vel = self._vel if not self.bike else self.bike_vel
            #we must re-snap to grid as (x,y) no longer to nearest square
            self.snap()

        if not hit_wall:

            #press s to strafe
            if keys[pygame.K_s]:
                self.strafe = True
            else:
                self.strafe = False
            if keys[pygame.K_LEFT]:
                if self.up and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = True
                    self.down = False
                    self.standing = False
                elif self.down and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = False
                    self.down = True
                    self.standing = False
                else:
                    self.left = True
                    self.right = False
                    self.up = False
                    self.down = False
                    self.standing = False
                    self.direction = 'L'
                self.x -= self.vel
            elif keys[pygame.K_RIGHT]:
                if self.up and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = True
                    self.down = False
                    self.standing = False
                elif self.down and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = False
                    self.down = True
                    self.standing = False
                else:
                    self.left = False
                    self.right = True
                    self.up = False
                    self.down = False
                    self.standing = False
                    self.direction = 'R'
                self.x += self.vel
            elif keys[pygame.K_UP]:
                if self.left and self.strafe:
                    self.left = True
                    self.right = False
                    self.up = False
                    self.down = False
                    self.standing = False
                elif self.right and self.strafe:
                    self.left = False
                    self.right = True
                    self.up = False
                    self.down = False
                    self.standing = False
                else:
                    self.left = False
                    self.right = False
                    self.up = True
                    self.down = False
                    self.standing = False
                    self.direction = 'U'
                self.y -= self.vel
            elif keys[pygame.K_DOWN]:
                if self.left and self.strafe:
                    self.left = True
                    self.right = False
                    self.up = False
                    self.down = False
                    self.standing = False
                elif self.right and self.strafe:
                    self.left = False
                    self.right = True
                    self.up = False
                    self.down = False
                    self.standing = False
                else:
                    self.left = False
                    self.right = False
                    self.up = False
                    self.down = True
                    self.standing = False
                    self.direction = 'D'
                self.y += self.vel
            else:
                self.standing = True
                self.walk_count = 0
        else: #collision
         #self.standing means either:
         #1) we respawned s.t bounds is touching an object, triggering hit_wall = True
         #2) we used mushroom and are not on top of a building
         # --> so find new node...
            if self.standing:
                self.x, self.y = random_xy()
            if self.left: self.x += self.vel
            elif self.right: self.x -= self.vel
            elif self.up: self.y += self.vel
            elif self.down: self.y -= self.vel

        #prevent movement beyond the screen
        #we would normally use self.width but as 10px grid spacing we want to be able to navigate the rightmost square
        if self.x > window_height-window_wall_width-grid_spacing:
            self.x -= self.vel
        elif self.x < 0:
            self.x += self.vel
        elif self.y < 0:
            self.y += self.vel
        elif self.y > window_height-self.height:
            self.y -= self.vel


    def snap(self):
        '''snap player x,y to grid'''
        self.x, self.y = SnaptoGrid.snap(self.x), SnaptoGrid.snap(self.y)
