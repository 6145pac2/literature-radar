# 文献雷达周报 2026-08-31

- 日期范围：2026-08-24 至 2026-08-31（左闭右开）
- 论文总数：13
- 主题关键词：hydrothermal liquefaction、biocrude、waste valorization、microalgae、biochar、biorefinery
- 排除关键词：medical、building structure
- 相关性评分：标题每命中1个主题词 +10分，摘要每命中1个主题词 +3分；本期共6个主题词，理论总分78分
- 检索时间：2026-08-31T15:31:05+08:00

---

## 水热转化

1. 预测木质纤维素生物质水热液化的生物油产量：通过联合引导蒙特卡罗的机器学习方法和不确定性传播  
   (Predicting bio-oil yield from hydrothermal liquefaction of lignocellulosic biomass: machine learning approach and uncertainty propagation via joint bootstrap Monte Carlo)  
   👤 Oraléou Sangué Djandja, Yulin Hu, Yimin Zeng, Quan He  
   📖 **Fuel** | IF: 7.5 | 中科院: 工程技术 2区 Top（2025升级版）  
   📚 小类分区: 能源与燃料 2区；工程：化工 2区  
   🔗 DOI: 10.1016/j.fuel.2026.141091  
   🎯 相关性得分: 13/78 (标题: hydrothermal liquefaction; 摘要: hydrothermal liquefaction)  
   🤖 AI摘要：
   **研究目的**：本研究旨在利用机器学习方法预测木质纤维素生物质在水热液化（HTL）过程中生物油产率及质量指标，并量化预测不确定性，以支持后续工艺优化。   
   **研究方法**：基于文献构建数据库，开发多层感知机、支持向量回归、决策树、随机森林（RF）和极端梯度提升（XGB）模型，预测生物油产率、元素比、碳保留率、脱氧效率和高位热值。预测因子选择结合过程知识与相关性分析，超参数通过粒子群优化。采用联合自助蒙特卡洛和残差共形分析量化不确定性，并用分段回归和局部偏依赖分析解释特征影响。   
   **关键结果**：XGB和RF性能最佳，但多数次级输出模型泛化能力有限，故详细分析仅聚焦生物油产率，其中XGB模型预测最可靠。有效水填充比（Vw/Vr）显著提升产率预测，SHAP分析将其列为最重要预测因子，而Spearman分析显示反应时间为最强单调因子（ρ≈−0.43），Vw/Vr次之（ρ≈+0.34）。分段回归表明反应时间影响主要集中于约80分钟以下，而Vw/Vr在模型断点约13.9以下产生更强非线性影响。   
   **主要结论**：该框架提供了可解释且考虑不确定性的木质纤维素HTL建模方法，优先识别关键工艺条件。Vw/Vr是产率预测的核心变量，反应时间影响具有阈值效应。联合自助蒙特卡洛方法建立了基于区间宽度和应用域支持的模型可信度包络，为工艺优化提供依据。原摘要未说明具体生物油产率数值及实验条件细节。  

## 生物炭

