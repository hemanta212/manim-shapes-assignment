import os
import json
from configparser import ConfigParser
from typing import Tuple
from manim import *


class Side(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_near_points_to(self, point, buff: float = 0.7) -> Tuple:
        """
        Returns two near points on either side of a point of a 2d line

        :Params:
        point: Any point on locus of line to take reference to
        buff: Percentage of length of line to keep distance with given point

        :Returns:
        (left_point, right_point) : where a point is [x,y,z]
        """

        slope = self.get_slope()
        x_coord, y_coord, z_coord = point
        # Translate buff from percent to length in units
        buff_len = buff / 100.0 * self.get_length()
        # Given a x point calculate y value from slope point form equation
        image_of_x = lambda x: slope * (x - x_coord) + y_coord
        # Gather 2 input x-points on either side of given points to input to eqn
        input_x_points = x_coord + buff_len, x_coord - buff_len
        # Generate correspoding y points for given x input
        output_y_points = [image_of_x(i) for i in input_x_points]
        # Generate3 (x,y,z) point on either side of given point from above info
        right_point = (input_x_points[0], output_y_points[0], z_coord)
        left_point = (input_x_points[1], output_y_points[1], z_coord)
        return (left_point, right_point)

    def align_normally(self, line: Line):
        """
        Aligns itself perpendicular to the given reference line

        :Params:
        line: Any point on locus of line to take reference to
        """
        given_slope = float(line.get_slope())
        new_slope = -1 / given_slope if given_slope != 0 else np.Infinity
        normal_angle = np.arctan(new_slope)
        self.set_angle(normal_angle)

    def get_length(self):
        return round(super().get_length(), 2)

    def angle_with(self, line: Line):
        """Return the angle in radian that a line makes with given line"""
        return np.absolute(self.get_angle() - line.get_angle())


class Setting:
    def __init__(self, config_file):
        assert os.path.exists(config_file)
        config = ConfigParser()
        config.read(config_file)

        self.include_side_length = config.getboolean("triangle", "include_side_length")
        self.include_angle = config.getboolean("triangle", "include_angle")
        self.include_side_similarity = config.getboolean(
            "triangle", "include_side_similarity"
        )
        self.include_angle_similarity = config.getboolean(
            "triangle", "include_angle_similarity"
        )
        self.rotation = config.getfloat("triangle", "rotation")
        self.length_units = config.get("triangle", "length_units").split(" ")
        print(self.length_units)
        self.angle_units = config.get("triangle", "angle_units").split(" ")
        print(self.angle_units)
        # Validate unit options
        self.validate_units()

        self.side_lengths = json.loads(config.get("triangle", "side_lengths"))
        self.validate_sides()

    def validate_units(self):
        # validate the sides of triangle
        assert len(self.angle_units) == 3 and len(self.length_units) == 3
        for a_unit in self.angle_units:
            assert a_unit == "radian" or a_unit == "degrees"
        for l_unit in self.length_units:
            assert l_unit == "cm" or l_unit == "m"

    def validate_sides(self):
        # validate the sides of triangle
        assert len(self.side_lengths) == 3
        assert None not in self.side_lengths
        A, B, C = self.side_lengths
        assert A + B > C and B + C > A and C + A > B


class TriangleGenerator(Scene):
    def setup(self):
        self.settings = Setting("triangle.ini")
        sides_len = self.settings.side_lengths
        self.equal_sides = [i for i in sides_len if sides_len.count(i) > 1]

    def construct(self):
        triangle = VGroup()
        # Get all 3 angles of triangle
        self.angles = self.get_angles()

        # Generate side Lines of triangle
        self.sides = self.get_sides()
        triangle.add(self.sides)

        # Get equality signs for triangle sides
        self.side_signs = self.get_side_signs()
        if self.settings.include_side_similarity:
            triangle.add(self.side_signs)

        # Generate side length and unit labels beside each side
        AB, BC, CA = self.sides
        side_dir_map = {
            AB: DOWN,
            BC: RIGHT,
            CA: LEFT,
        }
        self.labels = self.get_side_labels(side_dir_map)
        if self.settings.include_side_length:
            triangle.add(self.labels)

        # Generate and position the angle signs
        angle_side_quad_map = {
            AB: [(BC, CA), (-1, -1)],
            BC: [(AB, CA), (1, 1)],
            CA: [(AB, BC), (-1, 1)],
        }
        self.angle_signs = self.get_angle_signs(angle_side_quad_map)
        if self.settings.include_angle:
            triangle.add(self.angle_signs)

        # Generate and position the angle labels
        sign_c, sign_a, sign_b = self.angle_signs
        angle_a, angle_b, angle_c = self.angles
        sign_angle_map = {
            sign_a: angle_a,
            sign_b: angle_b,
            sign_c: angle_c,
        }
        figure_center = triangle.get_center_of_mass()
        angle_labels = self.get_angle_labels(sign_angle_map, figure_center)
        if self.settings.include_angle:
            triangle.add(angle_labels)

        # Reset triangle position
        triangle.move_to(ORIGIN)
        triangle.rotate_in_place(self.settings.rotation * DEGREES)
        self.add(triangle)

    def get_sides(self) -> VGroup:
        """
        Constructs 3 closed lines of specified lengths to form triangle

        :Returns:
        VGroup of sides
        """
        AB_len, BC_len, CA_len = self.settings.side_lengths
        angle_a = self.angles[0]
        # Create Lines as triangle sides
        AB = Side().set_length(AB_len).next_to(LEFT)
        CA = Side().set_length(CA_len).next_to(LEFT)
        CA.set_angle(angle_a)
        BC = Side(AB.get_end(), CA.get_end()).set_length(BC_len)
        assert BC.get_length() == BC_len
        return VGroup(AB, BC, CA)

    def get_angles(self) -> Tuple:
        # Derive angle from sides using the law of cosines
        AB_len, BC_len, CA_len = self.settings.side_lengths
        angle_a = self.get_angle_cosine(CA_len, AB_len, BC_len)
        angle_b = self.get_angle_cosine(AB_len, BC_len, CA_len)
        angle_c = self.get_angle_cosine(BC_len, CA_len, AB_len)
        assert angle_a + angle_b + angle_c == PI
        return (angle_a, angle_b, angle_c)

    def get_side_signs(self) -> VGroup:
        """
        For a given triangle's 3 sides, return VGroup of equality signs
        """
        signs = VGroup()
        for side in self.sides:
            double = False
            side_len = side.get_length()
            if self.equal_sides and side_len not in self.equal_sides:
                double = True
            side_sign = self.get_side_sign(side, double=double)
            signs.add(side_sign)
        return signs

    def get_angle_signs(self, angle_side_quad_map: dict) -> VGroup:
        """
        For a given triangle's 3 angles, return VGroup of angle symbols
        """
        angle_signs = VGroup()
        for side, (lines, quadrant) in angle_side_quad_map.items():
            double = False
            double_allowed = self.settings.include_angle_similarity
            # if side is not in equal sides then its corresponding angle will be double signed
            side_len = side.get_length()
            double_present = self.equal_sides and side_len not in self.equal_sides
            if double_allowed and double_present:
                double = True
            angle_sign = self.get_angle_sign(lines, quadrant, double=double)
            angle_signs.add(angle_sign)
        return angle_signs

    def get_angle_sign(
        self, lines: list, quadrant: Tuple[int, int], double: bool = False
    ) -> VGroup:
        "Get an Angle symbol for a given pair of adjacent line"
        is_right = lines[0].angle_with(lines[1]) == PI / 2
        other_angle = -1 in quadrant
        make_angle_with_radius = lambda x: Angle(
            *lines, elbow=is_right, quadrant=quadrant, other_angle=other_angle, radius=x
        )
        angle_sign = make_angle_with_radius(None)
        angle_signs = VGroup(angle_sign)
        if double:
            angle_signs.add(make_angle_with_radius(0.5))

        return angle_signs

    @staticmethod
    def get_side_sign(side: Side, double: bool = False) -> VGroup:
        """
        Generates equality signs of triangle.
        """
        sign = Side().scale(0.15)
        sign.align_normally(side)
        signs = VGroup(sign)
        if double:
            signs.add(sign.copy())
            r_point, l_point = side.get_near_points_to(side.get_midpoint())
            sign.move_to(r_point)
            signs[1].move_to(l_point)
        else:
            sign.move_to(side.get_midpoint())

        return signs

    def get_side_labels(self, side_dir_map: dict) -> VGroup:
        """
        Generate side labels VGroup containing length of side and specified unit.
        """
        labels = VGroup()
        units = self.settings.length_units
        for side, unit in zip(self.sides, units):
            label = self.gen_side_label_text(side, unit=unit)
            direction = side_dir_map[side]
            label.next_to(side.get_midpoint(), direction, buff=0.3)
            labels.add(label)
        return labels

    def get_angle_labels(self, sign_angle_map: dict, fig_center) -> VGroup:
        """
        Generate angle labels VGroup containing length of side and specified unit.
        """
        labels = VGroup()
        units = self.settings.angle_units
        for (sign, angle), unit in zip(sign_angle_map.items(), units):
            label = self.gen_angle_label_tex(angle, unit=unit)
            direction = Side(sign.get_center_of_mass(), fig_center).get_unit_vector()
            label.next_to(sign.get_center_of_mass(), direction=direction)
            labels.add(label)
        return labels

    @staticmethod
    def gen_side_label_text(side: Side, unit: str = "cm") -> Mobject:
        """
        Gives an side length + unit tex label mobject

        :Params:
        side: Side
        unit: str (cm/m)
        :Returns:
        Text Object
        """
        unit_symb = "cm"
        side_len = side.get_length()
        if unit == "m":
            side_len = side_len / 100.0
            unit_symb = "m"
        rounded_side = round(side_len, 2)
        tex_string = f"{rounded_side} {unit_symb}"
        label = Text(tex_string).scale(0.6)
        return label

    @staticmethod
    def gen_angle_label_tex(angle: float, unit: str = "radian") -> Mobject:
        """
        Gives an angle + unit tex label mobject

        :Params:
        angle: float (in radian)
        unit: str (degree/radian)
        :Returns:
        MathTex Object
        """
        unit_symb = r"^c"
        if unit == "degrees":
            angle = np.degrees(angle)
            unit_symb = r"^\circ"
        round_angle = round(angle, 2)
        tex_string = f"{round_angle}{unit_symb}"
        tex = MathTex(tex_string).scale(0.5)
        return tex

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
        return np.arccos((c ** 2 - b ** 2 - a ** 2) / (-2.0 * a * b))
