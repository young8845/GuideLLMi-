import subprocess
import os
import json

# 提前建好保存结果的文件夹
os.makedirs("outputs", exist_ok=True)

# 补充：假设你已经获取到了模型名，比如你之前的 DeepSeek-V4-Flash
MODEL = "DeepSeek-V4-Flash" 
VLLM_URL = "http://localhost:30004" # 注意：我帮你改成了你真实的端口

# 1. 拼装 GuideLLM 的执行命令
cmd = [
    "guidellm", "run", #运行guidellm
    "--backend", f"kind=openai_http,target={VLLM_URL}",#传入地点
    "--data", "kind=synthetic_text,prompt_tokens=32,output_tokens=16", #制造输入32，输出16的测试数据
    "--profile", "kind=synchronous", #吞吐并发模式
    "--constraint", "kind=max_requests,count=10",#限制最大吞吐量
    "--tokenizer", "kind=huggingface_auto,model=/data/models/DeepSeek-V4-Flash-FlexSMQ-AWQ-W8A8", # 丈量长度的尺子
    "--output", "kind=json,path=./outputs/benchmarks.json",#输出json格式，保存到path这个路径
]

# 2. 打印出我们要执行的命令
print(f"Running: {' '.join(cmd)}\n")

# 3. 在 Python 里调用终端执行这个命令
result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
#cmd保存执行的命令/拦截屏幕输出/转换为字符串文档/超时限制

# 4. 处理执行结果
if result.returncode == 0:
    print("Benchmark complete!")
    # 截取最后 2000 个字符打印出来，防止终端被刷爆
    tail = result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
    print(tail)
else:
    print(f"GuideLLM exited with code {result.returncode}")
    print(f"STDOUT:\n{result.stdout[-1000:]}")
    print(f"STDERR:\n{result.stderr[-1000:]}")

# 1. 读取刚才 GuideLLM 生成的 JSON 报告
with open("outputs/benchmarks.json") as f:
    report = json.load(f)

# 2. 剥洋葱，找到核心数据
bench = report["benchmarks"][0]
metrics = bench["metrics"]
# 统计成功完成的请求数量
n_requests = metrics["request_totals"]["successful"]

print(f"Profile: {bench['type_']}  |  Requests: {n_requests}\n")

# 3. 建立中英文对照字典 (把你关心的指标名映射到 JSON 里的键名)
display_metrics = {
    "TTFT (ms)":        "time_to_first_token_ms",
    "ITL (ms)":         "inter_token_latency_ms",
    "E2E Latency (s)":  "request_latency",
    "Output tokens":    "output_token_count",
}

# 4. 打印表头
print(f"{'Metric':<20} {'Mean':>8} {'p50':>8} {'p95':>8} {'p99':>8}")
print("-" * 55)

# 5. 遍历刚才的字典，从 JSON 里抠出 均值、P50、P95、P99 数据并打印
for label, key in display_metrics.items():
    dist = metrics[key]["successful"]
    p = dist["percentiles"]
    
    print(f"{label:<20} {dist['mean']:>8.2f} {p['p50']:>8.2f} "
          f"{p['p95']:>8.2f} {p['p99']:>8.2f}")

# 6. 最后单独把吞吐量 (Throughput) 和 请求率 (QPS) 拎出来打印
throughput = metrics["output_tokens_per_second"]["successful"]
req_rate = metrics["requests_per_second"]["successful"]
print(f"\nThroughput: {req_rate['mean']:.2f} req/s  |  "
      f"{throughput['mean']:.1f} output tokens/s")
