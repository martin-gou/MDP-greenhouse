"""Launch the mdp-greenhouse Gazebo world."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    default_world = PathJoinSubstitution([
        FindPackageShare('mirte26_nav'),
        'worlds',
        'mdp_greenhouse.world',
    ])

    gazebo_launch = PathJoinSubstitution([
        FindPackageShare('gazebo_ros'),
        'launch',
        'gazebo.launch.py',
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Gazebo world file to load.',
        ),
        DeclareLaunchArgument(
            'gui',
            default_value='true',
            description='Set to false to run Gazebo headless.',
        ),
        DeclareLaunchArgument(
            'verbose',
            default_value='false',
            description='Set to true for verbose Gazebo output.',
        ),
        DeclareLaunchArgument(
            'pause',
            default_value='false',
            description='Set to true to start Gazebo paused.',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch),
            launch_arguments={
                'world': LaunchConfiguration('world'),
                'gui': LaunchConfiguration('gui'),
                'verbose': LaunchConfiguration('verbose'),
                'pause': LaunchConfiguration('pause'),
            }.items(),
        ),
    ])
