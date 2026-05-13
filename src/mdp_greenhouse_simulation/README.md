# mdp_greenhouse_simulation

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
colcon build --packages-select mdp_greenhouse_simulation
```

Source both workspaces before running launches:

```bash
source /home/spatial-ai/ws/install/setup.bash
source /home/spatial-ai/mirte_simulation/install/setup.bash
```

## Launch Greenhouse Only

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_simulation.launch.py
```

Headless:

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_simulation.launch.py gui:=false
```

## Launch Greenhouse With MIRTE

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_master.launch.py
```

Change the robot start pose:

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_master.launch.py \
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
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_cartographer.launch.py
```

RViz opens by default and shows the live map, laser scan, TF, and robot model.

Drive the robot around with teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel_unstamped
```

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
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_navigation.launch.py
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
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_navigation.launch.py \
  map:=/absolute/path/to/your_map.yaml
```

Example:

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_navigation.launch.py \
  map:=/home/spatial-ai/mirte_simulation/info/my_map.yaml
```

The `.yaml` file must point to the matching `.pgm` image. If the YAML says `image: my_map.pgm`, keep both files in the same directory.

## Useful Options

Run navigation without RViz:

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_navigation.launch.py use_rviz:=false
```

Run navigation without Gazebo GUI:

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_navigation.launch.py gui:=false
```

Start the robot at a different pose:

```bash
ros2 launch mdp_greenhouse_simulation greenhouse_mirte_navigation.launch.py \
  x:=2.5 y:=1.0 yaw:=1.5708
```

## Files

```text
launch/greenhouse_simulation.launch.py
launch/greenhouse_mirte_master.launch.py
launch/greenhouse_mirte_cartographer.launch.py
launch/greenhouse_mirte_navigation.launch.py
worlds/mdp_greenhouse.world
config/mirte_2d.lua
config/nav2_mirte_params.yaml
rviz/greenhouse_cartographer.rviz
```

## Notes

- Cartographer mapping uses `/scan`, `/odom`, and the MIRTE TF tree.
- Mapping/manual teleop uses `/mirte_base_controller/cmd_vel_unstamped`.
- Nav2 navigation uses `/cmd_vel` directly.
- If Gazebo says the master port is already in use, stop the old Gazebo process or launch with a different `GAZEBO_MASTER_URI`.
