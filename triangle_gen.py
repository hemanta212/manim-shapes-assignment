import math
import json
from configparser import ConfigParser
from manim import *


class TriangleGenerator(Scene):
    def setup(self):
        # Load settings from config file to dictionary
        self.settings = self.load_configurations()

    def construct(self):
        # Holder for various optional triangle components
        extra_components = []
        # Get the side length from settings
        AB_len, BC_len, CA_len = self.settings.get("side_lengths")
        self.lengths = [AB_len, BC_len, CA_len]

        # Derive angle from sides using the law of cosines
        angle_a = self.get_angle_cosine(CA_len, AB_len, BC_len)
        angle_b = self.get_angle_cosine(AB_len, BC_len, CA_len)
        angle_c = self.get_angle_cosine(BC_len, CA_len, AB_len)
        self.angles = [angle_a, angle_b, angle_c]

        # Create Lines as triangle sides
        AB = Line().set_length(AB_len).next_to(LEFT)
        CA = Line().set_length(CA_len).next_to(LEFT)
        CA.set_angle(angle_a)
        BC = Line(AB.get_end(), CA.get_end())
        self.sides = VGroup(AB, BC, CA)

        # Get side labels
        labels = self.get_side_labels()
        include_side_length = self.settings.get("include_side_length")
        if include_side_length:
            extra_components.append(labels)

        # Get angle signs
        side_lengths = [round(line.get_length(), 2) for line in self.sides]
        self.equal_sides = [i for i in side_lengths if side_lengths.count(i) > 1]
        angle_sign_a, angle_sign_b, angle_sign_c = self.get_angle_signs()
        angle_signs = VGroup(angle_sign_a, angle_sign_b, angle_sign_c)

        # Create side signs
        include_similar = self.settings.get("include_side_similarity")
        if self.equal_sides and include_similar:
            side_signs = self.get_side_signs()
            extra_components.append(side_signs)

        # Load angle label and unit text
        unit = self.settings.get("angle_unit")
        angle_label_a = self.get_angle_label_tex(angle_a, unit=unit)
        angle_label_b = self.get_angle_label_tex(angle_b, unit=unit)
        angle_label_c = self.get_angle_label_tex(angle_c, unit=unit)

        # Position angle labels
        angle_label_a.next_to(angle_sign_a)
        angle_label_b.next_to(angle_sign_b, LEFT)
        angle_label_c.next_to(angle_sign_c, DOWN)
        angle_labels = VGroup(angle_label_a, angle_label_b, angle_label_c)
        include_angle = self.settings.get("include_angle")
        if include_angle:
            extra_components.append(angle_labels)

        # Accumulate all objects to a single triangle VGroup
        triangle = VGroup(self.sides, angle_signs, *extra_components)

        triangle.move_to(ORIGIN)
        rotation_through = self.settings.get("rotation")
        triangle.rotate_in_place(rotation_through * DEGREES)
        self.add(triangle)
        self.wait(5)

    def get_side_labels(self):
        AB, BC, CA = self.sides
        side_unit = self.settings.get("length_unit")
        A, B, C = AB.get_midpoint(), BC.get_midpoint(), CA.get_midpoint()
        label_a = self.get_side_label_tex(AB, unit=side_unit)
        label_b = self.get_side_label_tex(BC, unit=side_unit)
        label_c = self.get_side_label_tex(CA, unit=side_unit)
        label_a.next_to(A, DOWN)
        label_b.next_to(B, RIGHT, buff=0.5)
        label_c.next_to(C, LEFT)
        labels = VGroup(label_a, label_b, label_c)
        return labels

    def get_side_signs(self):
        side_signs = VGroup()
        for line in self.sides:
            similar = Line().scale(0.2)
            similar.set_angle(PI / 2 + line.get_angle())
            line_length = round(line.get_length(), 2)
            if line_length in self.equal_sides:
                similars = VGroup(similar, Line().scale(0.2))
                similars[1].next_to(similar, buff=0.1).set_angle(similar.get_angle())
                similars.move_to(line.get_midpoint())
                side_signs.add(similars)
            else:
                similar.move_to(line.get_midpoint())
                side_signs.add(similar)

        return side_signs

    def get_angle_signs(self):
        """List of Angle obj for denoting angle between lines"""

        # Get side lengths
        AB, BC, CA = self.sides.submobjects
        # Get all three angles
        angle_a, angle_b, angle_c = self.angles

        # Create angle shape using the Angle property
        is_right = lambda x: x == PI / 2
        angle_sign_a = VGroup(Angle(AB, CA, elbow=is_right(angle_a)))
        angle_sign_b = VGroup(
            Angle(AB, BC, quadrant=(-1, 1), other_angle=True, elbow=is_right(angle_a))
        )
        angle_sign_c = VGroup(
            Angle(BC, CA, quadrant=(-1, -1), other_angle=True, elbow=is_right(angle_a))
        )

        angle_signs = [angle_sign_a, angle_sign_b, angle_sign_c]
        include_similar = self.settings.get("include_angle_similarity")
        if not include_similar:
            return angle_signs

        # Append another angle symbol of different radius
        AB_len, BC_len, CA_len = self.lengths
        if CA_len in self.equal_sides:
            angle_sign_b.add(
                Angle(AB, BC, quadrant=(-1, 1), other_angle=True, radius=0.5)
            )

        if BC_len in self.equal_sides:
            angle_sign_a.add(Angle(AB, CA, radius=0.5))

        if AB_len in self.equal_sides:
            angle_sign_c.add(
                Angle(BC, CA, quadrant=(-1, -1), other_angle=True, radius=0.5)
            )

        return angle_signs

    @staticmethod
    def get_angle_label_tex(angle, unit="radian"):
        """
        Gives an angle + unit tex label mobject

        :Params:
        angle: float (in radian)
        unit: str (degree/radian)
        :Returns:
        MathTex Object
        """
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
        """
        Gives an side length + unit tex label mobject

        :Params:
        side: float
        unit: str (cm/m)
        :Returns:
        Text Object
        """
        unit_symb = "cm"
        side = side.get_length()
        if unit == "m":
            side = side / 100.0
            unit_symb = "m"
        rounded_side = round(side, 2)
        tex_string = f"{rounded_side} {unit_symb}"
        label = Text(tex_string).scale(0.5)
        return label

    @staticmethod
    def get_angle_cosine(a, b, c):
        """
        Applies Law of cosines to get the required angle from given sides
        cosA = (C^2 - B^2  - A^2) / (- 2 AB)

        :Params:
        a: first side
        b: second side
        c: third side
        :Returns:
        Angle in Radians
        """
        return math.acos((c ** 2 - b ** 2 - a ** 2) / (-2.0 * a * b))

    @staticmethod
    def load_configurations():
        config_file = "triangle.ini"
        config = ConfigParser()
        config.read(config_file)
        ctx = dict(
            length_unit=config.get("triangle", "length_unit"),
            angle_unit=config.get("triangle", "angle_unit"),
            include_side_length=config.getboolean("triangle", "include_side_length"),
            include_angle=config.getboolean("triangle", "include_angle"),
            include_side_similarity=config.getboolean(
                "triangle", "include_side_similarity"
            ),
            include_angle_similarity=config.getboolean(
                "triangle", "include_side_similarity"
            ),
            rotation=config.getfloat("triangle", "rotation"),
            side_lengths=json.loads(config.get("triangle", "side_lengths")),
        )
        return ctx
