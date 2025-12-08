"""
结果显示器

负责格式化和显示评估结果。
提供多种格式的结果展示方式。
"""

from typing import Dict, List

from data_models import EvaluateResult, ChartData, NTRPConstants, DimensionTag


class ResultDisplay:
    """结果显示器"""
    
    def __init__(self, config_manager):
        """初始化结果显示器"""
        self.config_manager = config_manager
    
    def display_summary_card(self, title: str, result: EvaluateResult) -> None:
        """
        显示简略版卡片（概览卡）
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        print("\n" + "="*50)
        print(f"🎾 {title}")
        print("="*50)
        
        # 卡片顶部 - 总体等级
        print(f"🎾 NTRP {result.rounded_level:.1f}")
        print(f"{result.level_label}")
        
        # 中部 - 能力雷达图概要
        print("\n📊 技术能力概览:")
        self._display_radar_summary(result)
        
        # 底部 - 优势和提升重点
        print("\n💪 主要优势:", end=" ")
        if result.advantages:
            advantage_names = [self.config_manager.get_dimension_name(dim) for dim in result.advantages[:3]]
            print(" / ".join(advantage_names))
        else:
            print("各方面发展较为均衡")
        
        print("🎯 提升重点:", end=" ")
        if result.weaknesses:
            weakness_names = [self.config_manager.get_dimension_name(dim) for dim in result.weaknesses[:3]]
            print(" / ".join(weakness_names))
        else:
            print("继续保持全面发展")
        
        print("\n" + "="*50)
    
    def display_detailed_result(self, title: str, result: EvaluateResult) -> None:
        """
        显示详细版卡片（完整评语版）
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
        
        # 1. 结果头部
        self._display_result_header(result)
        
        # 2. 总体摘要段落
        self._display_overall_summary(result)
        
        # 3. 优势维度 - 展开描述
        self._display_detailed_advantages(result)
        
        # 4. 提升重点 - 展开描述
        self._display_detailed_improvements(result)
        
        # 5. 各维度得分与评语
        self._display_dimension_details_expanded(result)
        
        # 6. 结尾建议
        self._display_final_suggestions(result)
        
        print("="*60)
    
    def display_full_result(self, title: str, result: EvaluateResult) -> None:
        """
        显示完整的评估结果（兼容旧接口）
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        self.display_detailed_result(title, result)
    
    def display_simple_result(self, title: str, result: EvaluateResult) -> None:
        """
        显示简化的评估结果
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        print(f"\n📋 {title}")
        print("-" * 40)
        
        # 显示基本信息
        print(f"🎾 NTRP等级: {result.rounded_level:.1f} ({result.level_label})")
        
        # 显示优势和短板
        if result.advantages:
            advantage_names = [self.config_manager.get_dimension_name(dim) for dim in result.advantages]
            print(f"💪 优势项目: {', '.join(advantage_names)}")
        
        if result.weaknesses:
            weakness_names = [self.config_manager.get_dimension_name(dim) for dim in result.weaknesses]
            print(f"📈 改进方向: {', '.join(weakness_names)}")
        
        print()
    
    def _display_result_header(self, result: EvaluateResult) -> None:
        """显示结果头部"""
        print(f"\n🎾 总体等级: NTRP {result.rounded_level:.1f} ({result.level_label})")
        print(f"原始得分: {result.total_level:.2f}")
    
    def _display_overall_summary(self, result: EvaluateResult) -> None:
        """显示总体摘要段落"""
        print(f"\n整体来看，你当前的综合水平约为 NTRP {result.rounded_level:.1f}（{result.level_label}）。")
        
        summary_parts = []
        if result.advantages:
            advantage_names = [self.config_manager.get_dimension_name(dim) for dim in result.advantages]
            summary_parts.append(f"在同水平玩家中，你已经具备一定的实战竞争力，尤其在{'、'.join(advantage_names)}上表现较好。")
        
        if result.weaknesses:
            weakness_names = [self.config_manager.get_dimension_name(dim) for dim in result.weaknesses]
            summary_parts.append(f"如果能够补上{'、'.join(weakness_names)}等环节，你的整体实力还有明显上升空间。")
        
        for part in summary_parts:
            print(part)
    
    def _display_radar_summary(self, result: EvaluateResult) -> None:
        """显示雷达图概要"""
        # 从配置获取维度分组
        knowledge = self.config_manager.load_tennis_knowledge()
        dimension_groups = knowledge.get("dimension_groups", {})
        
        # 按分组显示核心维度得分
        for group_name, dimensions in dimension_groups.items():
            group_dims = [(dim, result.dimension_scores.get(dim)) for dim in dimensions 
                         if dim in result.dimension_scores]
            
            if group_dims:
                dim_scores = [f"{self.config_manager.get_dimension_name(dim)}({score:.1f})" 
                             for dim, score in group_dims if score is not None]
                print(f"   {group_name}: {' / '.join(dim_scores)}")
    
    def _display_detailed_advantages(self, result: EvaluateResult) -> None:
        """显示优势维度展开描述"""
        if not result.advantages:
            return
            
        print(f"\n💪 你的主要优势：")
        print()
        
        for dim in result.advantages:
            dim_name = self.config_manager.get_dimension_name(dim)
            score = result.dimension_scores.get(dim, 0)
            comment = result.dimension_comments.get(dim, "")
            
            print(f"- {dim_name}（约 {score:.1f} 级）：")
            # 分析现状和建议
            if comment:
                sentences = comment.split("。")
                current_state = sentences[0] + "。" if sentences else ""
                suggestion = self.config_manager.get_advantage_suggestion(dim)
                print(f"  {current_state}")
                print(f"  {suggestion}")
            print()
    
    def _display_detailed_improvements(self, result: EvaluateResult) -> None:
        """显示提升重点展开描述"""
        if not result.weaknesses:
            return
            
        print(f"🎯 当前最值得优先提升的环节是：")
        print()
        
        for dim in result.weaknesses:
            dim_name = self.config_manager.get_dimension_name(dim)
            score = result.dimension_scores.get(dim, 0)
            comment = result.dimension_comments.get(dim, "")
            
            print(f"- {dim_name}（约 {score:.1f} 级）：")
            # 分析问题和练习建议
            if comment:
                sentences = comment.split("。")
                problem = sentences[0] + "。" if sentences else ""
                suggestion = self.config_manager.get_improvement_suggestion(dim)
                print(f"  {problem}")
                print(f"  {suggestion}")
            print()
        
        print("如果你只想抓重点，建议优先在上述 2～3 个方向投入练习时间。")
        print()
    
    def _display_dimension_details_expanded(self, result: EvaluateResult) -> None:
        """显示各维度得分与评语（逐维度展开）"""
        print("📝 各维度详细评估与建议：")
        print()
        
        # 从配置获取维度分组
        knowledge = self.config_manager.load_tennis_knowledge()
        dimension_groups = knowledge.get("dimension_groups", {})
        
        for group_name, dimensions in dimension_groups.items():
            group_has_content = any(dim in result.dimension_scores for dim in dimensions)
            if group_has_content:
                for dim in dimensions:
                    if dim in result.dimension_scores:
                        dim_name = self.config_manager.get_dimension_name(dim)
                        score = result.dimension_scores[dim]
                        comment = result.dimension_comments.get(dim, "暂无评语")
                        
                        print(f"【{dim_name}（约 {score:.1f} 级）】")
                        # 分离基础评语和相对评语
                        base_comment, relative_comment = self._split_dimension_comment(comment, score, result.rounded_level)
                        print(f"{base_comment}")
                        print(f"{relative_comment}")
                        print()
    
    def _display_final_suggestions(self, result: EvaluateResult) -> None:
        """显示结尾建议"""
        print("如果你每周有 2～3 次打球时间，建议在保证正常对抗的基础上，每周抽出 1 次做'针对短板的专项练习'，例如专门练发球+第一拍、底线深度控制等。")
        print("每隔 2～3 个月重新做一次评估，可以观察自己在各个维度上的变化趋势，也可以将本评估结果分享给教练，作为排课与训练重点的参考。")
        print()
    
    def _display_level_description(self, level: float) -> None:
        """显示等级详细说明"""
        description = self.config_manager.get_level_description(level)
        if description:
            print(f"💡 等级说明: {description}")
    
    def _display_dimension_analysis(self, result: EvaluateResult) -> None:
        """显示维度分析"""
        print(f"\n📊 技术维度分析:")
        print("-" * 40)
        
        # 按分组显示
        for group_name, dimensions in NTRPConstants.DIMENSION_GROUPS.items():
            group_dims = [(dim, result.dimension_scores.get(dim)) for dim in dimensions 
                         if dim in result.dimension_scores]
            
            if group_dims:
                print(f"\n🔍 {group_name}:")
                for dim, score in group_dims:
                    if score is not None:
                        dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
                        bar = self._create_score_bar(score, result.rounded_level)
                        tag = self._get_dimension_tag_text(score, result.rounded_level)
                        print(f"   {dim_name:8} {score:.1f} {bar} {tag}")
    
    def _create_score_bar(self, score: float, total_level: float) -> str:
        """创建分数条形图"""
        # 将分数转换为条形长度 (1-7 -> 0-20)
        bar_length = int((score - 1.0) / 6.0 * 20)
        bar_length = max(0, min(20, bar_length))
        
        # 确定颜色（相对于总体水平）
        diff = score - total_level
        if diff >= 0.5:
            # 优势项目用绿色
            filled = "█" * bar_length
            empty = "░" * (20 - bar_length)
            return f"[{filled}{empty}]"
        elif diff <= -0.5:
            # 短板项目用红色标记
            filled = "▓" * bar_length
            empty = "░" * (20 - bar_length)
            return f"[{filled}{empty}]"
        else:
            # 平衡项目用蓝色
            filled = "■" * bar_length
            empty = "░" * (20 - bar_length)
            return f"[{filled}{empty}]"
    
    def _get_dimension_tag_text(self, score: float, total_level: float) -> str:
        """获取维度标签文本"""
        diff = score - total_level
        if diff >= 0.5:
            return "💪 优势"
        elif diff <= -0.5:
            return "📈 短板"
        else:
            return "⚖️ 均衡"
    
    def _display_strengths_weaknesses(self, result: EvaluateResult) -> None:
        """显示优势和短板分析"""
        print(f"\n🎯 技术特点分析:")
        print("-" * 40)
        
        if result.advantages:
            print("💪 优势项目:")
            for i, dim in enumerate(result.advantages, 1):
                dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
                score = result.dimension_scores.get(dim, 0)
                print(f"   {i}. {dim_name} (NTRP {score:.1f})")
                # 显示详细评语的第一句
                comment = result.dimension_comments.get(dim, "")
                short_comment = comment.split("。")[0] + "。" if "。" in comment else comment[:50] + "..."
                print(f"      {short_comment}")
        
        if result.weaknesses:
            print("\n📈 改进方向:")
            for i, dim in enumerate(result.weaknesses, 1):
                dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
                score = result.dimension_scores.get(dim, 0)
                print(f"   {i}. {dim_name} (NTRP {score:.1f})")
                # 显示详细评语的第一句
                comment = result.dimension_comments.get(dim, "")
                short_comment = comment.split("。")[0] + "。" if "。" in comment else comment[:50] + "..."
                print(f"      {short_comment}")
    
    def _display_chart_summary(self, chart_data: ChartData) -> None:
        """显示图表数据概要"""
        print(f"\n📈 训练优先级建议:")
        print("-" * 40)
        
        if chart_data.priority_list:
            for item in chart_data.priority_list:
                print(f"{item.rank}. {item.label} (差距: {item.gap:.1f})")
                print(f"   💡 {item.suggestion}")
                print()
        else:
            print("   各维度发展较为均衡，继续保持全面训练即可。")
    
    def _display_summary(self, result: EvaluateResult) -> None:
        """显示总体评语"""
        print(f"\n📝 综合评语:")
        print("-" * 40)
        
        # 将长文本分段显示
        summary_lines = result.summary_text.split("。")
        for line in summary_lines:
            line = line.strip()
            if line:
                print(f"   {line}。")
    
    def display_evaluation_tips(self) -> None:
        """显示评估提示信息"""
        print("\n📋 NTRP评估说明:")
        print("-" * 40)
        print("• NTRP (National Tennis Rating Program) 是国际通用的网球水平分级标准")
        print("• 分级范围从1.0到7.0，每0.5为一个档次")
        print("• 评估涵盖底线、发球、网前等多个技术维度")
        print("• 建议根据实际情况如实回答，以获得准确的评估结果")
        print("• 评估结果可作为选择比赛对手和训练方向的参考")
    
    def _display_final_suggestions(self, result: EvaluateResult) -> None:
        """显示结尾建议"""
        print("如果你每周有 2～3 次打球时间，建议在保证正常对抗的基础上，每周抽出 1 次做'针对短板的专项练习'，例如专门练发球+第一拍、底线深度控制等。")
        print("每隔 2～3 个月重新做一次评估，可以观察自己在各个维度上的变化趋势，也可以将本评估结果分享给教练，作为排课与训练重点的参考。")
        print()
        
    def display_dimension_details(self, result: EvaluateResult) -> None:
        """显示详细的维度评语（兼容旧接口）"""
        self._display_dimension_details_expanded(result)

    def _generate_advantage_suggestion(self, dimension: str, current_state: str) -> str:
        """生成优势维度的建议"""
        suggestions = {
            "baseline": "你可以多多利用底线对拉作为主要得分手段，在比赛中通过深球和变线控制比赛节奏。",
            "forehand": "建议在比赛中多使用正手主动进攻，这是你的优势武器，可以通过正手制造得分机会。",
            "backhand": "反手已经比较稳定，可以在比赛中更多地使用反手变线和深球来压制对手。",
            "serve": "发球威胁较大，可以利用发球优势在比赛中控制主动权，多练习发球后第一拍的连击。",
            "return": "接发球表现出色，可以在对手发球局中更主动地寻找机会，转守为攻。",
            "net": "网前技术较好，建议多创造上网机会，利用网前优势结束回合。",
            "footwork": "步法移动能力强，可以在比赛中更大胆地调动对手，利用移动优势获得有利击球位置。",
            "tactics": "战术意识出色，继续发挥这一优势，在比赛中多观察对手弱点并制定针对性战术。",
            "match_result": "实战成绩不错，说明比赛能力强，可以多参加更高水平的比赛来检验和提升自己。",
            "training": "训练频率很好，这是技术持续进步的基础，可以在此基础上提高训练的针对性。"
        }
        
        return suggestions.get(dimension, "这是你的优势项目，在比赛中可以多多利用。")
    
    def _generate_improvement_suggestion(self, dimension: str, problem: str) -> str:
        """生成改进建议"""
        suggestions = {
            "baseline": "建议刻意练习深球和落点变化，例如多做'对角深球 + 直线变线'的对打练习，让你的底线球既稳又有威胁。",
            "forehand": "可以重点练习正手挥拍动作和击球时机，逐步提高正手的稳定性和威胁性。",
            "backhand": "建议加强反手技术练习，可以从稳定的切削开始，逐步过渡到上旋反手。",
            "serve": "可以逐步区分一发和二发，在保证二发稳定的前提下，提升一发力量和落点变化，并加入一定旋转。",
            "return": "建议多练习对不同类型发球的接发，提高反应速度和回球质量，特别是对快速发球的处理。",
            "net": "加强网前技术训练，特别是低球截击、反手截击和连续截击，让网前技术更全面。",
            "footwork": "建议多练习'左右调动 + 短球/高吊'组合，让你在多变球路下仍能打出稳定回球。",
            "tactics": "学习基本战术套路，多观察不同类型对手的弱点，逐步建立自己的比赛套路。",
            "match_result": "多参与实战比赛，积累比赛经验，学会在压力下保持技术稳定性。",
            "training": "增加训练频率和强度，可以制定更有针对性的训练计划，重点突破薄弱环节。"
        }
        
        return suggestions.get(dimension, "建议针对这个方面制定专项训练计划，重点突破。")
    
    def _split_dimension_comment(self, comment: str, score: float, total_level: float) -> tuple:
        """分离维度评语为基础评语和相对评语"""
        # 按句子分割
        sentences = comment.split("。")
        
        # 基础评语（通常是第一句或前几句）
        base_sentences = []
        relative_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 如果包含相对比较的关键词，归为相对评语
            if any(keyword in sentence for keyword in ["优势", "短板", "高于", "低于", "明显", "相对", "整体水平"]):
                relative_sentences.append(sentence)
            else:
                base_sentences.append(sentence)
        
        base_comment = "。".join(base_sentences) + "。" if base_sentences else ""
        
        # 如果没有现成的相对评语，生成一个
        if not relative_sentences:
            diff = score - total_level
            if diff >= 0.5:
                relative_comment = self.config_manager.get_relative_evaluation_text("strong_advantage")
            elif diff <= -0.5:
                relative_comment = self.config_manager.get_relative_evaluation_text("weakness")
            else:
                relative_comment = self.config_manager.get_relative_evaluation_text("balanced")
        else:
            relative_comment = "。".join(relative_sentences) + "。"
        
        return base_comment, relative_comment