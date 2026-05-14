# mirte26_nav

Gazebo Classic simulation package for the `mdp-greenhouse` default greenhouse layout, with launch files for:

- greenhouse world only
- greenhouse world with MIRTE Master
- Cartographer mapping
- Nav2 navigation using a saved map

The simulated greenhouse is based on the `mdp-greenhouse` default map:

- greenhouse size: `5 m x 10 m`
- 4 outside walls
- 12 table/shelf obstacles
- default MIRTE start pose: `x=2.5`, `y=0.8`, `yaw=1.5708`

## Build

From the workspace root:

```bash
cd /home/spatial-ai/mirte_simulation
colcon build --packages-select mirte26_nav
```

Source both workspaces before running launches:

```bash
source /home/spatial-ai/ws/install/setup.bash
source /home/spatial-ai/mirte_simulation/install/setup.bash
```

## Launch Greenhouse Only

```bash
ros2 launch mirte26_nav greenhouse_simulation.launch.py
```

Headless:

```bash
ros2 launch mirte26_nav greenhouse_simulation.launch.py gui:=false
```

## Launch Greenhouse With MIRTE

```bash
ros2 launch mirte26_nav greenhouse_mirte_master.launch.py
```

Change the robot start pose:

```bash
ros2 launch mirte26_nav greenhouse_mirte_master.launch.py \
  x:=2.5 y:=0.8 yaw:=1.5708
```

For manual teleop in this launch, use the MIRTE controller topic:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel_unstamped
```

## Build A Map With Cartographer

Launch Gazebo, MIRTE, Cartographer, and RViz:

```bash
ros2 launch mirte26_nav greenhouse_mirte_cartographer.launch.py
```

RViz opens by default and shows the live map, laser scan, TF, and robot model.

Drive the robot around with teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel_unstamped
```

## Test Cartographer With Bad Odometry

This launch is for simulation experiments only. It starts the greenhouse simulation, creates a fake odometry topic `/bad_odom`, and scales the normal simulation odometry by `3.0` before giving it to Cartographer.

```bash
ros2 launch mirte26_nav greenhouse_mirte_cartographer_test.launch.py
```

Change the scale factor:

```bash
ros2 launch mirte26_nav greenhouse_mirte_cartographer_test.launch.py odom_scale:=3.0
```

Teleop is the same as the normal simulation mapping launch:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel_unstamped
```

The test launch publishes:

```text
/bad_odom
bad_odom -> base_link
```

Cartographer then uses `/bad_odom` instead of `/odom`, so you can observe how bad odometry affects mapping.

When the map looks good, save it:

```bash
mkdir -p /home/spatial-ai/mirte_simulation/info
cd /home/spatial-ai/mirte_simulation/info
ros2 run nav2_map_server map_saver_cli -f my_map
```

This creates:

```text
/home/spatial-ai/mirte_simulation/info/my_map.yaml
/home/spatial-ai/mirte_simulation/info/my_map.pgm
```

## Launch Navigation With The Saved Map

The navigation launch defaults to:

```text
/home/spatial-ai/mirte_simulation/info/my_map.yaml
```

Run:

```bash
ros2 launch mirte26_nav greenhouse_mirte_navigation.launch.py
```

This starts:

- Gazebo greenhouse world
- MIRTE Master
- Nav2 map server
- AMCL localization
- Nav2 planner/controller/behavior tree
- RViz

In RViz:

1. Check that the robot is correctly localized on the map.
2. If needed, use **2D Pose Estimate** to reset the robot pose.
3. Use **Nav2 Goal** to send a navigation goal.

During Nav2 navigation, Nav2 publishes directly to `/cmd_vel`. If you want to manually test movement while this launch is running, use teleop without remapping:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Launch Navigation With Your Own Map

Use the `map` launch argument:

```bash
ros2 launch mirte26_nav greenhouse_mirte_navigation.launch.py \
  map:=/absolute/path/to/your_map.yaml
```

Example:

```bash
ros2 launch mirte26_nav greenhouse_mirte_navigation.launch.py \
  map:=/home/spatial-ai/mirte_simulation/info/my_map.yaml
