# 计算体心立方“中心原子团”模型从第1层到第30层的数据
import math


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
    # 前一层的累计原子数 N(n-1)，初始时 N(0)=0
    prev_cumulative_layer = 0
    # 汇总数据 R(n) = N(1) + N(2) + ... + N(n)
    cumulative_total = 0

    masses_str = [
        "2.3 M",
        "1.2730 G",
        "172.57 G",
        "125.20 G",
        "4.70 M",
        "93.5 M",
        "4.183 G",
        "0.5110 M",
        "105.66 M",
        "1776.93 M",
        "91.1880 G",
        "0.8",
        "0.17 M",
        "18.2 M",
        "80.3692 G",
    ]
    masses = {convert_to_number(_): _ for _ in masses_str}

    # 打印表头（各列含义）
    header = "Layer\tOddAtoms(n^3)\tEvenAtoms((n-1)^3)\tNewAtoms L(n)=N(n)-N(n-1)\tCumulativeLayer N(n)=n^3+(n-1)^3\tCumulativeTotal R(n)\tTriangularNum T(x)\tRelate"
    header_lengths = [len(_) + 4 for _ in header.split("\t")]
    print(header)
    # print(header_lengths)

    occupied = set()
    total = 0
    total_occupied = 0

    # 循环计算每一层的数据
    for n in range(1, n_layers + 1):
        odd_atoms = n ** 3  # 奇晶格原子数 = n^3
        even_atoms = (n - 1) ** 3  # 偶晶格原子数 = (n-1)^3，当 n=1 时为 0
        cumulative_layer = odd_atoms + even_atoms  # 累计原子数 N(n)
        new_atoms = cumulative_layer - prev_cumulative_layer  # 本层增加的原子数，即 N(n) - N(n-1)

        cumulative_total += cumulative_layer  # 更新“汇总数据”
        total += cumulative_total

        units = ["", "K", "M", "G"]
        unit_index = 2
        estimate_mass_data = 0.511 / 136 * cumulative_total

        while estimate_mass_data > 1000 or estimate_mass_data < 1:
            if estimate_mass_data > 1000:
                estimate_mass_data /= 1000
                unit_index += 1
            else:
                estimate_mass_data *= 1000
                unit_index -= 1
        estimate_mass_str = f"{estimate_mass_data:.3f} {units[unit_index]}"
        estimate_mass = convert_to_number(estimate_mass_str)

        # 打印当前层的所有数据，使用制表符进行分隔
        closest = find_closest_same_order(estimate_mass, masses, diff=5)
        closest_print = f"{estimate_mass_str}/{masses[closest[0]]} : {closest[1]}%" if closest[
            0] else f"{estimate_mass_str}"
        if closest[0]:
            occupied.add(masses[closest[0]])
            total_occupied += cumulative_total
        print(
            f"{n:<9}{odd_atoms:<17}{even_atoms:<22}{new_atoms:<29}{cumulative_layer:<36}{cumulative_total:<20}T({data[cumulative_total]:<5}) -> T({math.sqrt(data[cumulative_total]):<3.0f}^2)    {closest_print:<10}"
        )

        # 更新前一层的累计值
        prev_cumulative_layer = cumulative_layer
    un_occupied = set(masses.values()) - occupied
    print(f"Not found: {un_occupied}")
    print(f"Percentage found: {total_occupied / total * 100:.2f}%")


data = {}


def cal_triangle(max_n=100000):
    res = 0
    for i in range(1, max_n + 1):
        res += i
        data[res] = i


if __name__ == "__main__":
    cal_triangle()
    compute_bcc_layers(100)
