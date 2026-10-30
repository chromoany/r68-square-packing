# 复现补充材料：圆内的 68 个单位正方形

本材料支持以下上下界：

\[
\frac{39}{8}<r(68)\leq U,
\qquad U=\frac{5031404629453352}{10^{15}}=5.031404629453352.
\]

正方形允许任意实数平移与旋转，内部不得相交，边界可以接触。这些结果尚未确定全局最优值，也没有判定半径 5 时能否容纳 68 个正方形。数学论证，包括下界对连续位姿域的覆盖论证，见配套论文；程序负责复核相应的有限证书。

## 文件与算术

- `upper/` 保存一个精确的 68 块构造、其关于指定原点的精确半径、独立的标准库验算程序，以及 2026 年 10 月 30 日完整验算的结果。
- `lower/` 保存冻结的径向权重与位姿覆盖数据、加固后的证明核心源码、历史及本次完整重放结果，以及验证入口和小规模拒错控制。
- `inventory.json` 列出本补充材料内其余所有文件的字节数和 SHA-256。`lower/proof-manifest.json` 另行冻结本修订版的 8 件下界输入文件，该清单自身的 SHA-256 固定在包装程序中。

原坐标、半径、覆盖、权重、积分成本与历史重放数据均与 v1 逐字节一致。两份证明核心的数学表达式保留不变，验收断言改为显式检查。旧搜索器及临时命名入口已停用，原源码保留于 v1 版本。精确坐标与覆盖文件中的有理数字符串是验算依据。验算器从 `translation-gradient-cover-state.json` 读取 `shell_edges` 与 `shell_weights`；辅助权重 JSON/CSV 提供同一组有理权重，便于阅读。图形和显示的小数近似值用于说明，不是证明输入。

以下命令均从本补充材料目录运行，使用 Python 3。上界程序只需 Python 标准库。下界积分重放另需 `python-flint==0.8.0`，并采用 256 位精度的 Arb。证明与实现依赖 Python 整数、有理数运算和 FLINT/Arb 区间包围运算的正确性，不属于证明助手中的形式化认证。

## 精确上界验算

```text
python upper/verify-upper.py upper/best-68-exact-state.json --radius upper/best-68-exact-radius.json
```

完整成功时输出 `PASS_EXACT_68_SQUARE_UPPER_BOUND`。程序检查 68 个精确单位方向向量、全部 272 个顶点，以及全部 2,278 对正方形的精确有理分离轴不等式，允许相切。随后独立求出最大顶点距离的平方，并检查半径多项式与隔离区间。

本版编制期间已重新执行完整目标验算。`upper/verification-result.json` 记录全部 2,278 对及 272 个顶点通过，按首个成功分离轴分类的数量为 1,847、411、10、10。实测用时记录于结果文件，不作为运行时间保证。

所附构造关于指定原点的半径为

\[
\widehat R=\sqrt{p/q},\qquad q\widehat R^2-p=0,\quad\widehat R>0.
\]

互素正整数 `p`、`q` 分别保存在 `best-68-exact-radius.json` 的 `squared_radius_numerator` 与 `squared_radius_denominator` 字段，位数分别为 1,451 和 1,450。程序验证

\[
5.031404629453350730787899409097
<\widehat R<
5.031404629453350730787899409098<U.
\]

这是该构造关于指定原点的精确半径，不宣称是允许重新选择圆心后的最小外接圆半径，更不宣称等于全局最优值 `r(68)`。唯一最远顶点在数据中的标识为 `(25, +1, +1)`。

还可运行小型几何控制：

```text
python upper/verify-upper.py --self-test
```

这些控制与完整目标验算分别记录。

## 下界重放

在合适的 Python 环境中安装固定依赖：

```text
python -m pip install -r lower/requirements.txt
```

随后完整重放冻结证书：

```text
python lower/verify-lower.py
```

默认沿用历史成功重放的配置：16 个工作进程、300 秒重放预算。可显式设置，例如：

```text
python lower/verify-lower.py --workers 16 --budget 300 --scratch-parent .
```

`--scratch-parent` 须指向已存在且可写的目录。每次运行会在其中创建独立临时子目录，并在结束时清理该子目录；包中的原件不被修改。标准输出为结果 JSON，可自行重定向到新结果文件。

固定证书验算器接受 1–32 个工作进程和 1–600 秒的重放预算。这是保留的单次重放接口范围，不代表平台上限或科学搜索的终止规则。预算耗尽只能得到未完成结果，不能形成下界证书。不要使用 Python 的 `-O` 或 `-OO` 参数：包装程序与证明核心均明确拒绝优化模式；数学验收也已改为显式检查，并通过独立的小型控制验证其在优化编译下仍然有效。

重放前，包装程序先核对全部冻结源码与数据的身份、问题的有理参数、权重非负性、精确成本比较和无前缀重叠的二叉覆盖拓扑。覆盖的 11,837 个叶子分为 1,583 个公共内矩形叶、8,923 个梯度叶和 1,331 个排除叶，没有待决叶或严格缺口见证。这些前置检查不计算积分。

真正重放时，包装程序在新建临时目录内运行冻结验算器，不将历史结果复制为临时目录的输出。它检查进程退出码、新生成结果、准确状态与叶数、梯度叶全覆盖、输入身份，以及证明文件是否保持不变。只有完整的新重放才能输出 `PASS_GLOBAL_REAL_R68_LOWER_GRADIENT`，并带有 `fresh_full_replay: true`。证明核心同时重新计算向外包围的积分、导数界及所需的 π 上包围。仅有退出码 0、历史 `PASS` 或文件传输成功均不足以通过。

### 本次完整回放与历史证据

`lower/fresh-full-replay.json` 记录了本版**重新执行的完整回放**：16 个工作进程、256 位 Arb 算术，全部 11,837 个叶子通过，积分回放约 20.245 秒。Slurm 作业 **126395001** 为 `COMPLETED`，退出码 `0:0`。环境为 CPython 3.12.6、python-flint 0.8.0、FLINT 3.3.1、Linux x86_64；源码、结果和清单散列见 provenance 文件。这是同一验证算法的新鲜复跑，不是新的独立实现，也没有产生新界。

`lower/translation-gradient-independent-replay.json` 仍为未改动的历史原件（约 19.596 秒），不会被复制成新回放的输出。`source-equivalence.json` 记录 v1 到 v2 的数学表达式比较：仅在比较时将断言规范化为显式检查，实际源码变更可在 Git 历史中查看。

`wrapper-control-result.json` 记录 17 个拒错控制；`entrypoint-control-result.json` 记录 20 个新增控制，覆盖真实 `-O`/`-OO` 调用、旧入口停用、隔离的非法叶子，以及合法排除与超时情形。隔离叶子测试使用替身，不代替完整积分回放。`kernel-selftest.log` 记录同一计算作业中执行的面积核自检。

以下命令只需 Python 标准库：

```text
python lower/verify-lower.py --check-inputs
python lower/test-wrapper.py
python lower/test-entrypoints.py
```

请在可写的当前目录运行 `test-wrapper.py`。前置检查状态为 `INPUTS_CHECKED_NO_INTEGRAL_REPLAY`，不会重算 π 或任何叶积分；控制测试状态为 `SMALL_WRAPPER_CONTROLS_OK`。两者都不表示刚刚完成了全体下界积分重放。

这些读者入口不执行优化、构造生成、远端登录或作业提交。
