document.addEventListener("DOMContentLoaded", (event) => {
    // 注册 ScrollTrigger 插件，确保后续可以使用滚动触发动画
    gsap.registerPlugin(ScrollTrigger);

    // 创建 Lenis 实例，实现平滑滚动，并将滚动事件与 ScrollTrigger 联动
    const lenis = new Lenis();
    lenis.on("scroll", ScrollTrigger.update);

    // 用 GSAP 的 ticker 驱动 Lenis 的动画帧，保证滚动和动画同步
    gsap.ticker.add((time) => { lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0); // 关闭 GSAP 本身的延迟平滑，提升动画流畅度

    // 用于存放希望在页面文本中特别标记或高亮的关键词
    const keywords = [
        "vibrant",
        "living",
        "clarity",
        "expression",
        "shape",
        "intuitive",
        "storytelling",
        "interactive",
        "vision",
    ];

    // 处理每个 anime-text 段落
    document.querySelectorAll(".anime-text p").forEach((p) => {
        // 将段落按空格分割成多个单词
        const words = p.textContent.split(/\s+/);

        // 清空段落内容
        p.innerHTML = "";

        // 遍历每个单词，将其包裹在自定义 HTML 结构中
        // 结构示例：
        // <div class="word">
        //   <span>word</span>
        // </div>
        words.forEach((word) => {
            // 跳过空白单词
            if (!word.trim()) return;

            // 创建单词外层容器
            const wordContainer = document.createElement("div");
            wordContainer.className = "word"

            // 创建单词文本节点
            const wordText = document.createElement("span");
            wordText.textContent = word;

            // 如果是关键词，则添加高亮相关的类名，方便 CSS 特效
            const normalizedWord = word.toLowerCase().replace(/[.,!?;:"]/g, "");
            if (keywords.includes(normalizedWord)) {
                wordContainer.classList.add("keyword-wrapper");
                wordText.classList.add("keyword", normalizedWord);
            }

            // 组装结构并插入段落
            wordContainer.appendChild(wordText);
            p.appendChild(wordContainer);
        });
    });

    // 辅助函数：数值限制在指定范围内
    const clamp = (num, min, max) => Math.min(Math.max(num, min), max);

    // 根据滚动进度计算每个单词的样式
    const calcOpacityByProgress = (progress, index, totalWords) => {

        // 动画分界点（前后阶段的分割线）
        const animationSplit = 0.7;

        // 前半段动画：渐变出现
        if (progress <= animationSplit) {
            // 单词动画重叠数量，决定多个单词动画的交叠范围
            const overlapWords = 15;

            // 当前单词动画的起止区间（归一化到 0~1）
            const start =  index                 / (totalWords - 1 + overlapWords);
            const end   = (index + overlapWords) / (totalWords - 1 + overlapWords);

            // 计算当前单词在动画区间内的进度（0~1）
            const temp = progress / animationSplit;
            const wordProgress = clamp((progress / animationSplit - start) / (end - start), 0.0, 1.0);

            // 计算透明度变化的加速因子，使动画更有层次感
            const factor = clamp(10 * (wordProgress - 0.9), 0.0, 1.0);

            return { 
                // 文字透明度，后半段加速出现
                textOpacity: Math.pow(factor, 0.5),

                // 背景透明度，随动画进度先出现后逐渐消失
                backgroundOpacity: (1 - factor) * wordProgress,
            }
        }
        // 后半段动画：渐变消失
        else {
            // 单词动画重叠数量，决定多个单词动画的交叠范围
            const overlapWords = 5;

            // 当前单词动画的起止区间（归一化到 0~1）
            const start =  index                 / (totalWords - 1 + overlapWords);
            const end   = (index + overlapWords) / (totalWords - 1 + overlapWords);

            // 计算当前单词在动画区间内的进度（0~1）
            const temp = (progress - animationSplit) / (1 - animationSplit);
            const wordProgress = clamp((temp - start) / (end - start), 0.0, 1.0);

            return { 
                // 文字透明度：逐渐消失
                textOpacity: (1 - wordProgress),
                
                // 背景透明度：逐渐出现
                backgroundOpacity: wordProgress,
            }
        }
    };

    // 为每个 anime-text-container 容器创建滚动触发器，实现整块内容的固定（pin）效果
    document.querySelectorAll(".anime-text-container").forEach((container) => {
        ScrollTrigger.create({
            trigger: container,                 // 触发元素
            start: "top top",                   // 从容器顶部与视口顶部对齐时开始
            end: `+=${window.innerHeight * 4}`, // 固定持续的滚动距离（4屏高度）
            pin: container,                     // 滚动时固定该元素
            pinSpacing: true,                   // 固定时保留原本空间
            onUpdate: (self) => {
                // 获取当前容器内所有单词元素
                const wordContainers = Array.from(container.querySelectorAll(".anime-text .word"));
                const totalWords = wordContainers.length;

                // 根据滚动进度动态设置每个单词及其背景的透明度和颜色
                const progress = self.progress;
                wordContainers.forEach((wordContainer, index) => {
                    const wordText = wordContainer.querySelector("span");

                    // 通过自定义函数计算当前单词的透明度和背景色
                    const { textOpacity, backgroundOpacity } = calcOpacityByProgress(progress, index, totalWords);
                    wordContainer.style.backgroundColor = `rgba(60, 60, 60, ${backgroundOpacity})`;
                    wordText.style.opacity = textOpacity
                });
            },
        })
    });

});