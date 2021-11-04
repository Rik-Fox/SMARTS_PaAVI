# Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""smarts.core
===========

Core functionality of the SMARTS simulator
"""

import random
import uuid

import numpy as np

from dataclasses import dataclass
from .coordinates import BoundingBox
from .colors import SceneColors


def seed(a):
    random.seed(a)
    np.random.seed(a)


def gen_id():
    """Generates a unique but deterministic id if `smarts.core.seed` has set the core seed."""
    id_ = uuid.UUID(int=random.getrandbits(128))
    return str(id_)[:8]


@dataclass(frozen=True)
class VehicleConfig:
    vehicle_type: str
    color: tuple
    dimensions: BoundingBox
    glb_model: str


# A mapping between SUMO's vehicle types and our internal vehicle config.
# TODO: Don't leak SUMO's types here.
# XXX: The GLB's dimensions must match the specified dimensions here.
# TODO: for traffic histories, vehicle (and road) dimensions are set by the dataset
VEHICLE_CONFIGS = {
    "passenger": VehicleConfig(
        vehicle_type="car",
        color=SceneColors.SocialVehicle.value,
        dimensions=BoundingBox(length=3.68, width=1.47, height=1.4),
        glb_model="simple_car.glb",
    ),
    "bus": VehicleConfig(
        vehicle_type="bus",
        color=SceneColors.SocialVehicle.value,
        dimensions=BoundingBox(length=7, width=2.25, height=3),
        glb_model="bus.glb",
    ),
    "coach": VehicleConfig(
        vehicle_type="coach",
        color=SceneColors.SocialVehicle.value,
        dimensions=BoundingBox(length=8, width=2.4, height=3.5),
        glb_model="coach.glb",
    ),
    "truck": VehicleConfig(
        vehicle_type="truck",
        color=SceneColors.SocialVehicle.value,
        dimensions=BoundingBox(length=5, width=1.91, height=1.89),
        glb_model="truck.glb",
    ),
    "trailer": VehicleConfig(
        vehicle_type="trailer",
        color=SceneColors.SocialVehicle.value,
        dimensions=BoundingBox(length=10, width=2.5, height=4),
        glb_model="trailer.glb",
    ),
    "pedestrian": VehicleConfig(
        vehicle_type="pedestrian",
        color=SceneColors.SocialVehicle.value,
        dimensions=BoundingBox(length=0.5, width=0.5, height=1.6),
        glb_model="pedestrian.glb",
    ),
    "motorcycle": VehicleConfig(
        vehicle_type="motorcycle",
        color=SceneColors.SocialVehicle.value,
        dimensions=BoundingBox(length=2.5, width=1, height=1.4),
        glb_model="motorcycle.glb",
    ),
}

# TODO: Replace VehicleConfigs w/ the VehicleGeometry class
class VehicleGeometry:
    @classmethod
    def fromfile(cls, path, color):
        pass
