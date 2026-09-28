# W3 生词表 CSV -> 自动生成练习题
# 运行：python vocab_tool.py
import os
import csv
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  统一解析 data/ 路径，换目录也不会找不到文件

# 兼容文件名编码问题：查找data目录下的CSV文件
def find_vocab_csv():
    try:
        return weekpath.data_path(“生词表.csv”)
    except:
        # 如果文件名编码有问题，尝试查找任何CSV文件
        csv_files = glob.glob(os.path.join(weekpath.DATA_DIR, “*.csv”))
        if csv_files:
            return csv_files[0]
        raise FileNotFoundError(“未找到词汇表CSV文件”)

DATA = find_vocab_csv()


def load_words(path=DATA):
    “””从CSV文件加载词汇列表”””
    with open(path, encoding=”utf-8”) as f:
        return list(csv.DictReader(f))


def filter_by_level(words, level=”4”):
    “””按HSK等级筛选词汇”””
    return [w for w in words if str(w.get(“HSK等级”, “”)).strip() == str(level)]


def count_by_pos(words):
    “””统计词性分布”””
    d = {}
    for w in words:
        pos = w.get(“词性”, “未知”)
        d[pos] = d.get(pos, 0) + 1
    return d


def gen_exercises(words, out=None):
    “””生成造句练习题

    产物统一落到代码包根目录：否则”从哪个目录运行”决定了文件落在哪，
    与 README 的”任意目录运行”承诺冲突，且散落的产物 .gitignore 拦不住。
    “””
    out = out or weekpath.root_path(“练习.txt”)
    with open(out, “w”, encoding=”utf-8”) as f:
        for w in words:
            vocab = w.get(“词汇”, “”)
            pos = w.get(“词性”, “未知”)
            f.write('用”%s”造一个句子。（%s）\n' % (vocab, pos))


if __name__ == “__main__”:
    try:
        words = load_words()
        lv4 = filter_by_level(words, “4”)
        pos_dist = count_by_pos(lv4)
        print(“总词汇 %d 个，其中 HSK4 词汇 %d 个，词性分布：%s”
              % (len(words), len(lv4), pos_dist))
        out = weekpath.root_path(“练习.txt”)
        gen_exercises(lv4, out)
        print(“已生成：%s” % out)
    except Exception as e:
        print(“错误：%s” % str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
