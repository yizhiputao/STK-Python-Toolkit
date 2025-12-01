"""
直接使用固定参数创建单颗卫星的示例脚本。
"""

import os
import sys
from typing import Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from stk_toolkit import STKConnection
from stk_toolkit.components import SatelliteComponent
from stk_toolkit.components.satellite import PropagatorType

SATELLITE_NAME = "Satellite2"
DELETE_EXISTING_BEFORE_CREATE = True

ORBIT_PARAMS: Dict[str, float] = {
    "semi_major_axis": 7218.137,
    "eccentricity": 1.5e-6,
    "inclination": 97.5591,
    "raan": 320.4248,
    "arg_of_perigee": 0.0,
    "true_anomaly": 180.0,
    "step": 60.0,
}


def main():
    with STKConnection() as connection:
        if DELETE_EXISTING_BEFORE_CREATE and SatelliteComponent.exists(connection, SATELLITE_NAME):
            if SatelliteComponent.delete_by_name(connection, SATELLITE_NAME):
                print(f"已删除存在的卫星：{SATELLITE_NAME}")

        satellite = SatelliteComponent(connection, SATELLITE_NAME)
        satellite.create(
            propagator=PropagatorType.J2_PERTURBATION,
            semi_major_axis=ORBIT_PARAMS["semi_major_axis"],
            eccentricity=ORBIT_PARAMS["eccentricity"],
            inclination=ORBIT_PARAMS["inclination"],
            raan=ORBIT_PARAMS["raan"],
            arg_of_perigee=ORBIT_PARAMS["arg_of_perigee"],
            true_anomaly=ORBIT_PARAMS["true_anomaly"],
            step=ORBIT_PARAMS["step"],
        )

        info = satellite.get_info()
        print(f"{SATELLITE_NAME} 已创建：")
        for key, value in info.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

