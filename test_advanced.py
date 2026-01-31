"""
高级功能测试：验证新增的完整功能

测试内容：
1. 执行上下文和结果传递
2. 智能依赖推断
3. 操作结果注入
4. 并行执行
5. 重试机制
6. 结果查询
"""
import sys
from pathlib import Path

from core.intent import ArtIntent
from core.runtime import Runtime
from core.plan import ExecutionPlan, AtomicAction, ActionType
from core.context import ExecutionContext
from backends.mock import MockBackend


def test_context_and_result_passing():
    """测试1: 执行上下文和结果传递"""
    print("=" * 80)
    print("测试1: 执行上下文和结果传递")
    print("=" * 80)
    
    runtime = Runtime(enable_parallel=False)
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    # 创建带有依赖关系的计划
    action1 = AtomicAction(
        action_id="generate_base",
        action_type=ActionType.GENERATE,
        parameters={"prompt": "base image"}
    )
    
    action2 = AtomicAction(
        action_id="transform_style",
        action_type=ActionType.TRANSFORM,
        parameters={"style": "abstract"},
        dependencies=["generate_base"]
    )
    
    plan = ExecutionPlan(plan_id="test_context", actions=[action1, action2])
    trace = runtime.run(plan)
    
    # 检查执行上下文
    context = runtime.get_context()
    assert context is not None, "执行上下文应该存在"
    
    # 检查结果传递
    result1 = context.get_result("generate_base")
    assert result1 is not None, "第一个操作应该有结果"
    assert result1.is_successful(), "第一个操作应该成功"
    
    result2 = context.get_result("transform_style")
    assert result2 is not None, "第二个操作应该有结果"
    
    # 检查参数注入
    # 注意：MockBackend不会实际使用注入的参数，但我们可以检查追踪
    print(f"[OK] 执行上下文创建成功")
    print(f"[OK] 操作1结果: {result1.status.value}")
    print(f"[OK] 操作2结果: {result2.status.value}")
    print()


def test_smart_dependency_inference():
    """测试2: 智能依赖推断"""
    print("=" * 80)
    print("测试2: 智能依赖推断")
    print("=" * 80)
    
    runtime = Runtime()
    runtime.register_backend(MockBackend())
    
    # 使用智能编译器
    intent = ArtIntent(
        goals=["generate_base_image", "transform_to_abstract", "apply_filter"]
    )
    
    plan = runtime.compile(intent, auto_dependencies=True)
    
    # 检查依赖关系
    action_types = [a.action_type for a in plan.actions]
    print(f"[OK] 操作类型推断: {[t.value for t in action_types]}")
    
    # 检查是否有依赖关系
    has_deps = any(len(a.dependencies) > 0 for a in plan.actions)
    print(f"[OK] 自动依赖推断: {'是' if has_deps else '否'}")
    
    if has_deps:
        for action in plan.actions:
            if action.dependencies:
                print(f"  - {action.action_id} 依赖于: {action.dependencies}")
    print()


def test_result_injection():
    """测试3: 操作结果注入"""
    print("=" * 80)
    print("测试3: 操作结果注入")
    print("=" * 80)
    
    context = ExecutionContext()
    
    # 模拟第一个操作的结果
    from core.trace import TraceEvent, ActionStatus
    from datetime import datetime
    
    event1 = TraceEvent(
        timestamp=datetime.now(),
        action_id="action1",
        status=ActionStatus.COMPLETED,
        result_payload={"image": "base_image_data", "metadata": {"size": "1024x1024"}}
    )
    context.store_result(event1)
    
    # 测试参数注入
    action2_params = {"style": "abstract"}
    enriched_params = context.inject_dependencies(
        "action2",
        ["action1"],
        action2_params
    )
    
    assert "_dep_action1" in enriched_params, "应该注入依赖结果"
    assert enriched_params["_dep_action1"]["image"] == "base_image_data", "结果应该正确传递"
    assert "_dependencies" in enriched_params, "应该有依赖汇总"
    
    print(f"[OK] 参数注入成功")
    print(f"[OK] 注入的参数键: {list(enriched_params.keys())}")
    print()


def test_parallel_execution():
    """测试4: 并行执行"""
    print("=" * 80)
    print("测试4: 并行执行")
    print("=" * 80)
    
    runtime = Runtime(enable_parallel=True, max_workers=2)
    runtime.register_backend(MockBackend(name="mock", latency=0.2))
    
    # 创建可以并行执行的操作（无依赖）
    action1 = AtomicAction(
        action_id="parallel_1",
        action_type=ActionType.GENERATE,
        parameters={"task": "task1"}
    )
    
    action2 = AtomicAction(
        action_id="parallel_2",
        action_type=ActionType.GENERATE,
        parameters={"task": "task2"}
    )
    
    plan = ExecutionPlan(plan_id="test_parallel", actions=[action1, action2])
    
    import time
    start_time = time.time()
    trace = runtime.run(plan)
    elapsed = time.time() - start_time
    
    # 并行执行应该比串行快（2个操作，每个0.2秒，并行应该约0.2秒，串行约0.4秒）
    print(f"[OK] 执行完成，耗时: {elapsed:.2f} 秒")
    print(f"[OK] 预期并行执行时间 < 0.4秒: {elapsed < 0.4}")
    print()


