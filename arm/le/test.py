import lebai_sdk
# lebai:teach_mode()
# lebai:end_teach_mode()
class Arm:
    def __init__(self, ip):
        self.lebai = lebai_sdk.connect(ip, False) #创建实例
        self.lebai.start_sys()
        # 初始关节位置
        self.start_joint=[-2.2194784524720372, -1.747395865000231, -0.21360682471307552, -2.513619268549109, -4.742013984350731, 1.5966822525904667]
    def stop(self):
        self.lebai.stop_sys() #停止手臂
    def start(self):
        self.lebai.start_sys() #启动手臂
    # 手抓释放 
    def release(self):
        self.lebai.set_claw(10, 100)
    def grasp(self):
        self.lebai.set_claw(50, 50)
    def starting_point(self):
        self.movej(self.start_joint)
        self.release()
        self.lebai.wait_move() #等待运动完成
    # 法兰盘末端坐标
    def pose_trans(self,pose):
        current_tcp_pose = self.lebai.get_kin_data()['actual_tcp_pose'] #当前法兰盘末端坐标
        calculate_location = self.lebai.pose_trans(current_tcp_pose, pose) #计算的新位置
        self.movel(calculate_location)
        self.lebai.wait_move() #等待运动完成
    
    def pose_add(self,delta):
        base = self.lebai.get_kin_data()['actual_tcp_pose'] #当前末端坐标
        # frame  ={'x' : 0, 'y' :0, 'z' : 0, 'rz' :0, 'ry' : 0, 'rx' : 0}  #基座坐标系 位姿偏移量方向，仅姿态部分有效。
        pose = self.lebai.pose_add(base, delta) #计算的新位置
        self.movel(pose)
        self.lebai.wait_move() #等待运动完成
    def wait_move(self):
        self.lebai.wait_move() #等待运动完成
    def movel(self,pose):
        a = 0.3 #空间加速度 (m/s2)
        v = 0.1 #空间速度（m/s）
        t = 0   #运动时间 (s)。当 t > 0 时，参数速度 v 和加速度 a 无效
        r = 0   #交融半径 (m)。用于指定路径的平滑效果
        self.lebai.movel(pose,a,v,t,r)
    def movej(self,pose):
        a = 1 #关节加速度 (rad/s2)
        v = 0.3 #关节速度 (rad/s)
        t = 0   #运动时间 (s)。当 t > 0 时，参数速度 v 和加速度 a 无效
        r = 0.3   #交融半径 (m)。用于指定路径的平滑效果
        self.lebai.movej(pose,a,v,t,r) 
    #  获取机械臂的运动状态
    def state(self):
        self.lebai.get_robot_state()
    # 抓取任务
    def task(self):
        self.starting_point()
        low= [-2.15438014278614, -3.0778365770932963, -1.1442537939634454, -0.5517537146426166, -4.6777785388580195, 1.5996543403669952]
        high=[-2.1652138821005824, -1.6532477941437498, -0.07727428218973917, -2.21756097648718, -4.634635329198736, 1.6002295831624522]
        left=[0.7489661196851644, -1.532638554696241, -0.07574030140185353, -2.5300136882196367, -4.625527318270665, 1.6000378355639666]
        self.movej(low)
        self.wait_move()
        self.grasp()
        self.wait_move()
        self.movej(high)
        self.wait_move()
        self.movej(left)
        self.wait_move()
        self.starting_point()
        self.wait_move()
        
def main():
    # print(lebai_sdk.discover_devices(2))
    lebai_sdk.init()
    arm=Arm("192.168.3.220")
    # status_dic = arm.lebai.get_kin_data()  #获取手臂当前运动数据，返回一个字典，具体官网有详细说明。其中 actual_joint_pose 和 actual_tcp_pose 分别是关节角坐标表达的位置和笛卡尔坐标表达的位置
    # print('反馈关节位置',status_dic['actual_joint_pose'])  
    arm.task()
    # arm.starting_point()
    # pos={'x' : 0, 'y' :0, 'z' : 0.2, 'rz' :0, 'ry' : 0, 'rx' : 0}
    # arm.pose_trans(pos)
    # delta = {'x' : 0, 'y' :0.01, 'z' : -0.2, 'rz' :0, 'ry' : 0, 'rx' : 0}  
    # arm.pose_add(delta)
   

    arm.release()
    arm.grasp()
    # arm.starting_point()
    arm.lebai.wait_move()
    
  
main()