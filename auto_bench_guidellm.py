import subprocess
import os

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
