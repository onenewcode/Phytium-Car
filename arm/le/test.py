import lebai_sdk
class Arm:
    def __init__(self, ip):
        self.lebai = lebai_sdk.connect(ip, False) #创建实例
        self.lebai.start_sys()
    def stop(self):
        self.lebai.stop_sys() #停止手臂
    def start(self):
        self.lebai.start_sys() #启动手臂
    # 手抓释放 
    def release(self):
        self.lebai.set_claw(10, 100)
    def grasp(self):
        self.lebai.set_claw(60, 50)
    def starting_point(self):
        joint_pose=[0.7867403965868482, -1.704444402939433, 1.0572003842509354, -0.8716845827160156, 4.7465200529151454, 1.5381992350523266]
        cartesian_pose={'x': -0.09898701516754976, 'y': -0.27411352331697086, 'z': 0.5617409971994105, 'rx': 3.105792566259719, 'ry': -0.05073181418599773, 'rz': 0.8193567410370365}
        a = 0.5 #关节加速度 (rad/s2)
        v = 0.2 #关节速度 (rad/s)
        t = 0   #运动时间 (s)。当 t > 0 时，参数速度 v 和加速度 a 无效
        r = 0   #交融半径 (m)。用于指定路径的平滑效果
        self.lebai.movej(joint_pose,a,v,t,r) #关节运动 https://help.lebai.ltd/sdk/motion.html#%E5%85%B3%E8%8A%82%E8%BF%90%E5%8A%A8
        a = 0.3 #空间加速度 (m/s2)
        v = 0.1 #空间速度（m/s）
        t = 0   #运动时间 (s)。当 t > 0 时，参数速度 v 和加速度 a 无效
        r = 0   #交融半径 (m)。用于指定路径的平滑效果
        self.lebai.movel(cartesian_pose,a,v,t,r) #直线运动 https://help.lebai.ltd/sdk/motion.html#%E7%9B%B4%E7%BA%BF%E8%BF%90%E5%8A%A8
        self.lebai.wait_move() #等待运动完成

        
def main():
    lebai_sdk.init()
    arm=Arm("192.168.3.220")
    arm.starting_point()

    
  
main()