cmake_minimum_required(VERSION 3.8)
project(mirte26_nav)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch rviz worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/scaled_odom.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
