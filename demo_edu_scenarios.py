import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core.gateway import Gateway
from core.intent import ArtIntent
from rich.console import Console
from rich.panel import Panel

console = Console()
gateway = Gateway()

def demo_tutor():
    console.print(Panel("[bold cyan]场景 1: 智能辅导 (启发式答疑)[/bold cyan]"))
    intent = ArtIntent(goals=["讲解勾股定理"], constraints={"style": "educational"})
    trace = gateway.execute_intent(intent)
    for event in trace.events:
        if event.action_id == "tutor_heuristic_tutor":
            console.print(f"[bold]学生提问:[/bold] 什么是勾股定理？")
            console.print(f"[bold]EduSense 回复:[/bold] {event.result_payload}")

def demo_writing():
    console.print(Panel("[bold green]场景 2: 作文辅导 (修辞与结构)[/bold green]"))
    content = "春天来了。小草偷偷地从土里钻出来，嫩嫩的，绿绿的。风轻悄悄的，草软绵绵的。"
    
    # 手动调用技能演示
    rhetoric = gateway.skill_manager.execute("writing", "detect_rhetoric", content=content)
    evaluation = gateway.skill_manager.execute("writing", "evaluate_structure", content=content)
    
    console.print(f"[bold]作文片段:[/bold] {content}")
    console.print(f"[bold]修辞识别:[/bold] {rhetoric}")
    console.print(f"[bold]结构评价:[/bold] {evaluation['suggestion']}")

def demo_exam():
    console.print(Panel("[bold yellow]场景 3: 智能测评 (错题分析)[/bold yellow]"))
    
    # 模拟错题分析
    analysis = gateway.skill_manager.execute("exam", "analyze_error_pattern", 
                                          student_answer="24", 
                                          correct_answer="25")
    
    # 模拟生成针对性练习
    quiz = gateway.skill_manager.execute("exam", "generate_quiz", kp_title="勾股定理", difficulty=2)
    
    console.print(f"[bold]错题场景:[/bold] 学生回答 24，正确答案 25")
    console.print(f"[bold]EduSense 分析:[/bold] {analysis}")
    console.print(f"[bold]针对性推送:[/bold] {quiz['question']['q']} (难度: {quiz['question']['level']})")

if __name__ == "__main__":
    demo_tutor()
    console.print("\n")
    demo_writing()
    console.print("\n")
    demo_exam()
