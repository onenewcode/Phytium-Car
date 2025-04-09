import smbus
import time
import traitlets
import serial
import struct
import threading
from typing import Protocol
from simple_pid import PID 

# 定义电机驱动基类
class MotorBase(Protocol):

    def Control(self,direction,speed)->None:
        pass


# 定义 PCA9685 电机驱动类
class PCA9685Motor( traitlets.HasTraits):
    def __init__(self, d1, d2, d3, d4):
        super().__init__()
        # 设置 PCA9685 I2C 地址
        self.PCA9685_ADDRESS = 0x60

        # 寄存器地址
        self.MODE1 = 0x00
        self.PRE_SCALE = 0xFE
        self.LED0_ON_L = 0x06

        # 初始化 I2C 总线
        self.bus = smbus.SMBus(2)
        self.set_pwm_frequency(50)
        self.set_pwm(d1, d2, d3, d4)
        self.Stop()

        self.release_angle1 = 90
        self.release_angle2 = 87

        self.traffic_light_release()

    Car_run = traitlets.Integer(default_value=0)

    # 绑定 Car_run 属性的观察者函数
    @traitlets.validate("Car_run")
    def _Car_run_Task(self, proposal):
        actions = {
            0: self.Stop,
            1: self.Advance,
            2: self.Back,
            3: self.Move_Left,
            4: self.Move_Right,
            5: self.Trun_Left,
            6: self.Trun_Right,
            7: self.Advance_Left,
            8: self.Advance_Right,
            9: self.Back_Left,
            10: self.Back_Right,
            11: self.Rotate_Left,
            12: self.Rotate_Right,
        }

        value = proposal["value"]
        if value in actions:
            actions[value]()

        return value

    def Stop(self):  # 停止
        self.Status_control(0, 0, 0, 0)

    def Advance(self):  # 前进
        self.Status_control(1, 1, 1, 1)

    def Back(self):  # 后退
        self.Status_control(-1, -1, -1, -1)

    def Move_Left(self):  # 平移向左
        self.Status_control(-1, 1, 1, -1)

    def Move_Right(self):  # 平移向右
        self.Status_control(1, -1, -1, 1)

    def Trun_Left(self):  # 左转
        self.Status_control(0, 1, 1, 1)

    def Trun_Right(self):  # 右转
        self.Status_control(1, 0, 1, 1)

    def Advance_Left(self):  # 左前
        self.Status_control(0, 1, 1, 0)

    def Advance_Right(self):  # 右前
        self.Status_control(1, 0, 0, 1)

    def Back_Left(self):  # 左后
        self.Status_control(-1, 0, 0, -1)

    def Back_Right(self):  # 右后
        self.Status_control(0, -1, -1, 0)

    def Rotate_Right(self):  # 左旋转
        self.Status_control(1, -1, 1, -1)

    def Rotate_Left(self):  # 右旋转
        self.Status_control(-1, 1, -1, 1)

    def LX_90D(self, t_ms):  # 左旋转 90 度
        self.Rotate_Left()
        time.sleep(t_ms / 1000.0)
        self.Stop()

    def RX_90D(self, t_ms):  # 右旋转 90 度
        self.Rotate_Right()
        time.sleep(t_ms / 1000.0)
        self.Stop()

    def GS_run(self, L_speed, R_speed):
        self.set_pwm(L_speed, R_speed, L_speed, R_speed)

    def set_pwm_frequency(self, freq):
        # 计算预分频值
        prescale_val = int(25000000.0 / (4096 * freq) - 1)

        # 读取当前 MODE1 寄存器的值
        old_mode = self.bus.read_byte_data(self.PCA9685_ADDRESS, self.MODE1)

        # 设置 SLEEP 位（MODE1 寄存器的第 4 位）为 1，进入睡眠模式
        new_mode = (old_mode & 0x7F) | 0x10
        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.MODE1, new_mode)

        # 设置预分频寄存器的值
        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.PRE_SCALE, prescale_val)

        # 将 SLEEP 位设置为 0，退出睡眠模式
        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.MODE1, old_mode)

        # 等待至少 500us，以确保 OSC 稳定
        time.sleep(0.005)

        # 将 RESTART 位（MODE1 寄存器的第 7 位）设置为 1，重启设备
        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.MODE1, old_mode | 0x80)

        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.MODE1, 0x00)

    def set_pwm(self, Duty_channel4, Duty_channel3, Duty_channel2, Duty_channel1):
        # 设置 PWM 通道的占空比
        Duty_channel1 = max(0, min(Duty_channel1, 4095))  # 限制 off_time 在 0-4095 之间
        Duty_channel2 = max(0, min(Duty_channel2, 4095))  # 限制 off_time 在 0-4095 之间
        Duty_channel3 = max(0, min(Duty_channel3, 4095))  # 限制 off_time 在 0-4095 之间
        Duty_channel4 = max(0, min(Duty_channel4, 4095))  # 限制 off_time 在 0-4095 之间

        # 简化后的 PWM 设置函数
        def set_channel_pwm(channel, duty):
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 2, duty & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 3, duty >> 8
            )

        set_channel_pwm(0, Duty_channel1)
        set_channel_pwm(5, Duty_channel2)
        set_channel_pwm(6, Duty_channel3)
        set_channel_pwm(11, Duty_channel4)

    def Status_control(self, m4, m3, m2, m1):
        # 简化后的电机控制函数
        def set_motor_pwm(channel_pair, direction):
            channel1, channel2 = channel_pair

            if direction == -1:  # 反向
                set_channel_pwm(channel1, 4095)
                set_channel_pwm(channel2, 0)
            elif direction == 0:  # 停止
                set_channel_pwm(channel1, 0)
                set_channel_pwm(channel2, 0)
            elif direction == 1:  # 正向
                set_channel_pwm(channel1, 0)
                set_channel_pwm(channel2, 4095)

        def set_channel_pwm(channel, duty):
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 2, duty & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 3, duty >> 8
            )

        # 控制四个电机
        set_motor_pwm((1, 2), m1)
        set_motor_pwm((3, 4), m2)
        set_motor_pwm((7, 8), m3)
        set_motor_pwm((9, 10), m4)

    def set_servo_angle(self, angle):
        min_pulse = 150
        max_pulse = 2500
        angle = max(0, min(180, angle))  # 限制角度在 0 到 180 度之间
        pulse_width = int((angle / 180.0) * (max_pulse - min_pulse) + min_pulse)
        duty_cycle = (pulse_width / 20000) * 4096  # 将脉冲宽度转换为占空比
        return int(duty_cycle)

    def set_servo(self, channel, angle1):
        # 设置 PWM 通道的占空比
        Duty_channel1 = self.set_servo_angle(angle1)

        def set_channel_pwm(channel, on_value, off_value):
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel, on_value & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 1, on_value >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 2, off_value & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 3, off_value >> 8
            )

        set_channel_pwm(channel, 0, Duty_channel1)

    def release(self):
        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.MODE1, 0x00)

    def traffic_light_change(self):
        self.set_servo(12, 120)
        self.set_servo(13, 90)

    def traffic_light_release(self):
        self.set_servo(12, self.release_angle1)
        self.set_servo(13, self.release_angle2)

    def servo_follow(self):
        self.set_servo(12, 100)

    def servo_poss(self):
        self.set_servo(12, 40)

    def servo_map(self):
        self.set_servo(12, 105)

    def FT_Turn(self, L, R):
        self.Status_control(1, -1, 1, -1)
        self.set_pwm(L, R, L, R)


