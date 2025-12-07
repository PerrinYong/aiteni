"""
NTRP 网球等级评估系统核心模块

基于多维度模糊评分机制，支持硬性上限限制，自动生成详细评语。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import math
import pathlib


# =========================
#  基本数据结构
# =========================

@dataclass
class OptionConfig:
    """单个问题选项配置"""
    id: str
    text: str
    center_level: float
    hard_cap: Optional[float] = None


@dataclass
class QuestionConfig:
    """问题配置"""
    id: str
    text: str
    dimension: str       # baseline / forehand / ...
    weight: float
    options: List[OptionConfig]


@dataclass
class EvaluateResult:
    """评估结果完整输出"""
    total_level: float                     # 应用 hard cap 后的原始等级（未四舍五入）
    rounded_level: float                   # 对外展示等级（四舍五入到 0.5）
    level_label: str                       # 等级标签（初学 / 发展中业余 / 城市级...）
    dimension_scores: Dict[str, float]     # 各维度数值
    dimension_comments: Dict[str, str]     # 各维度长评语
    advantages: List[str]                  # 优势维度 key 列表
    weaknesses: List[str]                  # 短板维度 key 列表
    summary_text: str                      # 总结长文案
    support_distribution: Dict[float, float]  # 各等级支持度分布（调试用）


# =========================
#  NTRP 评估器
# =========================

class NTRPEvaluator:
    """
    NTRP 网球等级评估系统核心类（Python Demo 版）

    使用方法：
        questions = NTRPEvaluator.load_questions("questions.json")
        suggestion_rules = NTRPEvaluator.load_suggestions("dimension_suggestions.json")
        evaluator = NTRPEvaluator(questions, suggestion_rules)

        # 用户作答：question_id -> option_id
        answers = {
            "Q1": "Q1_A3",
            "Q2": "Q2_A4",
            ...
        }

        result = evaluator.evaluate(answers)
        print(result.rounded_level, result.summary_text)
    """

    # 等级刻度
    LEVELS: List[float] = [
        1.0, 1.5, 2.0, 2.5,
        3.0, 3.5, 4.0, 4.5,
        5.0, 5.5, 6.0, 7.0,
    ]

    # 维度名称映射（中文展示用）
    DIMENSION_META: Dict[str, str] = {
        "baseline": "底线综合（稳定性+深度）",
        "forehand": "正手",
        "backhand": "反手",
        "serve": "发球",
        "return": "接发球",
        "net": "网前与高压",
        "footwork": "步伐与场地覆盖",
        "tactics": "战术与心理",
        "match_result": "实战成绩",
        "training": "训练背景 / 频率",
    }

    def __init__(
        self,
        questions: List[QuestionConfig],
        suggestion_rules: Dict[str, List[Dict[str, Any]]],
        spread: float = 1.0,
    ) -> None:
        self.questions = questions
        # suggestion_rules: {"baseline": [ {"min":..,"max":..,"text":..}, ... ], ...}
        self.suggestion_rules = suggestion_rules
        self.spread = spread

    # ---------- 静态加载工具 ----------

    @staticmethod
    def load_questions(path: str | pathlib.Path) -> List[QuestionConfig]:
        """从 questions.json 加载题目配置。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        questions: List[QuestionConfig] = []
        for q in data["questions"]:
            options = [
                OptionConfig(
                    id=o["id"],
                    text=o["text"],
                    center_level=float(o["center_level"]),
                    hard_cap=float(o["hard_cap"]) if "hard_cap" in o else None,
                )
                for o in q["options"]
            ]
            questions.append(
                QuestionConfig(
                    id=q["id"],
                    text=q["text"],
                    dimension=q["dimension"],
                    weight=float(q.get("weight", 1.0)),
                    options=options,
                )
            )
        return questions

    @staticmethod
    def load_suggestions(path: str | pathlib.Path) -> Dict[str, List[Dict[str, Any]]]:
        """从 dimension_suggestions.json 加载维度评语规则。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # data = {"suggestions": {dim: [ {min,max,text}, ... ] } }
        return data.get("suggestions", {})

    # ---------- 公共入口 ----------

    def evaluate(self, answers: Dict[str, str]) -> EvaluateResult:
        """
        核心入口：输入用户作答（question_id -> option_id），返回评估结果。
        """

        # 1) 计算 support(L) + hardCap + 维度分数
        support = {L: 0.0 for L in self.LEVELS}
        hard_cap = max(self.LEVELS)

        dim_sum: Dict[str, float] = {}
        dim_wsum: Dict[str, float] = {}

        for q in self.questions:
            if q.id not in answers:
                continue
            opt_id = answers[q.id]
            opt = self._find_option(q, opt_id)
            if not opt:
                continue

            # 模糊 membership 加到 support
            for L in self.LEVELS:
                m = self._membership(L, opt.center_level, self.spread)
                support[L] += m * q.weight

            # hard cap
            if opt.hard_cap is not None:
                hard_cap = min(hard_cap, opt.hard_cap)

            # 维度加权平均
            dim_sum[q.dimension] = dim_sum.get(q.dimension, 0.0) + opt.center_level * q.weight
            dim_wsum[q.dimension] = dim_wsum.get(q.dimension, 0.0) + q.weight

        # 2) 得到期望值 + 应用 hard cap
        raw_level = self._compute_raw_level(support, hard_cap)

        rounded_level = self._round_to_half(raw_level)
        level_label = self._map_level_to_label(rounded_level)

        # 3) 各维度分数（简单加权平均）
        dimension_scores: Dict[str, float] = {}
        for dim, s in dim_sum.items():
            w = dim_wsum.get(dim, 0.0) or 1.0
            dimension_scores[dim] = s / w

        # 4) 维度评语：基础评语 + 优/劣/中补充语
        dimension_comments = self._build_dimension_comments(
            dimension_scores, rounded_level
        )

        # 5) 优势 / 短板维度
        advantages, weaknesses = self._pick_advantages_and_weaknesses(dimension_scores)

        # 6) 总体 summary 文案
        summary = self._build_summary_text(
            rounded_level,
            level_label,
            dimension_scores,
            dimension_comments,
            advantages,
            weaknesses,
        )

        return EvaluateResult(
            total_level=raw_level,
            rounded_level=rounded_level,
            level_label=level_label,
            dimension_scores=dimension_scores,
            dimension_comments=dimension_comments,
            advantages=advantages,
            weaknesses=weaknesses,
            summary_text=summary,
            support_distribution=support.copy(),
        )

    # =========================
    #  内部工具函数
    # =========================

    def _find_option(self, q: QuestionConfig, opt_id: str) -> Optional[OptionConfig]:
        """查找问题中的指定选项"""
        for o in q.options:
            if o.id == opt_id:
                return o
        return None

    @staticmethod
    def _membership(level: float, center: float, spread: float) -> float:
        """
        三角形隶属度函数：
            diff >= spread  -> 0
            diff == 0       -> 1
            中间线性衰减
        """
        diff = abs(level - center)
        if diff >= spread:
            return 0.0
        return 1.0 - diff / spread

    def _compute_raw_level(
        self,
        support: Dict[float, float],
        hard_cap: float,
    ) -> float:
        """基于支持度分布计算期望值等级"""
        total_support = sum(support.values())
        if total_support <= 0:
            # fallback：没有答题时，用 LEVELS 中位数
            fallback = self.LEVELS[len(self.LEVELS) // 2]
            return min(fallback, hard_cap)

        expectation = sum(L * support[L] for L in self.LEVELS) / total_support
        return min(expectation, hard_cap)

    @staticmethod
    def _round_to_half(x: float) -> float:
        """四舍五入到 0.5 的倍数。"""
        return round(x * 2) / 2.0

    @staticmethod
    def _map_level_to_label(L: float) -> str:
        """等级数值映射到中文标签"""
        if L <= 1.5:
            return "初学者"
        if L <= 2.5:
            return "入门级爱好者"
        if L <= 3.5:
            return "发展中业余选手"
        if L <= 4.5:
            return "城市级业余高手"
        if L <= 5.5:
            return "准专业 / 专业水平"
        return "职业 / 国际级水平"

    # ---------- 维度评语 ----------

    def _build_dimension_comments(
        self,
        dim_scores: Dict[str, float],
        total_level: float,
    ) -> Dict[str, str]:
        """为每个维度生成详细评语"""
        comments: Dict[str, str] = {}
        for dim, score in dim_scores.items():
            base = self._pick_base_comment(dim, score)
            extra = self._extra_comment_for_dim(score, total_level)
            comments[dim] = base + extra
        return comments

    def _pick_base_comment(self, dim: str, score: float) -> str:
        """根据维度和分数选择基础评语模板"""
        rules = self.suggestion_rules.get(dim, [])
        chosen = ""
        for rule in rules:
            r_min = float(rule.get("min", -math.inf))
            r_max = float(rule.get("max", math.inf))
            if score >= r_min and score < r_max:
                chosen = rule.get("text", "")
                break
        # 如果没匹配到，用一个通用 fallback
        if not chosen:
            chosen = f"在该维度上你的水平约为 NTRP {score:.1f}，可以结合自身情况继续针对性训练。"
        return chosen

    @staticmethod
    def _extra_comment_for_dim(score: float, total_level: float) -> str:
        """
        根据维度分数相对于整体等级的偏差，补充优势/短板/中性评语。
        """
        diff = score - total_level
        if diff >= 0.5:
            return "你在这一项上明显高于整体水平，可以把它当成比赛中的主要得分手段之一。"
        elif diff <= -0.5:
            return "这一项相对是短板，会在比赛中拖慢整体上限，建议作为近期重点练习方向。"
        else:
            return "这一项与整体水平大体一致，可以在保持稳定的基础上，循序渐进地提高质量。"

    # ---------- 优势 / 短板选择 ----------

    def _pick_advantages_and_weaknesses(
        self,
        dim_scores: Dict[str, float],
        top_k: int = 3,
    ) -> Tuple[List[str], List[str]]:
        """选择得分最高和最低的几个维度作为优势和短板"""
        items = sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)
        if not items:
            return [], []

        advantages = [dim for dim, _ in items[:top_k]]
        weaknesses = [dim for dim, _ in reversed(items[-top_k:])]
        return advantages, weaknesses

    # ---------- Summary 文案 ----------

    def _build_summary_text(
        self,
        rounded_level: float,
        level_label: str,
        dim_scores: Dict[str, float],
        dim_comments: Dict[str, str],
        advantages: List[str],
        weaknesses: List[str],
    ) -> str:
        """组合生成完整的评估总结文案"""
        parts: List[str] = []

        # 1) 总体概述
        parts.append(
            f"整体来看，你当前的综合水平约为 NTRP {rounded_level:.1f}（{level_label}）。\n"
        )

        # 2) 优势总结
        if advantages:
            parts.append("你的主要优势在：")
            for dim in advantages:
                name = self.DIMENSION_META.get(dim, dim)
                score = dim_scores.get(dim, 0.0)
                short = self._first_sentence(dim_comments.get(dim, ""))
                parts.append(f"- {name}（约 {score:.1f} 级）：{short}")
            parts.append("")  # 空行

        # 3) 提升重点
        if weaknesses:
            parts.append("当前最值得优先提升的环节是：")
            for dim in weaknesses:
                name = self.DIMENSION_META.get(dim, dim)
                score = dim_scores.get(dim, 0.0)
                short = self._first_sentence(dim_comments.get(dim, ""))
                parts.append(f"- {name}（约 {score:.1f} 级）：{short}")
            parts.append("如果你只想抓重点，建议优先在上述 2～3 个方向投入练习时间。\n")

        # 4) 详细拆解
        parts.append("下面是各个维度的具体评估与建议：\n")

        # 按 dim_meta 定义的顺序输出，体验更统一
        for dim_key, dim_name in self.DIMENSION_META.items():
            if dim_key not in dim_scores:
                continue
            score = dim_scores[dim_key]
            comment = dim_comments.get(dim_key, "")
            parts.append(f"【{dim_name}（约 {score:.1f} 级）】")
            parts.append(comment)
            parts.append("")  # 空行

        return "\n".join(parts).strip()

    @staticmethod
    def _first_sentence(text: str) -> str:
        """
        截取评语的第一句，作为"短标签"。
        用简单的句号/感叹号分割。
        """
        if not text:
            return ""
        for sep in ["。", "！", "!"]:
            if sep in text:
                idx = text.find(sep)
                return text[: idx + 1]
        return text


# =========================
#  简单示例（本地测试用）
# =========================

if __name__ == "__main__":
    # 假设当前目录下有 questions.json 和 dimension_suggestions.json
    base_dir = pathlib.Path(__file__).parent.parent / "config"

    try:
        questions = NTRPEvaluator.load_questions(base_dir / "questions.json")
        suggestions = NTRPEvaluator.load_suggestions(base_dir / "dimension_suggestions.json")

        evaluator = NTRPEvaluator(questions, suggestions, spread=1.0)

        # Demo：模拟一份回答（实际中由小程序前端收集）
        demo_answers = {
            "Q1": "Q1_A3",
            "Q2": "Q2_A4",
            "Q3": "Q3_A4",
            "Q4": "Q4_A3",
            "Q5": "Q5_A3",
            "Q6": "Q6_A3",
            "Q7": "Q7_A3",
            "Q8": "Q8_A3",
            "Q9": "Q9_A3",
            "Q10": "Q10_A3",
            "Q11": "Q11_A3",
            "Q12": "Q12_A3",
        }

        result = evaluator.evaluate(demo_answers)

        print("== NTRP 评估结果 ==")
        print("总等级(raw):", f"{result.total_level:.2f}")
        print("展示等级:", f"NTRP {result.rounded_level:.1f}", f"（{result.level_label}）\n")

        print("各维度得分：")
        for dim, score in result.dimension_scores.items():
            print(f"- {NTRPEvaluator.DIMENSION_META.get(dim, dim)}: {score:.2f}")
        print()

        print("优势维度:", result.advantages)
        print("短板维度:", result.weaknesses)
        print("\n===== 详细评语 =====\n")
        print(result.summary_text)

    except FileNotFoundError as e:
        print(f"配置文件未找到: {e}")
        print("请先创建 questions.json 和 dimension_suggestions.json 文件")