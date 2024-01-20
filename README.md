# Data Collection
```bash
roslaunch ldlidar_sl_ros viewer_ld14p_noetic.launch
rosbag record -O recording.bag pointcloud2d
rosbag filter --print="'%d.%d, %d : %s' % (t.secs % 100, t.nsecs, len(m.points), [(m.points[i].x, m.points[i].y) for i in range(len(m.points)) if (m.points[i].x != 0 or m.points[i].y != 0)])" recording.bag filtered.bag "topic=='pointcloud2d'" > cleaned.txt
```
