import os
print(os.environ.get('DEEPSEEK_API_KEY'))
# 检查环境变量是否设置
if not os.environ.get('DEEPSEEK_API_KEY'):
    print("DEEPSEEK_API_KEY 环境变量未设置")
else:
    print("DEEPSEEK_API_KEY 环境变量已设置")
    # 打印环境变量值（为了安全起见，不建议在生产环境中打印）
    print(f"DEEPSEEK_API_KEY 值为: {os.environ.get('DEEPSEEK_API_KEY')}")
    # sk-6420bba0892f4be7ac066d109d8aa03b