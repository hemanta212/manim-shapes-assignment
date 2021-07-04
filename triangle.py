from manim import *
from typing import Tuple


class Side(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_near_points_to(self, point, buff: float = 5.0) -> Tuple:
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
        right_point = np.ndarray((input_x_points[0], output_y_points[0], z_coord))
        left_point = np.ndarray((input_x_points[1], output_y_points[1], z_coord))
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


class TriangleGenerator(Scene):
    def construct(self):
        print(0)
        line = Side(LEFT, RIGHT)
        print(1)
        sign = self.get_side_sign(line)
        print(2)
        self.play(Create(line))
        self.play(Create(sign))
        self.wait(4)

    @staticmethod
    def get_side_sign(side: Line, double: bool = False) -> Side:
        # Construct a line 20% size of given side.
        sign_len = 20 / 100.0 * side.get_length()
        print(1.5)
        sign = Side().set_length(sign_len)
        print(1.6)
        sign.align_normally(side)
        print(1.7)
        sign.move_to(side.get_midpoint())
        return sign
