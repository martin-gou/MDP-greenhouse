"""Launch greenhouse + MIRTE Master + Nav2 using a saved map."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('mdp_greenhouse_simulation')
    sim_launch = PathJoinSubstitution([
        pkg_share,
        'launch',
        'greenhouse_mirte_master.launch.py',
    ])
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
        'nav2_mirte_params.yaml',
    ])
    default_map = '/home/spatial-ai/mirte_simulation/info/my_map.yaml'

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz_config),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('verbose', default_value='false'),
        DeclareLaunchArgument('pause', default_value='false'),
        DeclareLaunchArgument('x', default_value='2.5'),
        DeclareLaunchArgument('y', default_value='0.8'),
        DeclareLaunchArgument('z', default_value='0.05'),
        DeclareLaunchArgument('roll', default_value='0.0'),
        DeclareLaunchArgument('pitch', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='1.5708'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sim_launch),
            launch_arguments={
                'gui': LaunchConfiguration('gui'),
                'verbose': LaunchConfiguration('verbose'),
                'pause': LaunchConfiguration('pause'),
                'x': LaunchConfiguration('x'),
                'y': LaunchConfiguration('y'),
                'z': LaunchConfiguration('z'),
                'roll': LaunchConfiguration('roll'),
                'pitch': LaunchConfiguration('pitch'),
                'yaw': LaunchConfiguration('yaw'),
                'use_twist_mux': 'false',
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'map': LaunchConfiguration('map'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': LaunchConfiguration('params_file'),
                'autostart': LaunchConfiguration('autostart'),
                'use_rviz': LaunchConfiguration('use_rviz'),
                'slam': 'False',
                'use_composition': 'False',
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rviz_launch),
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            launch_arguments={
                'rviz_config': LaunchConfiguration('rviz_config'),
                'use_namespace': 'false',
            }.items(),
        ),
    ])
