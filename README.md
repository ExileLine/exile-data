# exile-data

BI系统+AI智能问数

### 项目环境配置

- 安装`python3.12`与`uv`
  ```shell 
  pip install uv
  ```

### 配置文件与使用

- 配置文件描述：[.env.example](.env.example)
- 本地开发环境配置文件：[.env.development](.env.development)
- 测试环境配置文件：[.env.test](.env.test)
- 生产环境配置文件：[.env.production](.env.production)

### 数据库初始化与迁移

- ORM 统一基于 SQLAlchemy 2.0
- 迁移工具统一使用 Alembic，模型注册入口在 `app/models/__init__.py`
- 生产环境建议先生成迁移 SQL 并经过审核后再执行

```shell
# 0) 查看当前迁移版本
uv run alembic current

# 1) 生成迁移脚本（根据当前模型与数据库差异）
uv run alembic revision --autogenerate -m "feat: update table schema"

# 2) 执行到最新版本
uv run alembic upgrade head

# 3) 回滚一个版本（可选）
uv run alembic downgrade -1

# 4) 生成离线 SQL（生产审核用）
uv run alembic upgrade head --sql
```

### 启动

```shell
# 本地启动
python local_run.py

# 或
uv run local_run.py 

# 或
uv run uvicorn main:app --host 0.0.0.0 --port 5001
```
