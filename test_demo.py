"""
artfish 功能演示测试文件

这个文件展示了 artfish 系统的各种功能和用例：
1. 基本执行流程
2. 依赖关系处理（DAG）
3. 错误处理和失败恢复
4. 多个后端适配器
5. 执行追踪和统计
6. 计划验证
"""
import sys
from pathlib import Path

try:
    from artfish.core.intent import ArtIntent
    from artfish.core.runtime import Runtime
    from artfish.core.plan import ExecutionPlan, AtomicAction, ActionType
    from artfish.backends.mock import MockBackend
except ImportError:
    artfish_dir = Path(__file__).parent
    parent_dir = artfish_dir.parent
    sys.path.insert(0, str(parent_dir))
    from artfish.core.intent import ArtIntent
    from artfish.core.runtime import Runtime
    from artfish.core.plan import ExecutionPlan, AtomicAction, ActionType
    from artfish.backends.mock import MockBackend


def demo_basic_execution():
    """演示1: 基本执行流程"""
    print("=" * 80)
    print("演示1: 基本执行流程")
    print("=" * 80)
    
    runtime = Runtime()
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    intent = ArtIntent(
        goals=["create_artwork", "apply_filter"],
        constraints={"resolution": "512x512"},
        metadata={"demo": "basic"}
    )
    
    plan = runtime.compile(intent)
    trace = runtime.run(plan)
    
    print(f"[OK] 成功执行 {len(plan.actions)} 个操作")
    print(f"[OK] 总成本: {trace.total_cost:.2f}")
    print(f"[OK] 成功率: {trace.get_statistics()['success_rate']:.1f}%")
    print()


def demo_dependency_handling():
    """演示2: 依赖关系处理（DAG拓扑排序）"""
    print("=" * 80)
    print("演示2: 依赖关系处理（DAG拓扑排序）")
    print("=" * 80)
    
    # 手动创建带有依赖关系的计划
    action1 = AtomicAction(
        action_id="generate_base",
        action_type=ActionType.GENERATE,
        parameters={"prompt": "base image"}
    )
    
    action2 = AtomicAction(
        action_id="transform_style",
        action_type=ActionType.TRANSFORM,
        parameters={"style": "abstract"},
        dependencies=["generate_base"]  # 依赖于 action1
    )
    
    action3 = AtomicAction(
        action_id="apply_filter",
        action_type=ActionType.FILTER,
        parameters={"filter": "blur"},
        dependencies=["transform_style"]  # 依赖于 action2
    )
    
    plan = ExecutionPlan(
        plan_id="demo_dag",
        actions=[action3, action1, action2]  # 故意打乱顺序
    )
    
    # 验证计划
    is_valid, error = plan.validate()
    print(f"[OK] 计划验证: {'通过' if is_valid else '失败'}")
    
    # 获取执行顺序（应该按照依赖关系排序）
    execution_order = plan.get_execution_order()
    print(f"[OK] 执行顺序: {' -> '.join([a.action_id for a in execution_order])}")
    print()


def demo_error_handling():
    """演示3: 错误处理和失败恢复"""
    print("=" * 80)
    print("演示3: 错误处理和失败恢复")
    print("=" * 80)
    
    runtime = Runtime()
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    # 创建一个会失败的操作
    action_fail = AtomicAction(
        action_id="failing_action",
        action_type=ActionType.GENERATE,
        parameters={"should_fail": True}  # 触发模拟失败
    )
    
    action_success = AtomicAction(
        action_id="success_action",
        action_type=ActionType.GENERATE,
        parameters={"should_fail": False}
    )
    
    plan = ExecutionPlan(
        plan_id="demo_error",
        actions=[action_fail, action_success]
    )
    
    trace = runtime.run(plan)
    stats = trace.get_statistics()
    
    print(f"[OK] 总操作数: {stats['total_actions']}")
    print(f"[OK] 成功操作: {stats['completed_actions']}")
    print(f"[OK] 失败操作: {stats['failed_actions']}")
    print(f"[OK] 系统继续运行，未因错误崩溃")
    print()


