# from kivy.config import Config
# Config.set('graphics','width',1300)
# Config.set('graphics','height',800)
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.graphics import *
from kivy.properties import Clock,ObjectProperty,StringProperty
from kivy.core.window import Window
from kivy import platform
from kivy.uix.relativelayout import RelativeLayout
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
import random
# from kivy.core.window import Window
# Window.size = (1200, 600)
Builder.load_file('menu.kv')
class MainWidget(RelativeLayout):
    from transforms import transform,transform_2D,transform_prespective
    from user_actions import on_touch_down,on_touch_up,_on_keyboard_down,_on_keyboard_up,_keyboard_closed
    menuWidget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    num_v_lines = 10
    line_spacing = 0.2
    vertical_line = []
    
    num_h_lines = 15
    h_line_spacing = 0.2
    horizontal_line = []
    current_offset_y = 0
    current_offset_x = 0
    current_speed = 0
    Speed = 0.8
    Speed_x = 3
    num_tiles = 16
    tile_coord = []
    tiles = []
    tlie_loop = 0
    ship_width = 0.1
    ship_height = 0.035
    base_ship_y = 0.04
    ship = None
    ship_coordinates = [(0,0),(0,0),(0,0)]
    game_over = False
    game_start = False
    label_title = StringProperty('G   A   L   A   X   Y')
    button_title = StringProperty('START')
    score = StringProperty("SCORE:0")
    music1 = None
    galaxy = None
    gameover_impact = None
    begin = None
    restart = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #print("X: "+str(self.width)+" Y: "+str(self.height))
        self.init_audio()
        self.init_v_lines()
        self.init_h_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        Clock.schedule_interval(self.update,1/60)
    def reset_game(self):
        self.current_offset_y = 0
        self.tlie_loop = 0
        self.score = str("SCORE:0")
        self.current_offset_x = 0
        self.current_speed = 0
        self.tile_coord = []
        self.pre_tiles()
        self.generate_tiles()
        self.game_over = False
    def is_desktop(self):
        print(str(platform))
        if platform in ('win','macosx','linux'):
            return True
        return False
    def init_audio(self):
        self.begin = SoundLoader.load("audio/begin.wav")
        self.galaxy = SoundLoader.load("audio/galaxy.wav")
        self.gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.music1 = SoundLoader.load("audio/music1.wav")
        self.restart = SoundLoader.load("audio/restart.wav")
        self.gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.music1.volume = 1
        self.galaxy.volume = 1
        self.gameover_impact.volume = 1
        self.begin.volume = 1
        self.restart.volume = 1
        self.gameover_voice.volume = 1
    def init_v_lines(self):
        with self.canvas:
            for i in range(self.num_v_lines):
                self.vertical_line.append(Line())
    def init_tiles(self):
        with self.canvas:
            Color(1,1,1)
            for i in range(self.num_tiles):
                self.tiles.append(Quad())
    def init_ship(self):
        with self.canvas:
            Color(0,0,0)
            self.ship = Triangle()
    def pre_tiles(self):
        for i in range(10):
            self.tile_coord.append((0,i))
    def generate_tiles(self):
        last_x = 0
        last_y = 0
        for i in range(len(self.tile_coord)-1,-1,-1):
            if self.tile_coord[i][1]< self.tlie_loop:
                del self.tile_coord[i]
        
        if len(self.tile_coord) > 0:
            last_coord = self.tile_coord[-1]
            last_x = last_coord[0]
            last_y = last_coord[1]+1 
        for i in range(len(self.tile_coord),self.num_tiles):
            r = random.randint(0,2)
            start_index = -int(self.num_v_lines/2)+1
            end_index = start_index+self.num_v_lines-1
            if last_x<= start_index:
                r = 1
            if last_x>= end_index:
                r = 2
            self.tile_coord.append((last_x,last_y))
            #0->straight
            #1->right
            #2->left
            if r==1:
                last_x+=1
                self.tile_coord.append((last_x,last_y))
                last_y+=1
                self.tile_coord.append((last_x,last_y))
            if r==2:
                last_x-=1
                self.tile_coord.append((last_x,last_y))
                last_y+=1
                self.tile_coord.append((last_x,last_y))
    def get_line_x_from_index(self,index):
        offset = index - 0.5
        centre_x = self.perspective_point_x
        space = int(self.width*self.line_spacing)
        line_x = centre_x + offset*space + self.current_offset_x
        return line_x
    def get_line_y_from_index(self,index):
        y_pnt = self.h_line_spacing*self.height
        line_y = int(index*y_pnt - self.current_offset_y)
        return line_y
    def get_tile_coordinates(self,tx,ty):
        ty -= self.tlie_loop
        x = self.get_line_x_from_index(tx)
        y = self.get_line_y_from_index(ty)
        return x,y
    def update_tiles(self):
        for i in range(self.num_tiles):
            tile = self.tiles[i]
            tile_coordinates = self.tile_coord[i]
            xmin,ymin = self.get_tile_coordinates(tile_coordinates[0],tile_coordinates[1])
            xmax,ymax = self.get_tile_coordinates(tile_coordinates[0]+1,tile_coordinates[1]+1)
            x1,y1 = self.transform(xmin,ymin)
            x2,y2 = self.transform(xmin,ymax)
            x3,y3 = self.transform(xmax,ymax)
            x4,y4 = self.transform(xmax,ymin)
            
            tile.points = [x1,y1,x2,y2,x3,y3,x4,y4]
    def update_ship(self):
        s_h = self.height * self.ship_height
        s_half_w = self.width * self.ship_width /2
        centre_x = self.width /2 
        base_y = self.height*self.base_ship_y
        self.ship_coordinates[0] = (centre_x-s_half_w,base_y)
        self.ship_coordinates[1] = (centre_x,base_y+s_h)
        self.ship_coordinates[2] = (centre_x+s_half_w,base_y)
        x1,y1 = self.transform(*self.ship_coordinates[0])
        x2,y2 = self.transform(*self.ship_coordinates[1])
        x3,y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1,y1,x2,y2,x3,y3]
    def check_ship_collision(self):
        for i in range(0,len(self.tile_coord)):
            ti_x,ti_y = self.tile_coord[i]
            if ti_y > self.tlie_loop+1:
                return False
            if self.check_ship_collision_with_tile(ti_x,ti_y):
                return True
        return False
    def check_ship_collision_with_tile(self,tx,ty):
        xmin,ymin = self.get_tile_coordinates(tx,ty)
        xmax,ymax = self.get_tile_coordinates(tx+1,ty+1)
        for i in range(0,3):
            px,py = self.ship_coordinates[i]
            if xmin <= px <=xmax and ymin<=py<=ymax:
                return True
        return False
        
    def update_v_lines(self):
        start_index = -int(self.num_v_lines/2)+1
        for i in range(start_index,start_index+self.num_v_lines):
            change_X = self.get_line_x_from_index(i)
            x1,y1 = self.transform(change_X,0)
            x2,y2 = self.transform(change_X,self.height)
            self.vertical_line[i].points = [x1,y1,x2,y2]
    def init_h_lines(self):
        with self.canvas:
            for i in range(self.num_h_lines):
                self.horizontal_line.append(Line())
                
    def update_h_lines(self):
        start_index = -int(self.num_v_lines/2)+1
        end_index = start_index+self.num_v_lines-1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(self.num_h_lines):
            y = self.get_line_y_from_index(i)
            x1,y1 = self.transform(xmin,y)
            x2,y2 = self.transform(xmax,y)
            self.horizontal_line[i].points = [x1,y1,x2,y2]
    
    
    def update(self,dt):
        self.update_v_lines()
        self.update_h_lines()
        self.update_tiles()
        self.update_ship()
        time_factor = dt*60
        if not self.game_over and self.game_start:
            speed_y = self.Speed * self.height /100
            self.current_offset_y += speed_y*time_factor
            y_pnt = self.h_line_spacing*self.height
            while self.current_offset_y>=y_pnt:
                self.current_offset_y-=y_pnt
                self.tlie_loop+=1
                self.score = "SCORE:"+str(self.tlie_loop)
                self.generate_tiles()
            speed_x = self.current_speed * self.height /100
            self.current_offset_x += speed_x*time_factor
        if not self.check_ship_collision() and not self.game_over:
            self.game_over = True
            self.menuWidget.opacity = 1
            self.label_title = "G  A  M  E    O  V  E  R"
            self.button_title = 'RESTART'
            self.music1.stop()
            self.gameover_impact.play()
            Clock.schedule_once(self.game_over_sound,2)
            
    def game_over_sound(self,dt):
        self.gameover_voice.play()
    def start_button(self):
        if self.game_over:
            self.restart.play()
        else:
            self.begin.play()
        self.music1.play()
        self.reset_game()
        self.label_title = "G  A  M  E    O  V  E  R"
        self.button_title = 'RESTART'
        self.game_start = True
        self.menuWidget.opacity = 0
        
class GalaxyApp(App):
    pass
GalaxyApp().run()