import smbus
import time
import traitlets


# 定义电机驱动类
class _motor(traitlets.HasTraits):
    def __init__(self, d1, d2, d3, d4):
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
        # Car_run = traitlets.Integer(default_value=0) 主要用于定义一个可观察的整数属性，
        # 它不仅能够存储和表示关于“车运行”状态的信息，还能够在属性值发生变化时，
        # 根据需要触发相应的处理逻辑或更新其他部分的状态

    Car_run = traitlets.Integer(default_value=0)

    # 绑定 Car_run 属性的观察者函数
    @traitlets.validate("Car_run")
    def _Car_run_Task(self, proposal):
        if proposal["value"] == 0:  # 停止
            self.Stop()
            return proposal["value"]

        elif proposal["value"] == 1:  # 前进
            self.Advance()
            return proposal["value"]

        elif proposal["value"] == 2:  # 后退
            self.Back()
            return proposal["value"]

        elif proposal["value"] == 3:  # 平移向左
            self.Move_Left()
            return proposal["value"]

        elif proposal["value"] == 4:  # 平移向右
            self.Move_Right()
            return proposal["value"]

        elif proposal["value"] == 5:  # 左转
            self.Trun_Left()
            return proposal["value"]

        elif proposal["value"] == 6:  # 右转
            self.Trun_Right()
            return proposal["value"]

        elif proposal["value"] == 7:  # 前左
            self.Advance_Left()
            return proposal["value"]

        elif proposal["value"] == 8:  # 前右
            self.Advance_Right()
            return proposal["value"]

        elif proposal["value"] == 9:  # 后左
            self.Back_Left()
            return proposal["value"]

        elif proposal["value"] == 10:  # 后右
            self.Back_Right()
            return proposal["value"]

        elif proposal["value"] == 11:  # 左旋转
            self.Rotate_Left()
            return proposal["value"]

        elif proposal["value"] == 12:  # 右旋转
            self.Rotate_Right()
            return proposal["value"]

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
        time.sleep(time / 1000.0)
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

        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 0, 0 & 0xFF)
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 0 + 1, 0 >> 8
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 0 + 2, Duty_channel1 & 0xFF
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 0 + 3, Duty_channel1 >> 8
        )

        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 5, 0 & 0xFF)
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 5 + 1, 0 >> 8
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 5 + 2, Duty_channel2 & 0xFF
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 5 + 3, Duty_channel2 >> 8
        )

        self.bus.write_byte_data(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 6, 0 & 0xFF)
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 6 + 1, 0 >> 8
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 6 + 2, Duty_channel3 & 0xFF
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 6 + 3, Duty_channel3 >> 8
        )

        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 11, 0 & 0xFF
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 11 + 1, 0 >> 8
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 11 + 2, Duty_channel4 & 0xFF
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 11 + 3, Duty_channel4 >> 8
        )

    def Status_control(self, m4, m3, m2, m1):

        if m1 == -1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 3, 4095 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 3, 0 >> 8
            )

        elif m1 == 0:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 3, 0 >> 8
            )

        elif m1 == 1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 1 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 2 + 3, 4095 >> 8
            )

        if m2 == -1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 3, 4095 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 3, 0 >> 8
            )
        elif m2 == 0:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 3, 0 >> 8
            )

        elif m2 == 1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 3 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 4 + 3, 4095 >> 8
            )

        if m3 == -1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 3, 4095 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 3, 0 >> 8
            )
        elif m3 == 0:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 3, 0 >> 8
            )

        elif m3 == 1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 7 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 8 + 3, 4095 >> 8
            )

        if m4 == -1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 3, 4095 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 3, 0 >> 8
            )

        elif m4 == 0:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 3, 0 >> 8
            )

        elif m4 == 1:
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 2, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 9 + 3, 0 >> 8
            )

            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10, 0 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 1, 0 >> 8
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 2, 4095 & 0xFF
            )
            self.bus.write_byte_data(
                self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * 10 + 3, 4095 >> 8
            )

    def set_servo_angle(self, angle):
        min_pulse = 150
        max_pulse = 2500
        angle = max(0, min(180, angle))  # 限制角度在 0 到 180 度之间
        pulse_width = int((angle / 180.0) * (max_pulse - min_pulse) + min_pulse)
        duty_cycle = (pulse_width / 20000) * 4096  # 将脉冲宽度转换为占空比
        print(duty_cycle)
        return int(duty_cycle)

    def set_servo(self, channel, angle1):
        # 设置 PWM 通道的占空比
        Duty_channel1 = self.set_servo_angle(angle1)

        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel, 0 & 0xFF
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 1, 0 >> 8
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 2, Duty_channel1 & 0xFF
        )
        self.bus.write_byte_data(
            self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * channel + 3, Duty_channel1 >> 8
        )

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


if __name__ == "__main__":
    try:
        Control_Motor = _motor(1500, 1500, 1500, 1500)
        print("start")
        while True:
            # 			Control_Motor.Car_run =2
            time.sleep(1)
            Control_Motor.Car_run = 0
            time.sleep(0.3)
            break

    except KeyboardInterrupt:
        # 使用 Ctrl+C 退出循环时，关闭 PCA9685
        Control_Motor.bus.write_byte_data(
            Control_Motor.PCA9685_ADDRESS, Control_Motor.MODE1, 0x00
        )