def demo_multiple_backends():
    """演示4: 多个后端适配器"""
    print("=" * 80)
    print("演示4: 多个后端适配器")
    print("=" * 80)
    
    runtime = Runtime()
    
    # 注册多个后端
    backend1 = MockBackend(name="backend_fast", latency=0.05)
    backend2 = MockBackend(name="backend_slow", latency=0.2)
    
    runtime.register_backend(backend1)
    runtime.register_backend(backend2)
    
    # 列出所有后端
    dispatcher = runtime._dispatcher
    backends = dispatcher.list_backends()
    print(f"[OK] 已注册后端: {', '.join(backends)}")
    
    # 使用后端提示
    action = AtomicAction(
        action_id="preferred_action",
        action_type=ActionType.GENERATE,
        backend_hint="backend_fast"  # 指定使用特定后端
    )
    
    plan = ExecutionPlan(plan_id="demo_backends", actions=[action])
    trace = runtime.run(plan)
    
    # 检查使用了哪个后端
    for event in trace.events:
        if event.status.value == "completed" and event.metadata.get("backend"):
            print(f"[OK] 操作使用了后端: {event.metadata['backend']}")
    print()


def demo_statistics():
    """演示5: 执行统计和分析"""
    print("=" * 80)
    print("演示5: 执行统计和分析")
    print("=" * 80)
    
    runtime = Runtime()
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    intent = ArtIntent(
        goals=["goal1", "goal2", "goal3"],
        constraints={"test": True}
    )
    
    plan = runtime.compile(intent)
    trace = runtime.run(plan)
    
    stats = trace.get_statistics()
    
    print("执行统计信息:")
    print(f"  - 总事件数: {stats['total_events']}")
    print(f"  - 总操作数: {stats['total_actions']}")
    print(f"  - 成功操作: {stats['completed_actions']}")
    print(f"  - 失败操作: {stats['failed_actions']}")
    print(f"  - 成功率: {stats['success_rate']:.1f}%")
    print(f"  - 总成本: {stats['total_cost']:.2f}")
    print(f"  - 执行时长: {stats['duration_seconds']:.2f} 秒")
    print(f"  - 状态分布: {stats['status_counts']}")
    print()


def demo_plan_validation():
    """演示6: 计划验证（循环依赖检测等）"""
    print("=" * 80)
    print("演示6: 计划验证（循环依赖检测等）")
    print("=" * 80)
    
    # 测试1: 有效的计划
    action1 = AtomicAction(action_id="a1", action_type=ActionType.GENERATE)
    action2 = AtomicAction(action_id="a2", action_type=ActionType.TRANSFORM, dependencies=["a1"])
    plan_valid = ExecutionPlan(plan_id="valid", actions=[action1, action2])
    
    is_valid, error = plan_valid.validate()
    print(f"[OK] 有效计划验证: {'通过' if is_valid else f'失败 - {error}'}")
    
    # 测试2: 循环依赖
    action3 = AtomicAction(action_id="a3", action_type=ActionType.GENERATE, dependencies=["a4"])
    action4 = AtomicAction(action_id="a4", action_type=ActionType.TRANSFORM, dependencies=["a3"])
    plan_cycle = ExecutionPlan(plan_id="cycle", actions=[action3, action4])
    
    is_valid, error = plan_cycle.validate()
    print(f"[OK] 循环依赖检测: {'未检测到' if is_valid else f'检测到 - {error}'}")
    
    # 测试3: 缺失依赖
    action5 = AtomicAction(action_id="a5", action_type=ActionType.GENERATE, dependencies=["nonexistent"])
    plan_missing = ExecutionPlan(plan_id="missing", actions=[action5])
    
    is_valid, error = plan_missing.validate()
    print(f"[OK] 缺失依赖检测: {'未检测到' if is_valid else f'检测到 - {error}'}")
    print()


def demo_trace_analysis():
    """演示7: 追踪分析和查询"""
    print("=" * 80)
    print("演示7: 追踪分析和查询")
    print("=" * 80)
    
    runtime = Runtime()
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    intent = ArtIntent(goals=["analyze_me"])
    plan = runtime.compile(intent)
    trace = runtime.run(plan)
    
    # 查询特定操作的事件
    if plan.actions:
        action_id = plan.actions[0].action_id
        action_events = trace.get_events_by_action(action_id)
        print(f"[OK] 操作 '{action_id}' 的事件数: {len(action_events)}")
        print(f"  事件状态序列: {' -> '.join([e.status.value for e in action_events])}")
    
    # 转换为JSON
    json_output = trace.to_json()
    print(f"[OK] 追踪JSON长度: {len(json_output)} 字符")
    print()


def main():
    """运行所有演示"""
    print("\n" + "=" * 80)
    print("artfish 功能演示测试")
    print("=" * 80 + "\n")
    
    try:
        demo_basic_execution()
        demo_dependency_handling()
        demo_error_handling()
        demo_multiple_backends()
        demo_statistics()
        demo_plan_validation()
        demo_trace_analysis()
        
        print("=" * 80)
        print("[SUCCESS] 所有演示完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
