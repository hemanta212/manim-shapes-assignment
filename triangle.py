from manim import *
from typing import Tuple


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


class TriangleGenerator(Scene):
    def setup(self):
        self.sides_len = [5.0, 5.0, 2.0]
        self.equal_sides = [i for i in self.sides_len if self.sides_len.count(i) > 1]

    def construct(self):
        triangle = VGroup()
        self.sides = self.get_sides()
        triangle.add(self.sides)

        self.side_signs = self.get_side_signs()
        triangle.add(self.side_signs)

        AB, BC, CA = self.sides
        side_dir_map = {
            AB: DOWN,
            BC: RIGHT,
            CA: LEFT,
        }
        self.labels = self.get_side_labels(side_dir_map)
        triangle.add(self.labels)
        triangle.move_to(ORIGIN)
        self.play(Create(triangle))

    def get_sides(self) -> VGroup:
        """
        Constructs 3 closed lines of specified lengths to form triangle

        :Returns:
        VGroup of sides
        """
        AB_len, BC_len, CA_len = self.sides_len
        # Derive angle from sides using the law of cosines
        angle_a = self.get_angle_cosine(CA_len, AB_len, BC_len)
        # Create Lines as triangle sides
        AB = Side().set_length(AB_len).next_to(LEFT)
        CA = Side().set_length(CA_len).next_to(LEFT)
        CA.set_angle(angle_a)
        BC = Side(AB.get_end(), CA.get_end()).set_length(BC_len)
        assert BC.get_length() == BC_len
        return VGroup(AB, BC, CA)

    def get_side_signs(self) -> VGroup:
        """
        For a given triangle's 3 sides, return VGroup of equality signs
        """
        signs = VGroup()
        for side in self.sides:
            double = False
            side_len = side.get_length()
            if self.equal_sides and side_len in self.equal_sides:
                double = True
            side_sign = self.get_side_sign(side, double=double)
            signs.add(side_sign)
        return signs

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
        labels = VGroup()
        for side in self.sides:
            unit = "m"
            label = self.gen_side_label_text(side, unit=unit)
            direction = side_dir_map[side]
            label.next_to(side.get_midpoint(), direction, buff=0.3)
            labels.add(label)
        return labels

    @staticmethod
    def gen_side_label_text(side: Side, unit: str = "cm"):
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
        return np.arccos((c ** 2 - b ** 2 - a ** 2) / (-2.0 * a * b))
