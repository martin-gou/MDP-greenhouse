"""Launch Nav2 for the real MIRTE robot with a saved map.

This launch does not start Gazebo or spawn a simulated robot. It assumes the
real MIRTE robot is already publishing /scan, /tf, /tf_static, and
/mirte_base_controller/odom, and that it accepts velocity commands on
/mirte_base_controller/cmd_vel.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import GroupAction
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import SetRemap
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('mdp_greenhouse_simulation')
    nav2_bringup = FindPackageShare('nav2_bringup')
    nav2_launch = PathJoinSubstitution([
        nav2_bringup,
        'launch',
        'bringup_launch.py',
    ])
    rviz_launch = PathJoinSubstitution([
        nav2_bringup,
        'launch',
        'rviz_launch.py',
    ])
    default_rviz_config = PathJoinSubstitution([
        nav2_bringup,
        'rviz',
        'nav2_default_view.rviz',
    ])
    default_params = PathJoinSubstitution([
        pkg_share,
        'config',
        'nav2_real_mirte_params.yaml',
    ])
    default_map = '/home/spatial-ai/mirte_simulation/info/real_mirte_map.yaml'

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz_config),
        GroupAction([
            SetRemap(src='/cmd_vel', dst='/mirte_base_controller/cmd_vel'),
            SetRemap(src='cmd_vel', dst='/mirte_base_controller/cmd_vel'),
            SetRemap(src='/odom', dst='/mirte_base_controller/odom'),
            SetRemap(src='odom', dst='/mirte_base_controller/odom'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(nav2_launch),
                launch_arguments={
                    'map': LaunchConfiguration('map'),
                    'use_sim_time': LaunchConfiguration('use_sim_time'),
                    'params_file': LaunchConfiguration('params_file'),
                    'autostart': LaunchConfiguration('autostart'),
                    'slam': 'False',
                    'use_composition': 'False',
                }.items(),
            ),
        ]),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rviz_launch),
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            launch_arguments={
                'rviz_config': LaunchConfiguration('rviz_config'),
                'use_namespace': 'false',
            }.items(),
        ),
    ])
