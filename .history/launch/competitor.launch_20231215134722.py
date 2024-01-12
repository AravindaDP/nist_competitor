import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import LaunchConfiguration

from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
)

from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):

    urdf = os.path.join(get_package_share_directory(
        "ariac_description"), "urdf/ariac_robots/ariac_robots.urdf.xacro")

    moveit_config = (
        MoveItConfigsBuilder(
            "ariac_robots", package_name="ariac_moveit_config")
        .robot_description(urdf)
        .robot_description_semantic(file_path="config/ariac_robots.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    # Test Competitor node
    test_competitor = Node(
        package="nist_competitor",
        executable="competitor",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            {"use_sim_time": True},
        ],
        arguments=['--ros-args', '--log-level', 'move_group_interface:=warn', '--log-level',
                   'moveit_trajectory_processing.time_optimal_trajectory_generation:=error']
    )

    nodes_to_start = [
        test_competitor,
    ]

    return nodes_to_start


def generate_launch_description():
    declared_arguments = []

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])