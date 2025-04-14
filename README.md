# 项目启动
## 可视化界面
根目录下运行 control.py 文件

# 结构解析
```shell

│  .gitignore  
│  car_cv.py  #用于识别的节点，接受cv识别的结果，控制小车运行
│  car_cv.yaml
│  color_detector.py
│  control.py   # 服务器控制小城
│  cv_show.yml
│  main.py
│  motor_test.yml
│  move.py
│  pyproject.toml
│  README.md
│  requirements.txt
│  test.py
│  uv.lock
│  yolo.py  # yolo迁移训练文件
│  yolo11n.pt
│
│
├─arm
│  └─le
│      │  main.py #控制机械臂的节点
│      │  test.py
│      
│
├─common
│  │  move_data.py # 输出移动数据
│  │  test_move_data.py
│  │  view.py #输出数据给前端
│  │  __init__.py
│
├─model  #用于yolo训练的文件
│      ball.yaml
│      yolo11n.pt
│
├─motor
│  │  main.py
│  │  Motor.py  # 控制电机节点 ModbusMotor是控制地盘
│  │  pyproject.toml
│  │  test.py
│  │
│
├─mycv
│  │  color.py #用于识别小球的节点
│  │  __init__.py
│
├─network
├─pa
│      test.py
│
├─sh
├─show
│  │  main.py
│  │
│  ├─ob
│  │      color_viewer.py
│  │      depth_color_sync_align_viewer.py
│  │      main.py
│
├─templates
│      index.html
│
├─untils
│  │  untils.py 
│  │  __init__.py
│  │
```