2. 面向废物衍生前体的循环生物炭系统：对吸附和异质类芬顿氧化性能的多分析和多变量见解  
   (Toward circular biochar systems from waste-derived precursors: multi-analytical and multivariate insights into adsorption and heterogeneous Fenton-like oxidation performance)  
   👤 Antonio Faggiano, Andrea Bergomi, Marco Vitelli, Valeria Comite, Gianluca Carabelli, Oriana Motta, Maria Ricciardi, Antonio Proto, Antonino Fiorentino, Paola Fermo  
   📖 **Journal of Cleaner Production** | IF: 11.1 | 中科院: 工程技术 1区  
   🔗 DOI: 10.1016/j.jclepro.2026.149314  
   🎯 相关性得分: 13/78 (标题: biochar; 摘要: biochar)  
   🤖 AI摘要：
   **研究目的**：本研究旨在阐明废弃生物质前驱体类型、热解温度及铁功能化如何共同调控生物炭基体系的吸附与异相Fenton-like氧化性能，从而推动废弃资源向高价值功能材料转化，支撑循环经济战略和可持续水处理技术发展。   
   **研究方法**：以废咖啡渣、橄榄果渣、橄榄果渣核和污水污泥四种废弃前驱体为原料，在450、550和650 °C三种热解温度下制备12种原始生物炭，经铁功能化后共获得24种材料。采用多分析表征手段结合I-最优响应面法（RSM）和主成分分析（PCA），RSM用于优化材料与工艺变量，PCA用于解析结构-性质-性能关系并识别控制吸附和氧化过程的主要描述符。吸附数据用Freundlich和Langmuir模型拟合，氧化实验以苯酚为目标污染物。   
   **关键结果**：平衡吸附数据更符合Freundlich模型（R² ≥ 0.97），表明表面异质性为主导因素；Langmuir-derived Qmax仅作比较性容量指标。木质纤维素生物炭受比表面积和芳香性控制，而污泥基生物炭因富含矿物质和含氧官能团表现出更强亲和力。铁功能化显著提升性能，Fe-SSBC450（铁功能化污泥生物炭，450 °C）表现最佳，Langmuir-derived吸附容量Qmax = 6.57 mg g⁻¹，氧化效率约76%苯酚去除。氧化过程遵循准二级动力学，由•OH自由基驱动。   
   **主要结论**：废弃前驱体可有效转化为高价值环境修复材料，铁功能化是提升吸附和氧化性能的关键策略。污泥基生物炭因独特矿物组成和官能团而具有应用潜力。本研究为废弃资源循环利用和资源节约型水净化提供了系统化设计框架，但原摘要未说明材料在实际水体中的长期稳定性、可重复使用性及处理真实废水的效果等局限性。  

3. 蒙脱石-生物炭复合材料增强土霉素衰减并调节羊粪堆肥过程中的抗生素耐药性反应  
   (Montmorillonite-biochar composite enhances oxytetracycline attenuation and modulates antibiotic resistance responses during sheep manure composting)  
   👤 Xu Bai, Kai Fu, Xiang Hu, Lu Liu, Heli Wang, Yajun Yang  
   📖 **Biochemical Engineering Journal** | IF: 3.8 | 中科院: 生物学 3区（2025升级版）  
   📚 小类分区: 生物工程与应用微生物 3区；工程：化工 3区；部分旧版大类为工程技术 3区  
   🔗 DOI: 10.1016/j.bej.2026.110378  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

4. 宏基因组学见解抑制中生态规模人工湿地中的抗生素抗性细菌：菖蒲-生物炭减轻选择压力并破坏遗传共现网络  
   (Metagenomic insights into suppressing antibiotic-resistant bacteria in mesocosm-scale constructed wetlands: calamus-biochar alleviates selective pressure and disrupts genetic co-occurrence network)  
   👤 Wei Wu, Yu Wang, Tian-Bao Yang, Xian-Kai Zhang, Bing-Dang Wu, Jinlong Zhuang, Qian-Yi Cao, Shuo Song, Wei Li, Tianyin Huang, XU Xiao-Yi  
   📖 **Bioresource Technology** | IF: 11.4 | 中科院: 工程技术 1区 Top  
   🔗 DOI: 10.1016/j.biortech.2026.135710  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

5. 强化生物膜介导的电子转移和全氟辛酸去除：铁生物炭基人工湿地中被忽视的大型植物的作用  
   (Reinforced biofilm-mediated electron transfer and perfluorooctanoic acid removal: Neglected macrophyte roles in iron-biochar-based constructed wetlands)  
   👤 Xiuwen Qian, Juan Huang, Ying Shi, Yuanyan Zhang, Zhishui Liang, Shiyu Shan, Jin Xu  
   📖 **Bioresource Technology** | IF: 11.4 | 中科院: 工程技术 1区 Top  
   🔗 DOI: 10.1016/j.biortech.2026.135713  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

6. 载铁生物炭对废弃活性污泥生产中链脂肪酸的影响  
   (Effect of iron-loaded biochar on medium-chain fatty acid production from waste activated sludge)  
   👤 Tianru Lou, Mingyang Liu, Yanan Yin, Jianlong Wang  
   📖 **Bioresource Technology** | IF: 11.4 | 中科院: 工程技术 1区 Top  
   🔗 DOI: 10.1016/j.biortech.2026.135715  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

