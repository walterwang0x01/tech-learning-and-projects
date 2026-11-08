# 🇨🇳 国内科技周报 — 2026-W45

> Author: Walter Wang
> 2026-11-02 至 2026-11-08：国产 Agent 走出聊天框，身份、终端、算力与物理执行同时补课。

## 📌 头条

### Top 1｜国产 Agent 从模型走向系统

美团发布 LongCat-2.5，把长程、多模态和 agent 编程写进 1.6 万亿参数 MoE 模型的训练目标。腾讯混元 Hy4 正式版首次补上视觉理解与 Computer Use，托管 API 先行，开放权重仍待落地。DeepSeek 的 dsh-superagent 则把长期运行拆成常驻路由与隔离 worker session，重点落在运行时而非单轮回答。三条线放在一起看，国内竞争已从“模型会不会答”推进到“能否持续做、操作软件并在系统里稳定运行”。

→ [LongCat-2.5](https://www.ithome.com/1/020/873.htm) / [腾讯 Hy4](https://www.tencent.com/tencent-launches-hy4-joining-the-ranks-of-the-worlds-leading-open-source-ai-models) / [dsh-superagent](https://github.com/deepseek-ai/dsh-superagent-prototype)

---

### Top 2｜Agent 身份与终端监管补位

香港大学发布 KYA 研究报告，把智能体的身份、授权、信用和责任放到真实经济活动里讨论。乌镇峰会同期出现智能体身份注册与解析平台，试图让用户可撤权、服务方可识别代理关系、不同平台可互相发现。工信部随后要求智能体终端做适配验证，并在产品设置页公示已适配的终端与操作系统。能力跑得越快，行业越需要回答“谁授权、能做什么、在哪些设备上安全运行”这三个问题。

→ [KYA 报告](https://www.leiphone.com/category/industrynews/KkjVOHcQ55GyhDLv.html) / [身份注册平台](https://www.leiphone.com/category/industrynews/KStlwPyruE6hJ107.html) / [终端适配通知](https://www.ithome.com/1/023/059.htm)

---

## ⚡ 快讯

- **Top 3｜物理 AI 进入真实作业场**：百度用 Apollo World 做无人驾驶仿真验证，蚂蚁灵波开源机器人通用大脑，京东物流再用“超脑 3.0”调度 11 款机器人；具身智能开始比拼真实场景数据、统一调度和常态运行 → [Apollo World](https://www.oschina.net/news/503374) / [蚂蚁灵波](https://www.leiphone.com/category/industrynews/ADcxxdwtaojQvzhp.html) / [京东物流](https://www.infoq.cn/article/1YeowHagkg1Or6wwy23P)
- **Top 4｜个人 Agent 拼事务和入口**：蚂蚁称灵光 2.0 一周托管 116 万项事务，华为把小艺 Work 做成独立应用，微信小微继续灰度进入阅读、图片和扫码入口；消费端竞争点从聊天框转向能接多少日常上下文 → [灵光 2.0](https://www.leiphone.com/category/industrynews/rJ5oXEPsUlwSPneA.html) / [华为小艺](https://www.ithome.com/1/023/086.htm) / [微信小微](https://www.ithome.com/1/023/806.htm)
- **Top 5｜国产算力开始换打法**：美团模型被报道全程使用国产算力训练，墨芯连续两轮获得近 10 亿元融资押注稀疏推理，游族披露 42.25 亿元 GPU 采购合同；模型、专用芯片和算力采购正从不同方向争抢推理成本优势 → [LongCat 算力报道](https://www.leiphone.com/category/industrynews/mUPVr3RF0MHNmn3t.html) / [墨芯融资](https://www.qbitai.com/2026/11/508155.html) / [游族 GPU 合同](https://www.ithome.com/1/022/526.htm)
- **本周加看｜AI 开始直接接受成交检验**：千问办公把 Token 当会员商品卖进直播间，阿里 Wan3.0 又进入双 11 品牌短剧并接到商品与直播链路；国产 AI 产品不再只报 benchmark，也开始用购买和转化证明价值，不过经营数字仍需区分平台口径与独立验证 → [千问办公](https://www.leiphone.com/category/industrynews/h454rlPtg41JIuFd.html) / [Wan3.0 品牌短剧](https://www.qbitai.com/2026/11/508118.html)
- **本周加看｜国内科研向机器人与生命科学扩展**：CoRL 2026 公开数据分析显示中国高校参与比例继续上升，中国科大团队的 RNA 基础模型 structRFM 登上《自然》并开源；两项信息的统计口径和性能结论都应回到论文与代码核验 → [CoRL 统计](https://www.leiphone.com/category/academic/3fdO5oKaYZHXYOxI.html) / [structRFM](https://www.ithome.com/1/022/511.htm)

## 🤖 大模型动态

| 公司 | 本周动态 | 链接 |
|------|------|------|
| 美团龙猫 | LongCat-2.5 主攻长程、多模态与 agent 编程 | [→](https://www.ithome.com/1/020/873.htm) |
| 腾讯混元 | Hy4 正式版加入视觉与 Computer Use，API 已上线、权重待放 | [→](https://www.tencent.com/tencent-launches-hy4-joining-the-ranks-of-the-worlds-leading-open-source-ai-models) |
| DeepSeek | 开源 dsh-superagent 原型，探索常驻路由与隔离 worker session | [→](https://github.com/deepseek-ai/dsh-superagent-prototype) |
| 蚂蚁百灵 | 开源 Ling-3.1-flash-1019，面向 Personal Agent 长程任务 | [→](https://m.ebrun.com/716640.html) |

## 📄 论文精选

| 论文 / 报告 | 本周看点 | 链接 |
|------|------|------|
| structRFM | 中国科大团队的 RNA 序列基础模型，论文登上《自然》并开放代码 | [→](https://www.ithome.com/1/022/511.htm) |
| CoRL 2026 录用集 | 687 篇录用论文构成机器人学习研究样本，机构统计仍受元数据缺失影响 | [→](https://github.com/Studeas/corl-2026-paper-list) |
| KYA 智能体信用体系 | 用 109 份从业者问卷和企业案例讨论智能体身份、授权、信用与责任 | [→](https://www.leiphone.com/category/industrynews/KkjVOHcQ55GyhDLv.html) |

## 🗓 下周预测

- 百度世界 2026 将于 11 月 12 日开幕，关注其“智能组织”主题是否给出可落地的产品与组织改造数据。→ [大会预告](https://www.leiphone.com/category/industrynews/49uolfG855V4Zc9M.html)
- 腾讯承诺随后开放 Hy4 权重与 system card，下周要核对是否如期落地，以及开放范围是否足够支持本地评测。→ [腾讯公告](https://www.tencent.com/tencent-launches-hy4-joining-the-ranks-of-the-worlds-leading-open-source-ai-models)
- CoRL 2026 于 11 月 9 至 12 日举行，中国高校高参与度会转化成哪些机器人学习方向的一手成果，值得按论文而非排名继续看。→ [会议官网](https://www.corl.org/)
- 智能体终端适配要求发布后，手机、车机和 PC 厂商可能开始公开适配清单与权限处理细节。→ [通知转述](https://www.ithome.com/1/023/059.htm)

> 注：周报按本周日报回顾，因此会复用当周一手链接；外部来源内容已按许可限制要求改写。

## 📈 趋势

- 🆕 长程、多模态与 Computer Use 同时进入国产旗舰模型
- 🆕 智能体身份注册、信用研究与终端适配开始形成治理组合
- 🔺 物理 AI 从展示单机能力转向真实作业、统一调度和规模数据
- 🔺 个人 Agent 从回答问题转向持续管理事务和嵌入超级 App 上下文
- 🔺 国产算力路线分化：大规模训练、通用 GPU 采购和稀疏专用芯片并行
- 🔺 AI 产品开始用成交、执行量和真实部署衡量商业价值
- 🔻 只靠聊天体验或单项 benchmark 证明产品价值的说服力继续下降
