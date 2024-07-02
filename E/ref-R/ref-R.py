import itertools
import re

# ANSI颜色码
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
ENDC = '\033[0m'  # 重置颜色

def convert_to_number(s):
    s = s.strip().lower()
    if s.endswith('k'):
        return float(s[:-1]) * 1000
    elif s.endswith('m'):
        return float(s[:-1]) * 1000000
    else:
        return float(s)

def format_resistance(value):
    if value >= 1000000:
        return f"{value / 1000000:.1f}M" if (value / 1000000) % 1 != 0 else f"{int(value / 1000000)}M"
    elif value >= 1000:
        return f"{value / 1000:.1f}K" if (value / 1000) % 1 != 0 else f"{int(value / 1000)}K"
    else:
        return f"{value:.1f}" if value % 1 != 0 else f"{int(value)}"

def read_numbers_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    numbers = []
    for line in lines:
        try:
            number = convert_to_number(line)
            numbers.append(number)
        except ValueError:
            continue  # 忽略无法转换为数值的行
    return numbers

def find_closest_ratios(arr, target):
    pairs_1 = []
    pairs_5 = []
    pairs_10 = []
    
    # Generate all possible pairs (i, j) with i != j
    for i, j in itertools.permutations(arr, 2):
        # If target < 1, only consider i < j
        if target < 1 and i < j:
            ratio = i / j
        # If target > 1, only consider i > j
        elif target > 1 and i > j:
            ratio = i / j
        # Skip pairs that don't meet the criteria
        else:
            continue

        # Calculate the difference from the target
        diff = ratio - target

        # Classify the pairs based on the difference
        if abs(diff) <= 0.01 * target:
            arrow = "-" if diff == 0 else "↑" if diff > 0 else "↓"
            color = MAGENTA if diff == 0 else YELLOW if diff > 0 else GREEN
            pairs_1.append((i, j, ratio, arrow, color))
        elif abs(diff) <= 0.05 * target:
            arrow = "-" if diff == 0 else "↑" if diff > 0 else "↓"
            color = MAGENTA if diff == 0 else YELLOW if diff > 0 else GREEN
            pairs_5.append((i, j, ratio, arrow, color))
        elif abs(diff) <= 0.10 * target:
            arrow = "-" if diff == 0 else "↑" if diff > 0 else "↓"
            color = MAGENTA if diff == 0 else YELLOW if diff > 0 else GREEN
            pairs_10.append((i, j, ratio, arrow, color))
    
    return pairs_1, pairs_5, pairs_10

def filter_pairs_by_total_resistance(pairs, total_resistance):
    valid_pairs = []
    for pair in pairs:
        R1, R2 = pair[0], pair[1]
        R_total = R1 + R2
        resistance_diff = abs(R_total - total_resistance) / total_resistance

        if resistance_diff <= 0.10:  # 阻值误差在10%以内
            valid_pairs.append(pair)
    
    return valid_pairs

# 从文件读取数组
file_path = 'R.txt'
arr = read_numbers_from_file(file_path)

# 获取目标值
while True:
    expr = input("\n请输入目标值: ")
    expr = expr.replace("^", "**")  # 将输入中的^符号替换为**，以支持乘方运算

    # 使用正则表达式检查输入是否只包含数字、小数点、加减乘除和空格
    if re.match(r'^[\d\s\.\+\-\*\/\(\)]+$', expr):
        try:
            target = eval(expr)
            print(f"\n匹配目标为: {RED}{target:.3f}{ENDC}")
            break  # 如果成功计算表达式，则跳出循环
        except (SyntaxError, ZeroDivisionError, ValueError):
            print("输入错误，请输入一个有效的数学表达式！")
    else:
        print("输入错误，请输入一个有效的数学表达式！")

# 获取电压和电流
while True:
    current_str = input("期望通过电流 (mA): ")
    voltage_str = input("线路电压 (V): ")

    try:
        voltage = convert_to_number(voltage_str.replace('v', ''))
        current = convert_to_number(current_str.replace('a', ''))
        if voltage <= 0 or current <= 0:
            raise ValueError("电压和电流必须大于零")
        total_resistance = voltage / current * 1000
        print(f"\n总电阻 (R1 + R2) 接近: {RED}{format_resistance(total_resistance)}{ENDC} 欧姆")
        break
    except ValueError:
        print("输入错误，请输入有效的电压和电流值！")

# 找到最接近的两个数的组合
pairs_1, pairs_5, pairs_10 = find_closest_ratios(arr, target)

# 筛选满足总电阻要求的组合
valid_pairs_1 = filter_pairs_by_total_resistance(pairs_1, total_resistance)
valid_pairs_5 = filter_pairs_by_total_resistance(pairs_5, total_resistance)
valid_pairs_10 = filter_pairs_by_total_resistance(pairs_10, total_resistance)

def sort_pairs_by_ratio(pairs):
    return sorted(pairs, key=lambda x: x[2])

# 输出结果
def print_pairs(pairs, error_percent):
    if pairs:
        sorted_pairs = sort_pairs_by_ratio(pairs)
        print(f"\n精度 {BOLD}{WHITE}{error_percent}%{ENDC} 以内的组合:")
        for pair in sorted_pairs:
            print(f"R1 = {format_resistance(pair[0]):<6}     R2 = {format_resistance(pair[1]):<6}     值: {pair[4]}{pair[2]:.3f} {pair[3]}{ENDC} ")
    else:
        print(f"\n未找到精度在 {BOLD}{WHITE}{error_percent}%{ENDC} 以内的组合")

print_pairs(valid_pairs_1, 1)
print_pairs(valid_pairs_5, 5)
print_pairs(valid_pairs_10, 10)
