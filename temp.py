from manim import *

class DecimalTest(Scene):
    def construct(self):
        x_axis = NumberLine(x_min=-5, x_max=5)
        dot = Dot(color=RED, radius=0.15).move_to(x_axis.get_left())
        number = DecimalNumber(-5, color=RED).next_to(dot, UP)

        number.add_updater(lambda m: m.next_to(dot, UP))
        number.add_updater(lambda m: m.set_value(dot.get_center()[0]))

        self.add(x_axis,dot,number)
        self.play(ApplyMethod(dot.shift, RIGHT * 10), rate_func=there_and_back, run_time=10)
        self.wait()