7. 氧化还原活性 MnOx-生物炭合成用于去除双酚 A，同时通过 Mn 催化 CO2 介导的生物质热化学处理产生富含 CO 的合成气  
   (Redox-Active MnOx-Biochar synthesis for bisphenol a removal with simultaneous CO-Rich syngas generation via Mn-Catalyzed CO2-mediated biomass thermochemical treatment)  
   👤 Youn-Jun Lee, Chohee Yang, Deok Hyun Moon, Eilhann E. Kwon  
   📖 **Bioresource Technology** | IF: 11.4 | 中科院: 工程技术 1区 Top  
   🔗 DOI: 10.1016/j.biortech.2026.135717  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

8. 生物炭作为添加剂改善大豆秸秆的生物甲烷化：现场实施和成本效益分析有助于循环生物经济  
   (Biochar as an additive to improve the biomethanation of soybean straw: on-field implementation and cost benefit analysis aiding circular bioeconomy)  
   👤 Sugato Panda, Sayak Chakravorty, Mayur Shirish Jain  
   📖 **Bioresource Technology** | IF: 11.4 | 中科院: 工程技术 1区 Top  
   🔗 DOI: 10.1016/j.biortech.2026.135719  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

9. 孢子衍生的 Fe2P/生物炭复合材料可有效降解四环素：反应机制研究、抗菌活性消除和抗生素耐药性风险缓解  
   (A spore-derived Fe2P/biochar composite for efficient tetracycline degradation: Reaction mechanism investigation, antibacterial activity elimination and antibiotic resistance risk mitigation)  
   👤 Linli Dai, Xuqian Wang, Xiuyuan Ran, Yongkui Zhang, Yabo Wang  
   📖 **Chemical Engineering Journal** | IF: 15.1 | 中科院: 工程技术 1区 Top  
   🔗 DOI: 10.1016/j.cej.2026.181071  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

10. 在生物质热解开始之前对其进行编程：功能性微孔生物炭的芬顿驱动键断裂  
   (Programming biomass pyrolysis before it starts: Fenton-driven bond cleavage for functional microporous biochar)  
   👤 Weilong Wu, Lukuan Xu, Chao Li, Yi Wang, Xun Hu  
   📖 **Fuel** | IF: 7.5 | 中科院: 工程技术 2区 Top（2025升级版）  
   📚 小类分区: 能源与燃料 2区；工程：化工 2区  
   🔗 DOI: 10.1016/j.fuel.2026.141101  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

11. 绿色原位构建澳洲坚果废弃物生物炭/UiO-66-NH2 混合物，用于高效去除废水中的刚果红和甲基橙  
   (Green in situ construction of a macadamia waste-derived biochar/UiO-66-NH2 hybrid for high-efficiency removal of congo red and methyl orange from wastewater)  
   👤 Van-Doan Nguyen, Thanh Xuan Tran, Thi Phuong Nguyen, Anh-Tuan Vu  
   📖 **Journal of Cleaner Production** | IF: 11.1 | 中科院: 工程技术 1区  
   🔗 DOI: 10.1016/j.jclepro.2026.149292  
   🎯 相关性得分: 10/78 (标题: biochar; 摘要: —)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

12. 生物质碳储存应对野火和气候危机的近期地理空间机会  
   (Near-term, geospatial opportunity for biomass carbon storage to address the wildfire and climate crises)  
   👤 Leah K. Clayton, Alexander S. Wyckoff, Sinéad M. Crotty  
   📖 **Science Advances** | IF: 13.9（2025 JIF） | 中科院: 综合性期刊 1区 Top（2025升级版）  
   📚 小类分区: 综合性期刊（MULTIDISCIPLINARY SCIENCES）1区  
   🔗 DOI: 10.1126/sciadv.aee6185  
   🎯 相关性得分: 3/78 (标题: —; 摘要: biochar)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）

13. 微生物诱导方解石沉淀（MICP）：机制、工程应用和现场规模部署途径——全面综述  
   (Microbially induced calcite precipitation (MICP): mechanisms, engineering applications, and pathway to field-scale deployment — a comprehensive review)  
   👤 Tao He, Jiaxing Chen, Xiyan Lou  
   📖 **Frontiers in Microbiology** | IF: 5.8（2025 JIF） | 中科院: 生物学 2区（2025升级版）  
   📚 小类分区: 微生物学 3区；Top状态未提供  
   🔗 DOI: 10.3389/fmicb.2026.1928040  
   🎯 相关性得分: 3/78 (标题: —; 摘要: biochar)  
   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）
