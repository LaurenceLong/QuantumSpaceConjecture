# 计算体心立方“中心原子团”模型从第1层到第30层的数据
import math
from random import expovariate


def convert_to_number(value_str):
    value_str = value_str.strip()
    if not value_str:
        return 0

    # 定义单位转换映射
    units = {
        'k': 1_000,
        'K': 1_000,
        'm': 1_000_000,
        'M': 1_000_000,
        'b': 1_000_000_000,
        'B': 1_000_000_000,
        'g': 1_000_000_000,
        'G': 1_000_000_000
    }

    # 如果字符串只有数字，直接转换
    if value_str[-1].isdigit():
        return float(value_str)

    # 获取单位和数值部分
    unit = value_str[-1]
    number_part = value_str[:-1]

    if unit in units:
        return float(number_part) * units[unit]
    else:
        raise ValueError(f"不支持的单位: {unit}")


def find_closest_same_order(target, numbers, diff=10):
    # 获取目标值的量级
    target_order = len(str(int(target)))

    # 筛选出与目标值量级相同的数字
    same_order_numbers = [num for num in numbers if len(str(int(num))) == target_order]

    if not same_order_numbers:
        return [None, None]

    # 找出最相近的数字
    closest = min(same_order_numbers, key=lambda x: abs(x - target))

    # 计算差距百分比
    percentage_diff = (target - closest) / target * 100
    if abs(percentage_diff) < abs(diff):
        return [closest, round(percentage_diff, 2)]
    return [None, None]


def compute_bcc_layers(n_layers=30):
    """计算BCC晶格结构的层数据并格式化输出"""

    # 封装数据初始化函数
    def initialize_data():
        masses_str = [
            "2.4 M", "1.2730 G", "172.57 G", "125.20 G", "4.70 M",
            "93.5 M", "4.183 G", "0.5110 M", "105.66 M", "1776.93 M",
            "91.1880 G", "0.8", "0.17 M", "18.2 M", "80.3692 G"
        ]
        return {convert_to_number(m): m for m in masses_str}

    # 计算每层数据的函数
    def calculate_layer_data(n, prev_cumulative_layer):
        odd_atoms = n ** 3  # 奇晶格原子数 = n^3
        even_atoms = (n - 1) ** 3  # 偶晶格原子数 = (n-1)^3
        cumulative_layer = odd_atoms + even_atoms  # 累计原子数 N(n)
        new_atoms = cumulative_layer - prev_cumulative_layer  # 本层增加的原子数
        return odd_atoms, even_atoms, new_atoms, cumulative_layer

    # 计算质量估计的函数
    def calculate_mass_estimate(cumulative_total):
        units = ["", "K", "M", "G"]
        unit_index = 2
        estimate_mass = 0.511 / 136 * cumulative_total

        while estimate_mass > 1000 or estimate_mass < 1:
            if estimate_mass > 1000:
                estimate_mass /= 1000
                unit_index += 1
            else:
                estimate_mass *= 1000
                unit_index -= 1

        return f"{estimate_mass:.3f} {units[unit_index]}"

    # 打印表头的函数
    def print_header():
        headers = [
            "Layer(n)", "Odd(n³)", "Event((n-1)³)", "NewAtoms",
            "SumLayers(n)", "SumSumLayers R(n)", "Triangle Num T(x)", "MassCompare",
            "        Exposure", "SumExposure", "SumSumExposure"
        ]
        print("  ".join(f"{h:<10}" for h in headers))
        print("-" * 180)  # 分隔线

    # 主计算逻辑
    masses = initialize_data()
    prev_cumulative_layer = 0
    cumulative_total = 0

    occupied = set()
    total = 0
    total_occupied = 0

    # 初始化暴露度相关变量
    sum_exposure = 0
    sum_sum_exposure = 0

    print_header()

    for n in range(1, n_layers + 1):
        odd_atoms, even_atoms, new_atoms, cumulative_layer = calculate_layer_data(n, prev_cumulative_layer)
        exposure = (odd_atoms - even_atoms) * (-1) ** (n + 1)  # 计算暴露度
        sum_exposure += exposure  # 累计暴露度
        sum_sum_exposure += sum_exposure  # 累计累计暴露度

        cumulative_total += cumulative_layer
        total += cumulative_total

        estimate_mass_str = calculate_mass_estimate(cumulative_total)
        estimate_mass = convert_to_number(estimate_mass_str)

        # 查找最接近的质量值
        closest = find_closest_same_order(estimate_mass, masses, diff=5)
        if closest[0]:
            closest_print = f"{estimate_mass_str}/{masses[closest[0]]}:{closest[1]}%"
            occupied.add(masses[closest[0]])
            total_occupied += cumulative_total
        else:
            closest_print = f"{estimate_mass_str}"

        # 打印格式化的数据行
        triangle_info = f"T({data[cumulative_total]})→T({math.sqrt(data[cumulative_total]):.0f}²)"
        print(
            f"{n:<10}  {odd_atoms:<10}  {even_atoms:<15}  {new_atoms:<10}  "
            f"{cumulative_layer:<15}  {cumulative_total:<10}  {triangle_info:<16}  {closest_print:<30}  "
            f"{exposure:<10}  {sum_exposure:<10}  {sum_sum_exposure:<10}"
        )

        prev_cumulative_layer = cumulative_layer

    # 打印统计信息
    un_occupied = set(masses.values()) - occupied
    print("\n未匹配质量:", ", ".join(un_occupied))
    print(f"匹配百分比: {total_occupied / total * 100:.2f}%")


data = {}


def cal_triangle(max_n=100000):
    res = 0
    for i in range(1, max_n + 1):
        res += i
        data[res] = i


if __name__ == "__main__":
    cal_triangle()
    compute_bcc_layers(100)
