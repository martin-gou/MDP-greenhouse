"""Launch simulation Cartographer with intentionally bad odometry."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('mdp_greenhouse_simulation')
    sim_launch = PathJoinSubstitution([
        pkg_share,
        'launch',
        'greenhouse_mirte_master.launch.py',
    ])
    cartographer_config_dir = PathJoinSubstitution([
        pkg_share,
        'config',
    ])
    rviz_config = PathJoinSubstitution([
        pkg_share,
        'rviz',
        'greenhouse_cartographer.rviz',
    ])

    use_sim_time = LaunchConfiguration('use_sim_time')
    resolution = LaunchConfiguration('resolution')
    publish_period_sec = LaunchConfiguration('publish_period_sec')
    use_rviz = LaunchConfiguration('use_rviz')
    odom_scale = LaunchConfiguration('odom_scale')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('verbose', default_value='false'),
        DeclareLaunchArgument('pause', default_value='false'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('resolution', default_value='0.05'),
        DeclareLaunchArgument('publish_period_sec', default_value='1.0'),
        DeclareLaunchArgument('odom_scale', default_value='3.0'),
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
            }.items(),
        ),
        Node(
            package='mdp_greenhouse_simulation',
            executable='scaled_odom.py',
            name='scaled_odom',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'scale': odom_scale,
                'input_topic': '/odom',
                'output_topic': '/bad_odom',
                'output_frame': 'bad_odom',
                'child_frame': 'base_link',
                'publish_tf': True,
            }],
        ),
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=[
                '-configuration_directory',
                cartographer_config_dir,
                '-configuration_basename',
                'mirte_2d_bad_odom.lua',
            ],
            remappings=[
                ('odom', '/bad_odom'),
            ],
        ),
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=[
                '-resolution',
                resolution,
                '-publish_period_sec',
                publish_period_sec,
            ],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            condition=IfCondition(use_rviz),
            output='screen',
        ),
    ])
