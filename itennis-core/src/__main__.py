"""
Command Line Interface for What2Eat

提供命令行交互界面，模拟聊天体验
"""

import os
import sys
import json
from typing import List, Dict, Any

# 添加what2eat-core到Python搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')  # what2eat-core目录
sys.path.insert(0, project_root)

from src.interaction.chatbot import ChatBot
from src.data_loader import DishLoader
from src.utils import debug, info, error, set_debug_mode


class CLIInterface:
    """命令行界面"""
    
    def __init__(self):
        debug("CLIInterface 初始化开始")
        self.chatbot: ChatBot = None
        self.current_state: Dict[str, Any] = {}
        self._load_data()
        debug("CLIInterface 初始化完成")
    
    def _load_data(self):
        """初始化ChatBot"""
        debug("开始初始化ChatBot")
        try:
            # 创建菜品数据提供者
            dish_provider = DishLoader.create_service_provider()
            
            # 初始化ChatBot（不再需要预加载菜品数据）
            self.chatbot = ChatBot(dish_provider=dish_provider)
            info("ChatBot初始化完成")
            print("✅ ChatBot初始化完成")
            debug("聊天机器人初始化完成")
        except Exception as e:
            error(f"初始化ChatBot失败: {e}")
            print(f"❌ 初始化ChatBot失败: {e}")
            sys.exit(1)
    
    def run(self):
        """运行主程序"""
        info("启动What2Eat主程序")
        self._print_welcome()
        
        try:
            # 开始对话
            debug("开始对话流程")
            self.current_state = self.chatbot.start_conversation()
            debug(f"初始对话状态: {self.current_state.get('status')}")
            
            while True:
                if self.current_state.get("status") == "question":
                    debug("处理问题状态")
                    self._handle_question()
                elif self.current_state.get("status") == "result":
                    debug("处理结果状态")
                    self._handle_result()
                    break
                elif self.current_state.get("status") == "error":
                    error_msg = self.current_state.get('message', '未知错误')
                    error(f"对话状态错误: {error_msg}")
                    print(f"❌ {error_msg}")
                    break
                else:
                    error(f"未知对话状态: {self.current_state.get('status')}")
                    print("❌ 未知状态，程序结束")
                    break
        
        except KeyboardInterrupt:
            info("用户中断程序")
            print("\\n👋 感谢使用，再见！")
        except Exception as e:
            error(f"程序运行出错: {e}")
            print(f"❌ 程序运行出错: {e}")
    
    def _print_welcome(self):
        """打印欢迎信息"""
        print("🍽️" + "=" * 50)
        print("     欢迎使用 What2Eat - 今天吃什么？")
        print("     零压力聊天，轻松决定今天这一顿！")
        print("=" * 52)
        print()
    
    def _handle_question(self):
        """处理问题状态"""
        question_data = self.current_state
        question_id = question_data.get('node_id', 'unknown')
        question_text = question_data.get('question', '')
        
        debug(f"处理问题节点: {question_id}")
        debug(f"问题内容: {question_text}")
        
        print(f"🤖 {question_text}")
        print()
        
        options = question_data.get('options', [])
        question_type = question_data.get('question_type')
        
        debug(f"问题类型: {question_type}, 选项数量: {len(options)}")
        
        if not options:
            error(f"问题 {question_id} 没有可选选项")
            print("❌ 没有可选选项")
            return
        
        # 显示选项
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option['label']}")
        print()
        
        if question_type == "multi_choice":
            print("💡 提示: 可以选择多个选项，用逗号分隔（如: 1,3,5），或直接按Enter跳过")
            print("          如果只选一个，直接输入数字即可（如: 2）")
        
        # 获取用户输入
        while True:
            try:
                user_input = input("👤 请选择: ").strip()
                debug(f"用户输入: '{user_input}'")
                
                if not user_input:
                    # 空输入，对于多选题表示跳过
                    selected_values = []
                    debug("用户选择跳过")
                    break
                
                # 解析用户输入
                if question_type == "multi_choice":
                    # 多选题：解析逗号分隔的数字
                    indices = [int(x.strip()) for x in user_input.split(',')]
                else:
                    # 单选题
                    indices = [int(user_input)]
                
                # 验证选择
                selected_values = []
                for idx in indices:
                    if 1 <= idx <= len(options):
                        selected_values.append(options[idx - 1]['value'])
                        debug(f"用户选择选项 {idx}: {options[idx - 1]['value']}")
                    else:
                        raise ValueError(f"选项 {idx} 不存在")
                
                break
                
            except ValueError as e:
                debug(f"用户输入错误: {e}")
                print(f"❌ 输入无效: {e}")
                print(f"   请输入1-{len(options)}之间的数字")
                if question_type == "multi_choice":
                    print("   多个选项请用逗号分隔")
                print()
        
        # 处理用户响应
        debug(f"向聊天机器人发送选择: {selected_values}")
        print()
        self.current_state = self.chatbot.process_user_response(selected_values)
        debug(f"新的对话状态: {self.current_state.get('status')}")
    
    def _handle_result(self):
        """处理结果状态"""
        result = self.current_state
        
        debug("开始处理推荐结果")
        debug(f"决策模式: {result.get('decision_mode')}")
        
        print("🎉 推荐结果出炉！")
        print("=" * 40)
        print()
        
        # 显示推荐理由
        if result.get('reasoning'):
            print(f"💭 {result['reasoning']}")
            print()
        
        # 显示健康模式的详细推荐信息
        if result.get('decision_mode') == 'health' and result.get('health_recommendations'):
            self._print_health_recommendations(result['health_recommendations'])
            print()
        
        # 显示主推荐
        recommended = result.get('recommended_dish')
        if recommended:
            self._print_dish_card(recommended, "🌟 今日推荐")
        else:
            print("😅 抱歉，没有找到合适的推荐")
            return
        
        # 显示备选
        alternatives = result.get('alternative_dishes', [])
        if alternatives:
            print()
            print("🎲 备选方案:")
            for i, dish in enumerate(alternatives, 1):
                self._print_dish_card(dish, f"备选 {i}")
        
        print()
        print("=" * 40)
        
        # 用户操作菜单
        self._show_action_menu()
    
    def _print_dish_card(self, dish: Dict[str, Any], title: str):
        """打印菜品卡片"""
        print(f"🎴 {title}")
        print(f"   📝 {dish['name']}")
        if dish.get('description'):
            print(f"   💬 {dish['description']}")
        if dish.get('cuisine'):
            print(f"   🏷️  {dish['cuisine']}")
        if dish.get('category'):
            print(f"   📂 {dish['category']}")
        print()
    
    def _print_health_recommendations(self, health_info: Dict[str, Any]):
        """打印健康模式的详细推荐信息"""
        if not health_info:
            return
            
        reason = health_info.get('reason', {})
        advice = health_info.get('advice', {})
        
        print("📋 健康分析与建议:")
        print("─" * 35)
        
        # 显示目标和原则
        if reason.get('goal'):
            print(f"🎯 您的目标: {reason['goal']}")
            
        if reason.get('principles'):
            print("📏 推荐原则:")
            for principle in reason['principles']:
                print(f"   • {principle}")
        
        # 显示菜品分析
        if reason.get('dish_analysis'):
            print("🔍 这道菜的特点:")
            for analysis in reason['dish_analysis']:
                print(f"   • {analysis}")
        
        # 显示配量和运动建议
        if advice:
            print("💡 食用建议:")
            if advice.get('portion_text'):
                print(f"   🍽️  配量: {advice['portion_text']}")
            
            if advice.get('exercise_text'):
                print(f"   🏃 运动: {advice['exercise_text']}")
                if advice.get('cardio_minutes') or advice.get('strength_minutes'):
                    exercise_details = []
                    if advice.get('cardio_minutes', 0) > 0:
                        exercise_details.append(f"有氧{advice['cardio_minutes']}分钟")
                    if advice.get('strength_minutes', 0) > 0:
                        exercise_details.append(f"力量训练{advice['strength_minutes']}分钟")
                    if exercise_details:
                        print(f"       ({' + '.join(exercise_details)})")
    
    def _show_action_menu(self):
        """显示用户操作菜单"""
        while True:
            print("请选择操作:")
            print("  1. ✅ 就吃推荐的这个")
            print("  2. 🎲 换一批看看")
            print("  3. 🔍 查看详细信息")
            print("  4. 🔄 重新开始")
            print("  5. 👋 退出程序")
            print()
            
            try:
                choice = input("👤 请选择: ").strip()
                debug(f"用户选择操作: {choice}")
                
                if choice == "1":
                    recommended = self.current_state.get('recommended_dish')
                    if recommended:
                        info(f"用户确认选择: {recommended['name']}")
                        print(f"\\n🎉 好，那这顿就定 **{recommended['name']}** 啦！")
                        print("祝你吃得开心 🥢✨")
                    break
                    
                elif choice == "2":
                    debug("用户选择重新推荐")
                    print("\\n🎲 正在为您重新推荐...")
                    new_result = self.chatbot.regenerate_recommendations()
                    if new_result.get("status") == "result":
                        debug("重新推荐成功")
                        self.current_state = new_result
                        self._handle_result()
                    else:
                        error_msg = new_result.get('message', '重新推荐失败')
                        error(f"重新推荐失败: {error_msg}")
                        print(f"❌ {error_msg}")
                    break
                    
                elif choice == "3":
                    debug("用户选择查看详细信息")
                    self._show_detailed_info()
                    
                elif choice == "4":
                    debug("用户选择重新开始")
                    print("\\n🔄 重新开始...")
                    print()
                    self.current_state = self.chatbot.start_conversation()
                    break
                    
                elif choice == "5":
                    info("用户选择退出程序")
                    print("\\n👋 感谢使用，再见！")
                    sys.exit(0)
                    
                else:
                    print("❌ 请输入1-5之间的数字\\n")
                    
            except KeyboardInterrupt:
                print("\\n👋 感谢使用，再见！")
                sys.exit(0)
    
    def _show_detailed_info(self):
        """显示详细信息"""
        print("\\n📊 详细信息:")
        print(f"  决策模式: {self.current_state.get('decision_mode')}")
        
        context = self.chatbot.get_current_context()
        if context:
            print("  上下文信息:")
            for key, value in context.items():
                if isinstance(value, dict):
                    print(f"    {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"      {sub_key}: {sub_value}")
                else:
                    print(f"    {key}: {value}")
        
        print("\\n按Enter键返回...")
        input()


def main():
    """主函数"""
    # 检查是否启用Debug模式
    debug_env = os.getenv('WHAT2EAT_DEBUG', 'false').lower()
    if debug_env in ('true', '1', 'yes', 'on'):
        set_debug_mode(True)
        debug("Debug模式已启用")
    
    try:
        cli = CLIInterface()
        cli.run()
    except Exception as e:
        error(f"程序启动失败: {e}")
        print(f"❌ 程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()