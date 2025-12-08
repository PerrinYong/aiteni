"""
配置管理器

负责加载和管理问题配置、评语规则等配置文件。
提供统一的配置访问接口。
"""

import json
import pathlib
from typing import Dict, List, Any, Optional

from data_models import QuestionConfig, OptionConfig


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_dir: Optional[pathlib.Path] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录路径，如果为None则使用默认路径
        """
        if config_dir is None:
            # 默认配置目录为当前文件上级目录的config文件夹
            self.config_dir = pathlib.Path(__file__).parent.parent / "config"
        else:
            self.config_dir = config_dir
            
        self._questions: Optional[List[QuestionConfig]] = None
        self._suggestions: Optional[Dict[str, List[Dict[str, Any]]]] = None
    
    def load_questions(self) -> List[QuestionConfig]:
        """
        加载问题配置
        
        Returns:
            问题配置列表
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if self._questions is not None:
            return self._questions
            
        questions_file = self.config_dir / "questions.json"
        
        try:
            with open(questions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"问题配置文件不存在: {questions_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"问题配置文件格式错误: {e}")

        try:
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
            
            self._questions = questions
            return questions
            
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"问题配置文件数据结构错误: {e}")
    
    def load_suggestions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        加载评语建议配置
        
        Returns:
            评语规则字典，key为维度名称，value为评语规则列表
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if self._suggestions is not None:
            return self._suggestions
            
        suggestions_file = self.config_dir / "dimension_suggestions.json"
        
        try:
            with open(suggestions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self._suggestions = data
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"评语配置文件不存在: {suggestions_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"评语配置文件格式错误: {e}")
    
    def get_question_by_id(self, question_id: str) -> Optional[QuestionConfig]:
        """
        根据ID获取问题配置
        
        Args:
            question_id: 问题ID
            
        Returns:
            问题配置，如果不存在返回None
        """
        questions = self.load_questions()
        for question in questions:
            if question.id == question_id:
                return question
        return None
    
    def get_option_by_id(self, question_id: str, option_id: str) -> Optional[OptionConfig]:
        """
        根据ID获取选项配置
        
        Args:
            question_id: 问题ID
            option_id: 选项ID
            
        Returns:
            选项配置，如果不存在返回None
        """
        question = self.get_question_by_id(question_id)
        if question is None:
            return None
            
        for option in question.options:
            if option.id == option_id:
                return option
        return None
    
    def validate_answer(self, question_id: str, option_id: str) -> bool:
        """
        验证答案是否有效
        
        Args:
            question_id: 问题ID
            option_id: 选项ID
            
        Returns:
            是否有效
        """
        return self.get_option_by_id(question_id, option_id) is not None
    
    def validate_answers(self, answers: Dict[str, str]) -> bool:
        """
        验证答案集合是否有效
        
        Args:
            answers: 答案字典，key为问题ID，value为选项ID
            
        Returns:
            是否全部有效
        """
        questions = self.load_questions()
        question_ids = {q.id for q in questions}
        
        # 检查是否所有问题都有答案
        if not question_ids.issubset(answers.keys()):
            return False
        
        # 检查每个答案是否有效
        for question_id, option_id in answers.items():
            if not self.validate_answer(question_id, option_id):
                return False
        
        return True
    
    def get_demo_cases(self) -> List[Dict[str, Any]]:
        """
        获取演示用例
        
        Returns:
            演示用例列表
        """
        return [
            {
                "name": "初级选手示例",
                "description": "刚开始学习网球，基础技术尚不稳定",
                "answers": {
                    "Q1": "Q1_A1",    # 很难连续超过3拍
                    "Q2": "Q2_A1",    # 多数球都落在发球线附近
                    "Q3": "Q3_A1",    # 正手动作不完整
                    "Q4": "Q4_A1",    # 基本不敢用反手
                    "Q5": "Q5_A1",    # 经常双误
                    "Q6": "Q6_A1",    # 基本只求发进去
                    "Q7": "Q7_A1",    # 对快球容易慌
                    "Q8": "Q8_A1",    # 很少上网
                    "Q9": "Q9_A1",    # 移动覆盖范围很小
                    "Q10": "Q10_A1",  # 基本没有战术意识
                    "Q11": "Q11_A1",  # 基本都是0:6失败
                    "Q12": "Q12_A1",  # 很少练球
                }
            },
            {
                "name": "中级选手示例",
                "description": "有一定基础，正在提高技术水平",
                "answers": {
                    "Q1": "Q1_A3",    # 能打到6-10拍
                    "Q2": "Q2_A3",    # 有时能打到底线
                    "Q3": "Q3_A3",    # 正手方向控制不错
                    "Q4": "Q4_A3",    # 反手能稳定回场
                    "Q5": "Q5_A3",    # 一发有力量但经常出界
                    "Q6": "Q6_A3",    # 有一定威胁性
                    "Q7": "Q7_A3",    # 中速发球可以稳定接进
                    "Q8": "Q8_A3",    # 正手截击还算稳定
                    "Q9": "Q9_A3",    # 能覆盖大部分底线区域
                    "Q10": "Q10_A3",  # 会观察对手弱点
                    "Q11": "Q11_A3",  # 比赛经常是3:6、4:6
                    "Q12": "Q12_A3",  # 大概每周2次
                }
            },
            {
                "name": "高级选手示例",
                "description": "技术比较全面，有一定比赛经验",
                "answers": {
                    "Q1": "Q1_A5",    # 中速对拉失误很少
                    "Q2": "Q2_A5",    # 能有意识压在对手底线
                    "Q3": "Q3_A5",    # 正手能主动压制对手
                    "Q4": "Q4_A5",    # 反手能主动变线攻击
                    "Q5": "Q5_A5",    # 一发威力大且进球率高
                    "Q6": "Q6_A5",    # 二发也有一定攻击性
                    "Q7": "Q7_A5",    # 能处理大部分发球并反击
                    "Q8": "Q8_A5",    # 网前技术比较全面
                    "Q9": "Q9_A5",    # 移动迅速，覆盖能力强
                    "Q10": "Q10_A5",  # 能制定和执行战术
                    "Q11": "Q11_A5",  # 经常能赢下6:4、6:3
                    "Q12": "Q12_A5",  # 几乎每天都练
                }
            }
        ]