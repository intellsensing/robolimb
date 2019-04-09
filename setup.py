""" Setup script for robolimb package. """

from setuptools import setup

setup(
    name = "robolimb",
    version = "0.0.1",
    author = "Agamemnon Krasoulis",
    description = ("Interface the Touch Bionics (Össur) RoboLimb " + \
                   "prosthetic/robotic hand in Python via CAN."),
    url = "https://github.com/agamemnonc/robolimb",
    packages=['robolimb']
)