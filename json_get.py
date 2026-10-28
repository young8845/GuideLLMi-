import json

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