# 定义 Modbus 电机驱动类
# 在 ModbusMotor 类中添加 PID 控制相关方法
 # 需要安装：pip install simple-pid

class ModbusMotor(MotorBase ):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True
        self.last_time = time.time()
        self.interval = 0.05
        # 添加速度相关的属性初始化
        self.left_speed = 0
        self.right_speed = 0
        self.max_speed = 255  # 最大速度限制
        self.enable_motor()

    def set_motor_speed(self, left_speed, right_speed):
        """设置电机速度
        
        Args:
            left_speed: 左轮速度 (-255 到 255)
            right_speed: 右轮速度 (-255 到 255)
        """
        # 限制速度范围
        self.left_speed = max(-self.max_speed, min(self.max_speed, left_speed))
        self.right_speed = max(-self.max_speed, min(self.max_speed, right_speed))



    def Control(self, direction, speed):
        actions = {
            0: self.Stop,
            1: self.Advance,
            2: self.Back,
            5: self.Trun_Left,
            6: self.Trun_Right,
        }

        self.left_speed=speed
        self.right_speed=speed
        if direction==0:
            actions[direction]()
        current_time=time.time()
        if current_time-self.last_time>self.interval:
            print("Car_run_Task called with value:", direction)  # 调试打印
            self.last_time=current_time
            actions[direction]()


    def send_modbus_command(self, command):
        try:
            with serial.Serial(self.port, baudrate=57600, timeout=0.1) as ser:
                request = bytes.fromhex(command)
                ser.write(request)
        except (serial.SerialException, OSError) as e:
            print(f"Unable to open serial port {self.port}: {e}")
    # 添加一个装饰器函数来检查电机状态
    def check_motor_state(func):
        def wrapper(self, *args, **kwargs):
            if not self.running:
                self.enable_motor()
            return func(self, *args, **kwargs)
        return wrapper
    # 计算 CRC 函数
    def calculate_crc(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        return crc

    def enable_motor(self):
        self.running=True
        self.send_modbus_command(self.get_modbus_command("enable"))

    def disable_motor(self):
        self.running=False
        self.send_modbus_command(self.get_modbus_command("disable"))

    def Stop(self):
        self.running=False
        self.send_modbus_command(self.get_modbus_command("stop"))
    @check_motor_state
    def Advance(self):
        self.send_modbus_command(self.get_modbus_command("advance"))
    @check_motor_state
    def Back(self):

        self.send_modbus_command(self.get_modbus_command("back"))

    @check_motor_state
    def Trun_Left(self):

        self.send_modbus_command(self.get_modbus_command("turn_left"))
    @check_motor_state
    def Trun_Right(self):

        self.send_modbus_command(self.get_modbus_command("turn_right"))


    # 获取 Modbus 命令映射
    def set_motor_speed(self, left_speed, right_speed):
        """设置电机速度
        
        Args:
            left_speed: 左轮速度 (-255 到 255)
            right_speed: 右轮速度 (-255 到 255)
        """
        # 限制速度范围
        self.left_speed = left_speed
        self.right_speed = right_speed
        
    def get_modbus_command(self, action):
        """获取 Modbus 命令"""
        # 转换速度为十六进制格式
        def speed_to_hex(speed):
            if speed >= 0:
                return f"FF {speed:02X}"  # 正向速度
            else:
                return f"00 {abs(speed):02X}"  # 反向速度

        # 基础命令模板
        base_commands = {
            "enable": "05 44 21 00 31 00 00 01 00 01",
            "disable": "05 44 21 00 31 00 00 00 00 00",
            "stop": "05 44 21 00 31 00 00 00 00 00",
        }

        # 运动命令需要动态生成
        movement_commands = {
            "advance": f"05 44 23 18 33 18 {speed_to_hex(self.left_speed)} {speed_to_hex(self.right_speed)}",
            "back": f"05 44 23 18 33 18 {speed_to_hex(-self.left_speed)} {speed_to_hex(-self.right_speed)}",
            "turn_left": f"05 44 23 18 33 18 {speed_to_hex(-self.left_speed)} {speed_to_hex(self.right_speed)}",
            "turn_right": f"05 44 23 18 33 18 {speed_to_hex(self.left_speed)} {speed_to_hex(-self.right_speed)}",
        }

        # 合并命令字典
        commands = {**base_commands, **movement_commands}
        command = commands.get(action, "")
        
        # 如果命令非空，计算并添加 CRC
        if command:
            data = bytes.fromhex(command)
            crc = self.calculate_crc(data)
            crc_bytes = struct.pack('<H', crc)
            command = f"{command} {crc_bytes[0]:02X} {crc_bytes[1]:02X}"
        print(command)
        return command


# 统一的电机控制类，可以选择使用哪种驱动方式
class Motor:
    def __init__(self, driver_type="pca9685", **kwargs):
        """
        初始化电机控制器

        参数:
            driver_type: 驱动类型，可选 "pca9685" 或 "modbus"
            **kwargs: 根据驱动类型传递不同的参数
                对于 pca9685: d1, d2, d3, d4
                对于 modbus: port
        """
        if driver_type == "pca9685":
            d1 = kwargs.get("d1", 1500)
            d2 = kwargs.get("d2", 1500)
            d3 = kwargs.get("d3", 1500)
            d4 = kwargs.get("d4", 1500)
            self.driver = PCA9685Motor(d1, d2, d3, d4)
        elif driver_type == "modbus":
            port = kwargs.get("port", "COM1")
            self.driver = ModbusMotor(port)
        else:
            raise ValueError(f"不支持的驱动类型：{driver_type}")

        self.driver_type = driver_type

    def __getattr__(self, name):
        """转发方法调用到具体的驱动实现"""
        return getattr(self.driver, name)

def calculate_crc(data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        return crc
def send_modbus_command(command):
    
            data_without_crc = command[:-5]
            crc = calculate_crc(bytes.fromhex(data_without_crc))
            crc_bytes = struct.pack('<H', crc)
            command_with_crc = data_without_crc + f" {crc_bytes[0]:02X} {crc_bytes[1]:02X}"
            print(command_with_crc)
if __name__ == "__main__":
    # 使用 Modbus 驱动
    # car_controller:MotorBase = ModbusMotor(port="COM1")
    # car_controller.Control(1,100)
    send_modbus_command("05 44 23 18 33 18 FF 64 FF 64 AD 09")

               