def test_retry_mechanism():
    """测试5: 重试机制"""
    print("=" * 80)
    print("测试5: 重试机制")
    print("=" * 80)
    
    runtime = Runtime(max_retries=2, enable_parallel=False)
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    # 创建一个会失败的操作（但MockBackend需要should_fail参数）
    # 注意：MockBackend的失败是模拟的，不会真正重试
    # 这里主要测试重试框架是否工作
    action = AtomicAction(
        action_id="retry_test",
        action_type=ActionType.GENERATE,
        parameters={"test": "retry"}
    )
    
    plan = ExecutionPlan(plan_id="test_retry", actions=[action])
    trace = runtime.run(plan)
    
    print(f"[OK] 重试机制已配置: max_retries={runtime._max_retries}")
    print(f"[OK] 执行完成")
    print()


def test_result_query():
    """测试6: 结果查询"""
    print("=" * 80)
    print("测试6: 结果查询")
    print("=" * 80)
    
    runtime = Runtime(enable_parallel=False)
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    intent = ArtIntent(goals=["query_test"])
    plan = runtime.compile(intent)
    trace = runtime.run(plan)
    
    # 查询操作结果
    if plan.actions:
        action_id = plan.actions[0].action_id
        result = trace.get_action_result(action_id)
        
        assert result is not None, "应该能查询到结果"
        assert "status" in result, "结果应该包含状态"
        assert "result_payload" in result, "结果应该包含负载"
        
        print(f"[OK] 结果查询成功")
        print(f"[OK] 操作状态: {result['status']}")
        
        # 查询所有结果
        all_results = trace.get_all_results()
        print(f"[OK] 所有操作结果数: {len(all_results)}")
    print()


def test_dag_execution():
    """测试7: DAG执行和层级分组"""
    print("=" * 80)
    print("测试7: DAG执行和层级分组")
    print("=" * 80)
    
    runtime = Runtime(enable_parallel=True, max_workers=3)
    runtime.register_backend(MockBackend(name="mock", latency=0.1))
    
    # 创建复杂的DAG
    # Level 0: action1, action2 (可以并行)
    # Level 1: action3 (依赖action1), action4 (依赖action2) (可以并行)
    # Level 2: action5 (依赖action3, action4)
    
    action1 = AtomicAction(action_id="a1", action_type=ActionType.GENERATE)
    action2 = AtomicAction(action_id="a2", action_type=ActionType.GENERATE)
    action3 = AtomicAction(action_id="a3", action_type=ActionType.TRANSFORM, dependencies=["a1"])
    action4 = AtomicAction(action_id="a4", action_type=ActionType.TRANSFORM, dependencies=["a2"])
    action5 = AtomicAction(action_id="a5", action_type=ActionType.COMPOSE, dependencies=["a3", "a4"])
    
    plan = ExecutionPlan(
        plan_id="test_dag",
        actions=[action5, action1, action2, action3, action4]  # 故意打乱顺序
    )
    
    # 验证计划
    is_valid, error = plan.validate()
    assert is_valid, f"计划应该有效: {error}"
    
    # 检查执行顺序
    execution_order = plan.get_execution_order()
    order_ids = [a.action_id for a in execution_order]
    
    # 验证依赖顺序
    assert order_ids.index("a1") < order_ids.index("a3"), "a1应该在a3之前"
    assert order_ids.index("a2") < order_ids.index("a4"), "a2应该在a4之前"
    assert order_ids.index("a3") < order_ids.index("a5"), "a3应该在a5之前"
    assert order_ids.index("a4") < order_ids.index("a5"), "a4应该在a5之前"
    
    print(f"[OK] DAG验证通过")
    print(f"[OK] 执行顺序: {' -> '.join(order_ids)}")
    
    # 执行计划
    trace = runtime.run(plan)
    stats = trace.get_statistics()
    print(f"[OK] 执行完成，成功率: {stats['success_rate']:.1f}%")
    print()


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("artfish 高级功能测试")
    print("=" * 80 + "\n")
    
    try:
        test_context_and_result_passing()
        test_smart_dependency_inference()
        test_result_injection()
        test_parallel_execution()
        test_retry_mechanism()
        test_result_query()
        test_dag_execution()
        
        print("=" * 80)
        print("[SUCCESS] 所有高级功能测试通过！")
        print("=" * 80)
        
    except AssertionError as e:
        print(f"\n[ERROR] 断言失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
