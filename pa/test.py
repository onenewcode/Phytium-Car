import pyarrow as pa

# 假设 event.key.char 是一个具体的字符，例如 'A'
# 这里我们直接指定一个示例字符，因为在没有上下文的情况下无法直接获取 event 对象
char_example = "A"

# 使用 pyarrow 创建一个 array
data = pa.array([char_example])

# 输出 Arrow Array 来确认内容
print("Arrow Array:", data)

# 转换回来的方法取决于你想要的结果形式。
# 如果你想要回原始列表形式，可以简单地将其转换为 Python list
data_converted_back = data.to_pylist()

# 输出转换回来的数据来确认内容
print("Converted back to Python list:", data_converted_back)

# 如果你只需要第一个元素，可以直接访问列表的第一个元素
original_char = data_converted_back[0]
print("Original char:", original_char)
