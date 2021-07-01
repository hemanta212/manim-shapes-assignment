import math
import json
from functools import partial
from configparser import ConfigParser
from manim import *

class TriangleGenerator(Scene):

    def setup(self):
        self.ctx = self.load_configurations()

    def construct(self):
        AB_len, BC_len, CA_len = json.loads(self.ctx('side_lengths'))

        angle_a = self.get_angle_cosine(CA_len, AB_len, BC_len)
        angle_b = self.get_angle_cosine(AB_len, BC_len, CA_len)
        angle_c = self.get_angle_cosine(BC_len, CA_len, AB_len)
        
        AB = Line(color=YELLOW).set_length(AB_len).next_to(LEFT)
        CA = Line(color=RED).set_length(CA_len).next_to(LEFT)
        CA.set_angle(angle_a)
        BC = Line(AB.get_end(), CA.get_end())
        self.add(AB, BC, CA)

        A, B, C = AB.get_midpoint(), BC.get_midpoint(), CA.get_midpoint()
        # label_a, label_b, label_c = (Text(i, size=0.5) for i in "A B C".split())
        label_a = self.get_side_label_tex(AB)
        label_a.next_to(A, DOWN)
        label_b.next_to(B, RIGHT, buff=0.5)
        label_c.next_to(C, LEFT)
        labels = VGroup(label_a, label_b, label_c)
        self.add(labels)

        angle_sign_a = Angle(AB, CA)
        angle_sign_b = Angle(AB, BC, quadrant=(-1, 1), other_angle=True)
        angle_sign_c = Angle(BC, CA, quadrant=(-1, -1), other_angle=True)
        self.add(angle_sign_a, angle_sign_b, angle_sign_c)

        angle_label_a = self.get_angle_label_tex(angle_a, unit="degree")
        angle_label_b = self.get_angle_label_tex(angle_b, unit="degree")
        angle_label_c = self.get_angle_label_tex(angle_c, unit="degree")

        angle_label_a.next_to(angle_sign_a)
        angle_label_b.next_to(angle_sign_b, LEFT)
        angle_label_c.next_to(angle_sign_c, DOWN)
        self.add(angle_label_a, angle_label_b, angle_label_c)
       
        for line in (AB, BC, CA):
            similar_angle_sign = Line().scale(0.2)
            similar_angle_sign.set_angle(PI/2 + line.get_angle())
            similar_angle_sign.move_to(line.get_midpoint())
            self.add(similar_angle_sign)

        self.wait(5)

    @staticmethod
    def get_angle_label_tex(angle, unit="radian"):
        '''
        Gives an angle + unit tex label mobject

        :Params:
        angle: float (in radian)
        unit: str (degree/radian)
        :Returns:
        MathTex Object
        '''
        unit_symb = r"^c"
        if unit == "degree":
            angle = math.degrees(angle)
            unit_symb = r"^\circ"
        round_angle = round(angle, 2)
        tex_string = f"{round_angle}{unit_symb}"
        tex = MathTex(tex_string).scale(0.5)
        return tex

    @staticmethod
    def get_side_label_tex(side, unit="cm"):
        '''
        Gives an side length + unit tex label mobject

        :Params:
        side: float 
        unit: str (cm/m)
        :Returns:
        MathTex Object
        '''
        unit_symb = "cm"
        if unit == "m":
            side = side/100.0
            unit_symb = "m"
        rounded_side = round(side, 2)
        tex_string = f"{rounded_side} {unit_symb}"
        label = Text(tex_string).scale(0.5)
        return label

    @staticmethod
    def get_angle_cosine(a,b,c):
        '''
        Applies Law of cosines to get the required angle from given sides
        cosA = (C^2 - B^2  - A^2) / (- 2 AB)

        :Params:
        a: first side
        b: second side
        c: third side
        :Returns:
        Angle in Radians
        '''
        return math.acos((c**2 - b**2 - a**2)/(-2.0 * a * b))

    @staticmethod
    def load_configurations():
        config_file = "triangle.ini"
        config = ConfigParser()
        config.read(config_file)
        ctx = partial(config.get, 'triangle')
        return ctx;
        
