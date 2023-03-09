from turtle import position

from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
from kivy.app import App
import random
from kivy import platform
from kivy.uix.image import Image,AsyncImage
from kivy.core.window import Window

from kivy.graphics import Color, Line, Quad, Triangle

from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up
    menu_widget = ObjectProperty()

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    menu_title = StringProperty("G  A  L  A  X  Y")
    menu_button_title = StringProperty("START")
    score_label = StringProperty("SCORE:0")

    V_NB_LINES = 8
    V_LINES_SPACING = 0.2
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = 0.1   # percentage
    horizontal_lines = []

    SPEED_y = 0.8
    current_offset_y = 0
    current_y_loop = 0

    SPEED_x = 1.3
    current_speed_x = 0
    current_offset_x = 0

    tiles = []
    NB_TILES = 8
    tiles_coordinates = []

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_image = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]
    state_game_over = False
    state_game_has_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice =None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)

        self.init_audio()
        self.sound_galaxy.play()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.init_ship_image()
        self.pre_fill_tile_coordinates()
        self.generate_tile_coordinates()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1 / 60)

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_begin.volume =0.25
        self.sound_galaxy.volume = 0.25
        self.sound_gameover_impact.volume = 0.6
        self.sound_gameover_voice.volume = 0.25
        self.sound_music1.volume = 1
        self.sound_restart.volume = 0.25
        self.sound_music1.loop = True

    def reset_game(self):

        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.tiles_coordinates = []
        self.pre_fill_tile_coordinates()
        self.generate_tile_coordinates()
        self.state_game_over = False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def init_ship(self):
        with self.canvas:
            source="images/shipp.png"
            Color(0, 0, 0,0)

            self.ship = Triangle()

    def init_ship_image(self):
        with self.canvas:
            img = Image(source ="images/shipp1.png")
            self.ship_image =img

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y+20)
        self.ship_coordinates[1] = (center_x, ship_height + base_y+20)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y+20)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])


        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def update_ship_image(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        #self.ship_coordinates[2] = (center_x + ship_half_width , base_y )
        self.ship_coordinates[0] = (center_x- ship_half_width, base_y-base_y)
        x1, y1 = self.transform(*self.ship_coordinates[0])
        self.ship_image.size = (self.SHIP_WIDTH * self.width, self.SHIP_WIDTH * self.width)
        self.ship_image.pos= [x1, y1]


    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop +1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)

        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True

        return False


    def pre_fill_tile_coordinates(self):

        for i in range(0, 10):

            self.tiles_coordinates.append((0, i))


    def generate_tile_coordinates(self):
        last_y = 0
        last_x = 0
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1
        for i in range(len(self.tiles_coordinates)-1,-1,-1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]
        if len(self.tiles_coordinates)>0:
            last_coordinates = self.tiles_coordinates[-1]
            last_y = last_coordinates[1] + 1
            last_x = last_coordinates[0]

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            if last_x >= end_index - 1:
                r = 2
            if last_x <= start_index:
                r = 1
            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1


    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_vertical_lines(self):
        with self.canvas:
            Color(1,1,1)
            # self.Line = Line(points=[100, 0, 100, 100])
            for i in range(0,self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        center_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index-0.5
        line_x = center_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self,index):
        spacing_y = self.H_LINES_SPACING * self.width
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y-self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y



    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_line(self):
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]


    def init_horizontal_lines(self):
        with self.canvas:
            Color(1,1,1)

            for i in range(0,self.H_NB_LINES):
                self.horizontal_lines.append(Line())



    def update_horizontal_line(self):
        startindex = -int(self.V_NB_LINES/2)+1
        end_index = startindex + self.V_NB_LINES-1
        xmin = self.get_line_x_from_index(startindex)
        xmax = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]



    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_line()
        self.update_horizontal_line()
        self.update_tiles()
        self.update_ship_image()
        self.update_ship()
        if not self.state_game_over and self.state_game_has_started:
            self.current_offset_y += self.SPEED_y * self.height/100
            spacing_y = self.H_LINES_SPACING * self.width

            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_label = "SCORE: " + str(self.current_y_loop)
                self.generate_tile_coordinates()

            self.current_offset_x += self.current_speed_x*self.width * time_factor/100

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            self.menu_title = "G  A  M  E     O  V  E  R"
            self.menu_button_title = "RESTART"
            #self.sound_gameover_voice.play()
            Clock.schedule_once(self.play_gameover_voice, 2)
            self.menu_widget.opacity = 1
            print("Game over ")

    def play_gameover_voice(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()


    def on_menu_button_pressed(self):
        print("press")
        if self.menu_button_title == 'START':
            self.sound_begin.play()
        else:
            self.sound_restart.play()

        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0

        self.sound_music1.play()
        print("loader")






class GalaxyApp(App):
    pass


GalaxyApp().run()
