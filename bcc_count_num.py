import platform
from collections import deque, defaultdict

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

system = platform.system()
if system == 'Windows':
    mpl.rc('font', family='Microsoft YaHei')  # Windows系统使用微软雅黑


def get_neighbors(pos):
    """
    计算一个原子的所有最近邻位置。
    输入 pos 为一个三元组 (x, y, z)，这些值均为整数，
    实际物理坐标为 (x/2, y/2, z/2) 。
    对于体心立方结构，每一步的移动为每个坐标 ±1 （对应实际 ±0.5）。
    """
    offsets = [(dx, dy, dz)
               for dx in [1, -1]
               for dy in [1, -1]
               for dz in [1, -1]]
    for off in offsets:
        neighbor = (pos[0] + off[0], pos[1] + off[1], pos[2] + off[2])
        yield neighbor


def bfs_bcc(max_layer):
    """
    从中心原子 (0,0,0)（A 位原子，对应实际 (0,0,0)）开始，
    采用 BFS 遍历体心立方晶格的原子（两子格交错），
    返回一个字典，key 为原子位置（以整数元组表示），value 为到中心的最短步数（层数）。
    仅搜索步数不超过 max_layer 的原子。
    """
    start = (0, 0, 0)  # 中心原子，A 位
    distances = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        d = distances[current]
        if d >= max_layer:
            continue  # 超出最大步数，不再拓展
        for nb in get_neighbors(current):
            if nb not in distances:  # 未访问过，记录步数，并入队
                distances[nb] = d + 1
                queue.append(nb)
    return distances


def plot_bcc_cluster_layer_by_layer(layers, max_layer):
    """
    逐层绘制BCC原子团簇，每一层显示累积的所有原子
    """
    # 使用 colormap 为不同层着色
    cmap = plt.get_cmap("viridis")
    colors = [cmap(i) for i in np.linspace(0, 1, max_layer + 1)]

    # 逐层绘制原子团簇
    for n in range(max_layer + 1):
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')

        # 计算当前层数下的累计原子数
        total_atoms = sum(len(layers[d]) for d in range(n + 1))
        formula_value = n ** 3 + (n + 1) ** 3

        # 绘制到当前层为止的所有原子
        for d in range(n + 1):
            pos_list = layers[d]
            if not pos_list:
                continue
            coords = np.array(pos_list, dtype=float) / 2.0  # 转换回实际坐标
            ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2],
                       color=colors[d], edgecolors='k', s=200,
                       label=f'层 {d}，原子数: {len(pos_list)}')

        # 设置图表属性
        ax.set_xlabel("X", fontsize=14)
        ax.set_ylabel("Y", fontsize=14)
        ax.set_zlabel("Z", fontsize=14)
        ax.set_title(f"体心立方原子团 (n={n})\n"
                     f"累计原子数: {total_atoms}，公式预测值: {formula_value}",
                     fontsize=16)

        # 设置适当的视角和范围
        # 找出所有显示原子的最大坐标，确保视图范围合适
        all_coords = []
        for d in range(n + 1):
            if layers[d]:
                all_coords.extend([np.array(pos) / 2.0 for pos in layers[d]])

        if all_coords:
            all_coords = np.array(all_coords)
            max_range = np.max(np.abs(all_coords)) + 0.5
            ax.set_xlim(-max_range, max_range)
            ax.set_ylim(-max_range, max_range)
            ax.set_zlim(-max_range, max_range)

        # 选择一个好的视角
        ax.view_init(elev=20, azim=30)

        # 确保坐标轴比例相等
        ax.set_box_aspect([1, 1, 1])

        # 添加图例
        ax.legend(loc='upper left', fontsize=12)

        plt.tight_layout()
        plt.show()


def plot_atom_count_growth(layers, max_layer):
    """
    绘制随层数增加的原子数增长曲线，并与理论公式对比
    """
    fig, ax = plt.figure(figsize=(10, 6)), plt.gca()

    # 实际数据
    n_values = list(range(max_layer + 1))
    actual_counts = [sum(len(layers[d]) for d in range(n + 1)) for n in n_values]

    # 公式预测值
    formula_counts = [n ** 3 + (n + 1) ** 3 for n in n_values]

    # 绘制曲线
    ax.plot(n_values, actual_counts, 'o-', linewidth=2, label='实际原子数')
    ax.plot(n_values, formula_counts, 's--', linewidth=2, label='公式: n³+(n+1)³')

    # 设置图表属性
    ax.set_xlabel('层数 n', fontsize=14)
    ax.set_ylabel('累计原子数', fontsize=14)
    ax.set_title('BCC原子团簇中原子数随层数的增长', fontsize=16)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(fontsize=12)

    # 在图表中添加数据标签
    for i, (actual, formula) in enumerate(zip(actual_counts, formula_counts)):
        ax.annotate(f'{actual}', (i, actual), textcoords="offset points",
                    xytext=(0, 10), ha='center')
        ax.annotate(f'{formula}', (i, formula), textcoords="offset points",
                    xytext=(0, -15), ha='center')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # 设置最大层数（步数），对应公式中 n 的取值。
    max_layer = 5  # 可修改为更大值，例如 5, 6, ...

    # 利用 BFS 得到所有原子的位置及其最短步数
    distances = bfs_bcc(max_layer)

    # 分层整理（按距离层数分组），便于后续绘图
    layers = defaultdict(list)
    for pos, d in distances.items():
        layers[d].append(pos)

    # 统计每一"层"累积的原子总数，并与公式对比
    print("layer,\tcount,\tsum,\tside,\tpredict n^3+(n+1)^3")
    for n in range(max_layer + 1):
        layer_count = len(layers[n])
        cum_count = sum(len(layers[d]) for d in range(n + 1))
        side = 8 + 12 * (n - 1)
        predicted = n ** 3 + (n + 1) ** 3
        print(f" {n:2d}\t    {layer_count:4d}\t{cum_count:4d}\t    {side:4d}\t    {predicted:4d}")

    # 逐层显示原子团簇
    plot_bcc_cluster_layer_by_layer(layers, max_layer)

    # 绘制原子数增长曲线
    plot_atom_count_growth(layers, max_layer)