```

The `.yaml` file must point to the matching `.pgm` image. If the YAML says `image: my_map.pgm`, keep both files in the same directory.

## REAL_MIRTE Commands

Use this section when this machine is connected to the real MIRTE robot over ROS 2 and can see/publish the robot topics. Do not launch Gazebo for the real robot.

Source the workspace:

```bash
source /home/spatial-ai/ws/install/setup.bash
source /home/spatial-ai/mirte_simulation/install/setup.bash
```

Check that this machine can see the robot topics:

```bash
ros2 topic list
```

Important real MIRTE topics from the saved topic list:

```text
/scan
/tf
/tf_static
/robot_description
/joint_states
/mirte_base_controller/cmd_vel
/mirte_base_controller/odom
```

### Real Robot Teleop

For the real robot, publish velocity commands to `/mirte_base_controller/cmd_vel`:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel
```

### Build A Real Map

Run Cartographer on the real robot topics. This launch does not start Gazebo and uses real time.

```bash
ros2 launch mirte26_nav real_mirte_cartographer.launch.py
```

Drive the real robot slowly with teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel
```

When the map looks good in RViz, save it:

```bash
mkdir -p /home/spatial-ai/mirte_simulation/info
cd /home/spatial-ai/mirte_simulation/info
ros2 run nav2_map_server map_saver_cli -f real_mirte_map
```

This creates:

```text
/home/spatial-ai/mirte_simulation/info/real_mirte_map.yaml
/home/spatial-ai/mirte_simulation/info/real_mirte_map.pgm
```

### Load Real Navigation With A Saved Map

Start Nav2 with the real map and real time. This launch does not start Gazebo. It remaps Nav2 velocity output to `/mirte_base_controller/cmd_vel` and odometry subscriptions to `/mirte_base_controller/odom`.

```bash
ros2 launch mirte26_nav real_mirte_navigation.launch.py \
  map:=/home/spatial-ai/mirte_simulation/info/real_mirte_map.yaml
```

In RViz:

1. Use **2D Pose Estimate** to set the robot pose on the map.
2. Use **Nav2 Goal** to send a navigation target.

Important: this launch remaps Nav2 `/cmd_vel` to `/mirte_base_controller/cmd_vel`. If the robot does not move, check:

```bash
ros2 topic info /cmd_vel
ros2 topic info /mirte_base_controller/cmd_vel
```

The real robot must receive Nav2 velocity commands on `/mirte_base_controller/cmd_vel`.

## Useful Options

Run navigation without RViz:

```bash
ros2 launch mirte26_nav greenhouse_mirte_navigation.launch.py use_rviz:=false
```

Run navigation without Gazebo GUI:

```bash
ros2 launch mirte26_nav greenhouse_mirte_navigation.launch.py gui:=false
```

Start the robot at a different pose:

```bash
ros2 launch mirte26_nav greenhouse_mirte_navigation.launch.py \
  x:=2.5 y:=1.0 yaw:=1.5708
```

## Files

```text
launch/greenhouse_simulation.launch.py
launch/greenhouse_mirte_master.launch.py
launch/greenhouse_mirte_cartographer.launch.py
launch/greenhouse_mirte_cartographer_test.launch.py
launch/greenhouse_mirte_navigation.launch.py
launch/real_mirte_cartographer.launch.py
launch/real_mirte_navigation.launch.py
worlds/mdp_greenhouse.world
config/mirte_2d.lua
config/mirte_2d_bad_odom.lua
config/real_mirte_2d.lua
config/nav2_mirte_params.yaml
config/nav2_real_mirte_params.yaml
rviz/greenhouse_cartographer.rviz
```

## Notes

- Simulation Cartographer mapping uses `/scan`, `/odom`, and the MIRTE TF tree.
- Real MIRTE Cartographer mapping ignores wheel odometry and uses lidar scan matching because the real odometry can be inaccurate.
- Mapping/manual teleop uses `/mirte_base_controller/cmd_vel_unstamped`.
- Nav2 navigation uses `/cmd_vel` directly.
- If Gazebo says the master port is already in use, stop the old Gazebo process or launch with a different `GAZEBO_MASTER_URI`.
